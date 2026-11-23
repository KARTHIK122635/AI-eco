"""
Scheduler and Recovery Orchestrator for Daily Rolling AI Ecosystem Pipeline
==========================================================================
Manages scheduled execution, interruption detection, crash recovery,
and execution checkpointing for daily incremental pipeline updates.

Usage:
    python -m core.scheduler --run-once
    python -m core.scheduler --run-daemon --schedule "06:00"
    python -m core.scheduler --check-recovery
    python -m core.scheduler --resume
"""

import os
import sys
import time
import json
import uuid
import signal
import asyncio
import logging
import argparse
import traceback
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.env_loader import load_project_env
from core.working_database import WorkingDatabaseManager
from core.daily_pipeline import DailyRollingPipeline

load_project_env()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [Scheduler] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Scheduler")


class RollingPipelineScheduler:
    """Manages scheduled daily pipeline runs, interruptions, and recovery."""

    def __init__(
        self,
        working_db_path: str = "data/working/rolling_ai_ecosystem.db",
        canonical_db_path: str = "data/normalized/ai_ecosystem.db",
        reports_dir: str = "reports",
        exports_dir: str = "data/working",
        daily_schedule_utc: str = "06:00"
    ):
        self.working_db_path = os.path.abspath(working_db_path)
        self.canonical_db_path = os.path.abspath(canonical_db_path)
        self.reports_dir = os.path.abspath(reports_dir)
        self.exports_dir = os.path.abspath(exports_dir)
        self.daily_schedule_utc = daily_schedule_utc
        self._shutdown_requested = False

        self.db_manager = WorkingDatabaseManager(
            working_db_path=self.working_db_path,
            canonical_db_path=self.canonical_db_path
        )
        self.pipeline = DailyRollingPipeline(
            working_db_path=self.working_db_path,
            canonical_db_path=self.canonical_db_path,
            reports_dir=self.reports_dir,
            exports_dir=self.exports_dir
        )

    def check_for_interrupted_runs(self) -> List[Dict[str, Any]]:
        """
        Inspects collection_logs for runs with status 'IN_PROGRESS' that may have crashed
        or been abruptly terminated.
        """
        if not os.path.exists(self.working_db_path):
            return []

        conn = self.db_manager.get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT run_id, scheduled_time, start_time, execution_type,
                   rolling_window_start, rolling_window_end, new_startups,
                   new_products, new_papers, new_news, new_jobs,
                   updated_metrics_count, status, checkpoint_data
            FROM collection_logs
            WHERE status = 'IN_PROGRESS'
            ORDER BY start_time DESC
        """)
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def recover_interrupted_run(self, run_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely recovers an interrupted pipeline execution.
        Marks previous run as 'RECOVERED_INTERRUPTED' and completes missing pipeline stages.
        """
        run_id = run_info["run_id"]
        logger.warning(f"Initiating recovery for interrupted run: {run_id} (started at {run_info['start_time']})")

        conn = self.db_manager.get_connection()
        c = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        # Update the interrupted run record
        c.execute("""
            UPDATE collection_logs
            SET status = 'RECOVERED_INTERRUPTED',
                end_time = ?,
                error_log = COALESCE(error_log, '') || '\nProcess recovered by Scheduler on ' || ?
            WHERE run_id = ?
        """, (now_iso, now_iso, run_id))
        conn.commit()
        conn.close()

        logger.info(f"Marked run {run_id} as RECOVERED_INTERRUPTED. Triggering catch-up daily pipeline...")
        # Execute catch-up run
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            recovery_summary = loop.run_until_complete(
                self.pipeline.execute_daily_pipeline(
                    execution_type="RECOVERY_CATCHUP",
                    run_pilot=False
                )
            )
            return recovery_summary
        finally:
            loop.close()

    def get_seconds_until_next_run(self, schedule_time_str: str) -> float:
        """Calculates seconds remaining until the next scheduled UTC execution time."""
        target_hour, target_minute = map(int, schedule_time_str.split(":"))
        now_utc = datetime.now(timezone.utc)
        target_today = now_utc.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        if now_utc >= target_today:
            # Target is tomorrow
            target_next = target_today + timedelta(days=1)
        else:
            target_next = target_today

        wait_seconds = (target_next - now_utc).total_seconds()
        return max(0.0, wait_seconds)

    def run_once(self, run_pilot: bool = True, execution_type: str = "DAILY_INCREMENTAL") -> Dict[str, Any]:
        """Runs a single pipeline cycle with automated interruption detection and error logging."""
        interrupted = self.check_for_interrupted_runs()
        if interrupted:
            logger.warning(f"Found {len(interrupted)} interrupted run(s). Recovering first...")
            self.recover_interrupted_run(interrupted[0])

        logger.info(f"Starting single pipeline cycle (execution_type={execution_type}, pilot={run_pilot})...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            summary = loop.run_until_complete(
                self.pipeline.execute_daily_pipeline(
                    execution_type=execution_type,
                    run_pilot=run_pilot
                )
            )
            logger.info(f"Pipeline cycle finished successfully: Run ID {summary['run_id']}")
            return summary
        except Exception as e:
            err_msg = traceback.format_exc()
            logger.error(f"Pipeline execution encountered exception: {e}\n{err_msg}")
            # Log failure in database
            self.db_manager.log_collection_checkpoint({
                "run_id": f"failed_{uuid.uuid4().hex[:8]}",
                "start_time": datetime.now(timezone.utc).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "execution_type": execution_type,
                "rolling_window_start": datetime.now(timezone.utc).isoformat(),
                "rolling_window_end": datetime.now(timezone.utc).isoformat(),
                "status": "FAILED",
                "error_log": err_msg
            })
            raise
        finally:
            loop.close()

    def run_daemon(self, max_runs: Optional[int] = None) -> None:
        """
        Runs the scheduler daemon in an endless loop (or up to max_runs),
        triggering daily updates at the configured UTC schedule.
        """
        logger.info(f"Starting scheduler daemon. Target schedule: {self.daily_schedule_utc} UTC daily.")
        runs_completed = 0

        while not self._shutdown_requested:
            wait_sec = self.get_seconds_until_next_run(self.daily_schedule_utc)
            next_run_dt = datetime.now(timezone.utc) + timedelta(seconds=wait_sec)
            logger.info(f"Next scheduled execution at: {next_run_dt.strftime('%Y-%m-%d %H:%M:%S UTC')} (in {wait_sec/3600:.2f} hours)")

            # Sleep in chunks to allow graceful termination
            slept = 0.0
            chunk = 10.0
            while slept < wait_sec and not self._shutdown_requested:
                to_sleep = min(chunk, wait_sec - slept)
                time.sleep(to_sleep)
                slept += to_sleep

            if self._shutdown_requested:
                logger.info("Scheduler daemon received shutdown request. Exiting.")
                break

            try:
                self.run_once(run_pilot=False, execution_type="SCHEDULED_DAEMON")
                runs_completed += 1
                if max_runs and runs_completed >= max_runs:
                    logger.info(f"Reached max requested runs ({max_runs}). Exiting daemon.")
                    break
            except Exception as e:
                logger.error(f"Error during scheduled execution: {e}. Daemon will retry on next cycle.")


