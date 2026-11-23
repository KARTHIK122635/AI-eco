import os
import json
import csv
import sqlite3
from typing import List, Optional
from core.models import StartupProductRecord


class StorageManager:
    """Manages exporting collected records to JSONL, CSV, and SQLite."""
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.jsonl_path = os.path.join(self.data_dir, "startups_and_products.jsonl")
        self.csv_path = os.path.join(self.data_dir, "startups_and_products.csv")
        self.db_path = os.path.join(self.data_dir, "startups_and_products.db")
        self._init_sqlite()

    def _init_sqlite(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                product_name TEXT,
                description TEXT,
                employee_count TEXT,
                pricing_model TEXT,
                company_website TEXT,
                original_source_url TEXT UNIQUE,
                source_directory TEXT,
                categories TEXT,
                discovered_at TEXT,
                raw_metadata TEXT
            )
            """)
            conn.commit()

    def append_record(self, record: StartupProductRecord):
        # 1. JSONL append
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

        # 2. SQLite append
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO records (
                company_name, product_name, description, employee_count,
                pricing_model, company_website, original_source_url,
                source_directory, categories, discovered_at, raw_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.company_name,
                record.product_name,
                record.description,
                str(record.employee_count) if record.employee_count is not None else None,
                record.pricing_model,
                record.company_website,
                record.original_source_url,
                record.source_directory,
                ", ".join(record.categories) if record.categories else None,
                record.discovered_at,
                json.dumps(record.raw_metadata)
            ))
            conn.commit()

    def export_csv(self, records: List[StartupProductRecord]):
        fieldnames = [
            "company_name", "product_name", "description", "employee_count",
            "pricing_model", "company_website", "original_source_url",
            "source_directory", "categories", "discovered_at"
        ]
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                d = r.to_dict()
                d["categories"] = "; ".join(d.get("categories", []))
                d.pop("raw_metadata", None)
                writer.writerow(d)
