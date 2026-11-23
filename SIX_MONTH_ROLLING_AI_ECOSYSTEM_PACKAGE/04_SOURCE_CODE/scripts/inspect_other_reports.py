import csv

with open('reports/stage2_ai_relevance_audit.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    print("AI Relevance Audit Headers:", reader.fieldnames)
    row = next(reader)
    print("Sample row:", row)

with open('reports/stage2_url_validation.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    print("URL Validation Headers:", reader.fieldnames)
    row = next(reader)
    print("Sample row:", row)