def main():
    parser = argparse.ArgumentParser(description="Rolling AI Ecosystem Pipeline Scheduler")
    parser.add_argument("--run-once", action="store_true", help="Execute single daily update immediately")
    parser.add_argument("--run-daemon", action="store_true", help="Run background scheduler daemon")
    parser.add_argument("--schedule", default="06:00", help="Daily execution time in UTC (HH:MM, default 06:00)")
    parser.add_argument("--check-recovery", action="store_true", help="Check for interrupted or crashed runs")
    parser.add_argument("--resume", action="store_true", help="Resume/recover any interrupted run")
    parser.add_argument("--skip-pilot", action="store_true", help="Skip Phase III pilot enrichment")

    args = parser.parse_args()
    scheduler = RollingPipelineScheduler(daily_schedule_utc=args.schedule)

    if args.check_recovery:
        interrupted = scheduler.check_for_interrupted_runs()
        if not interrupted:
            print("[Scheduler Check] No interrupted runs found. Pipeline is clean.")
        else:
            print(f"[Scheduler Check] Found {len(interrupted)} interrupted run(s):")
            for r in interrupted:
                print(f"  - Run ID: {r['run_id']}, Started: {r['start_time']}, Type: {r['execution_type']}")
        return

    if args.resume:
        interrupted = scheduler.check_for_interrupted_runs()
        if not interrupted:
            print("[Scheduler Resume] No interrupted run to resume.")
        else:
            print(f"[Scheduler Resume] Resuming run {interrupted[0]['run_id']}...")
            res = scheduler.recover_interrupted_run(interrupted[0])
            print(f"[Scheduler Resume] Recovery complete: Run ID {res['run_id']}")
        return

    if args.run_daemon:
        scheduler.run_daemon()
        return

    if args.run_once:
        res = scheduler.run_once(run_pilot=not args.skip_pilot)
        print(f"[Scheduler] Run-once finished successfully: Run ID {res['run_id']}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
