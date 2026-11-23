import json
import csv
import sqlite3

# Load JSONL
jsonl_records = []
with open("data/canonical/canonical_jobs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        jsonl_records.append(json.loads(line)["content"]["data"])

# Load CSV
csv_rows = []
with open("data/canonical/canonical_jobs.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_rows.append(row)

# Load SQLite
conn = sqlite3.connect("data/normalized/ai_ecosystem.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM ai_jobs ORDER BY rowid")
sqlite_rows = cur.fetchall()
conn.close()

print(f"Loaded: JSONL={len(jsonl_records)}, CSV={len(csv_rows)}, SQLite={len(sqlite_rows)}")

field_map = {
    "jobId": "job_id",
    "jobTitle": "job_title",
    "companyName": "company_name",
    "companyWebsite": "company_website",
    "category": "category",
    "classificationReason": "classification_reason",
    "responsibilityEvidence": "responsibility_evidence",
    "qualificationEvidence": "qualification_evidence",
    "classificationConfidence": "classification_confidence",
    "jobDescription": "job_description",
    "requiredSkills": "required_skills",
    "preferredSkills": "preferred_skills",
    "experienceLevel": "experience_level",
    "location": "location",
    "remoteType": "remote_type",
    "salaryMin": "salary_min",
    "salaryMax": "salary_max",
    "currency": "currency",
    "compensationType": "compensation_type",
    "compensationPeriod": "compensation_period",
    "employmentType": "employment_type",
    "jobStatus": "job_status",
    "vacancyStatus": "vacancy_status",
    "applicationUrl": "application_url",
    "postedAt": "posted_at",
    "sourceName": "source_name",
    "provenance": "provenance",
    "collectedAt": "collected_at"
}

mismatches = []
null_string_discrepancies = []

for i in range(1930):
    j_rec = jsonl_records[i]
    c_rec = csv_rows[i]
    s_rec = sqlite_rows[i]

    for j_key, s_key in field_map.items():
        j_val = j_rec.get(j_key)
        # CSV may have camelCase or snake_case key
        c_val = c_rec.get(j_key) if j_key in c_rec else c_rec.get(s_key)
        s_val = s_rec[s_key]

        # Handle list / dict fields (skills, provenance)
        if isinstance(j_val, (list, dict)):
            c_val_parsed = json.loads(c_val) if c_val else ([] if isinstance(j_val, list) else {})
            s_val_parsed = json.loads(s_val) if s_val else ([] if isinstance(j_val, list) else {})
            if not (j_val == c_val_parsed == s_val_parsed):
                mismatches.append((i, j_key, j_val, c_val, s_val))
            continue

        # Handle float fields (salary, confidence)
        if isinstance(j_val, float):
            c_float = float(c_val) if (c_val is not None and c_val != "") else None
            s_float = float(s_val) if s_val is not None else None
            if not (j_val == c_float == s_float):
                mismatches.append((i, j_key, j_val, c_val, s_val))
            continue

        # Handle null / empty representation
        # JSONL None should correspond to CSV "" and SQLite None
        if j_val is None:
            if c_val != "" and c_val is not None:
                null_string_discrepancies.append((i, j_key, "JSONL None vs CSV non-empty", j_val, c_val))
            if s_val is not None:
                null_string_discrepancies.append((i, j_key, "JSONL None vs SQLite non-NULL", j_val, s_val))
        else:
            # Non-null values should match exactly as strings
            if str(j_val) != str(c_val):
                mismatches.append((i, j_key, f"JSONL vs CSV: '{j_val}' vs '{c_val}'"))
            if str(j_val) != str(s_val):
                mismatches.append((i, j_key, f"JSONL vs SQLite: '{j_val}' vs '{s_val}'"))

print(f"Total value mismatches: {len(mismatches)}")
print(f"Total null/string representation discrepancies: {len(null_string_discrepancies)}")

if len(mismatches) == 0 and len(null_string_discrepancies) == 0:
    print("SUCCESS: 100.0% Exact Parity Verified Across All 28 Fields & 1,930 Records!")
else:
    for m in mismatches[:10]:
        print("Mismatch:", m)
    for n in null_string_discrepancies[:10]:
        print("Null/String:", n)
