"""
Stage 3 Human Review & Approval Queue Manager
=============================================
Provides CLI interface to inspect, approve, reject, or request review for
Gemini LLM enrichment proposals in compliance with Stage 3 requirements.

Supported decisions:
- APPROVE: Explicitly marks proposal as approved for eventual canonical database application.
- REJECT: Rejects proposal with required reason.
- REQUEST_REVIEW: Marks proposal for further investigation/context.

Default status of all new proposals is PENDING_APPROVAL.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ReviewQueueManager:
    """Manages the human review workflow for Stage 3 enrichment proposals."""

    VALID_DECISIONS = {"APPROVE", "REJECT", "REQUEST_REVIEW"}

    def __init__(
        self,
        queue_csv_path: str = "data/stage3/gemini_review_queue.csv",
        results_jsonl_path: str = "data/stage3/gemini_enrichment_results.jsonl",
        summary_json_path: str = "data/stage3/gemini_enrichment_summary.json",
    ):
        self.queue_csv_path = os.path.abspath(queue_csv_path)
        self.results_jsonl_path = os.path.abspath(results_jsonl_path)
        self.summary_json_path = os.path.abspath(summary_json_path)

    def load_queue_csv(self) -> List[Dict[str, str]]:
        """Loads all proposals from the review queue CSV."""
        if not os.path.exists(self.queue_csv_path):
            return []
        with open(self.queue_csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def load_results_jsonl(self) -> Dict[str, Dict[str, Any]]:
        """Loads detailed proposals from JSONL keyed by proposal_id."""
        if not os.path.exists(self.results_jsonl_path):
            return {}
        results = {}
        with open(self.results_jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    pid = data.get("proposal_id")
                    if pid:
                        results[pid] = data
        return results

    def save_queue_csv(self, rows: List[Dict[str, str]]):
        """Saves updated review queue to CSV."""
        if not rows:
            return
        fieldnames = list(rows[0].keys())
        with open(self.queue_csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def save_results_jsonl(self, results: Dict[str, Dict[str, Any]]):
        """Saves updated detailed proposals back to JSONL."""
        with open(self.results_jsonl_path, "w", encoding="utf-8") as f:
            for p in results.values():
                f.write(json.dumps(p, ensure_ascii=False) + "\n")

    def update_summary_json(self):
        """Recomputes approval distribution and updates summary JSON."""
        if not os.path.exists(self.summary_json_path):
            return

        with open(self.summary_json_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        rows = self.load_queue_csv()
        approval_dist = {
            "PENDING_APPROVAL": 0,
            "APPROVED": 0,
            "REJECTED": 0,
            "REQUEST_REVIEW": 0,
        }
        for r in rows:
            st = r.get("approval_status", "PENDING_APPROVAL")
            approval_dist[st] = approval_dist.get(st, 0) + 1

        summary["approval_distribution"] = approval_dist
        summary["last_reviewed_at"] = datetime.now(timezone.utc).isoformat()

        with open(self.summary_json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def list_proposals(self, filter_status: Optional[str] = None):
        """Prints a tabular summary of proposals in the review queue."""
        rows = self.load_queue_csv()
        if not rows:
            print("No proposals found in review queue.")
            return

        if filter_status:
            rows = [r for r in rows if r.get("approval_status") == filter_status or r.get("validation_status") == filter_status]

        print("=" * 115)
        print(f"{'#':<3} {'Proposal ID':<36} {'Record ID':<26} {'Field':<18} {'Validation':<14} {'Approval Status'}")
        print("=" * 115)

        for i, r in enumerate(rows, 1):
            pid = r.get("proposal_id", "")
            rec_id = r.get("record_id", "")
            if len(rec_id) > 24:
                rec_id = rec_id[:21] + "..."
            field = r.get("field_name", "")
            val_st = r.get("validation_status", "")
            app_st = r.get("approval_status", "")

            print(f"{i:<3} {pid:<36} {rec_id:<26} {field:<18} {val_st:<14} {app_st}")

        print("=" * 115)
        print(f"Total shown: {len(rows)}")

    def show_proposal(self, proposal_id: str):
        """Displays exhaustive details of a single proposal."""
        results = self.load_results_jsonl()
        proposal = results.get(proposal_id)
        if not proposal:
            # Check CSV if not in JSONL
            rows = self.load_queue_csv()
            for r in rows:
                if r.get("proposal_id") == proposal_id:
                    proposal = r
                    break

        if not proposal:
            print(f"[ERROR] Proposal ID '{proposal_id}' not found.")
            return

        print("=" * 80)
        print(f"PROPOSAL DETAILS: {proposal_id}")
        print("=" * 80)
        print(f"Record ID:            {proposal.get('record_id')}")
        print(f"Entity Type:          {proposal.get('entity_type')}")
        print(f"Target Field:         {proposal.get('field_name')}")
        print(f"Original Value:       {proposal.get('original_value')}")
        print(f"Gemini Proposed:      {proposal.get('proposed_value')}")
        print(f"Confidence Score:     {proposal.get('confidence_score')}")
        print(f"Validation Status:    {proposal.get('validation_status')}")
        print(f"Validation Rationale: {proposal.get('validation_rationale')}")
        print(f"Approval Status:      {proposal.get('approval_status')}")
        print(f"Reviewer:             {proposal.get('reviewer') or 'Unreviewed'}")
        print(f"Reviewed At:          {proposal.get('reviewed_at') or 'N/A'}")
        print(f"Review Notes:         {proposal.get('review_notes') or 'N/A'}")
        print("-" * 80)
        print("Evidence Quotation:")
        print(f"  \"{proposal.get('evidence_quote')}\"")
        print(f"Evidence Source URL:  {proposal.get('evidence_url')}")
        print(f"Evidence Summary:     {proposal.get('evidence')}")
        print("-" * 80)
        print(f"Reasoning:            {proposal.get('reasoning')}")
        print(f"Limitations:          {proposal.get('limitations')}")
        print(f"Model ID:             {proposal.get('model_id')}")
        print(f"Provider:             {proposal.get('provider')}")
        print("=" * 80)

    def record_decision(
        self,
        proposal_id: str,
        decision: str,
        reviewer: str,
        notes: str = "",
    ) -> bool:
        """Records a human review decision for a proposal."""
        if decision not in self.VALID_DECISIONS:
            print(f"[ERROR] Invalid decision: {decision}. Must be one of {self.VALID_DECISIONS}")
            return False

        # Update CSV
        rows = self.load_queue_csv()
        found = False
        target_row = None
        for r in rows:
            if r.get("proposal_id") == proposal_id:
                found = True
                target_row = r
                break

        if not found:
            print(f"[ERROR] Proposal ID '{proposal_id}' not found in review queue CSV.")
            return False

        timestamp = datetime.now(timezone.utc).isoformat()
        target_row["approval_status"] = decision
        target_row["reviewer"] = reviewer
        target_row["reviewed_at"] = timestamp
        target_row["review_notes"] = notes
        self.save_queue_csv(rows)

        # Update JSONL
        results = self.load_results_jsonl()
        if proposal_id in results:
            results[proposal_id]["approval_status"] = decision
            results[proposal_id]["reviewer"] = reviewer
            results[proposal_id]["reviewed_at"] = timestamp
            results[proposal_id]["review_notes"] = notes
            self.save_results_jsonl(results)

        # Update Summary
        self.update_summary_json()

        print(f"[SUCCESS] Proposal '{proposal_id}' updated to '{decision}' by {reviewer} at {timestamp}.")
        if notes:
            print(f"          Notes: {notes}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Stage 3 Gemini Review Queue Manager")
    parser.add_argument("--queue-csv", default="data/stage3/gemini_review_queue.csv", help="Path to review queue CSV")
    parser.add_argument("--results-jsonl", default="data/stage3/gemini_enrichment_results.jsonl", help="Path to results JSONL")
    parser.add_argument("--summary-json", default="data/stage3/gemini_enrichment_summary.json", help="Path to summary JSON")

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--list", action="store_true", help="List all proposals in review queue")
    action_group.add_argument("--show", metavar="PROPOSAL_ID", help="Show full details of a specific proposal")
    action_group.add_argument("--approve", metavar="PROPOSAL_ID", help="Approve a proposal")
    action_group.add_argument("--reject", metavar="PROPOSAL_ID", help="Reject a proposal")
    action_group.add_argument("--request-review", metavar="PROPOSAL_ID", help="Flag proposal for review")

    parser.add_argument("--filter-status", help="Filter --list by approval or validation status")
    parser.add_argument("--reviewer", default="human_auditor", help="Name or ID of reviewer")
    parser.add_argument("--notes", default="", help="Review notes or justification")

    args = parser.parse_args()

    manager = ReviewQueueManager(
        queue_csv_path=args.queue_csv,
        results_jsonl_path=args.results_jsonl,
        summary_json_path=args.summary_json,
    )

    if args.list:
        manager.list_proposals(filter_status=args.filter_status)
    elif args.show:
        manager.show_proposal(args.show)
    elif args.approve:
        manager.record_decision(args.approve, "APPROVED", args.reviewer, args.notes)
    elif args.reject:
        if not args.notes:
            print("[ERROR] Rejection requires --notes explaining why the proposal is rejected.")
            sys.exit(1)
        manager.record_decision(args.reject, "REJECTED", args.reviewer, args.notes)
    elif args.request_review:
        manager.record_decision(args.request_review, "REQUEST_REVIEW", args.reviewer, args.notes)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
