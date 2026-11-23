import json

with open("data/canonical/canonical_products.jsonl", "r", encoding="utf-8") as f:
    products = [json.loads(line) for line in f]

for p in products[50:54]:
    print(p["content"]["entityName"])
    print(" ", p["content"]["data"])
