import json

with open("data/canonical/canonical_products.jsonl", "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

print("Sample product records:")
for p in products[:3]:
    print(p["content"]["entityName"])
    print(" ", p["content"]["data"])
