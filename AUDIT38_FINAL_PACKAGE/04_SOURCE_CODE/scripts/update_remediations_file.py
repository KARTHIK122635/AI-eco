import json

with open('scripts/test_audit15_remediations.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    "'job_a1f6d34afbcae1d9': (\n        'Financial Analysis : Conduct",
    "'job_a1f6d34afbcae1d9': (\n        'Financial Analysis: Conduct"
)
text = text.replace(
    "'job_c906cdf09836f33d': (\n        'Financial Analysis : Conduct",
    "'job_c906cdf09836f33d': (\n        'Financial Analysis: Conduct"
)
text = text.replace(
    "'job_68f457a1316cf9d3': (\n        'Financial Analysis : Conduct growth and margin analysis, discount impact assessment, and deal profitability modeling to support data-driven decision making'",
    "'job_68f457a1316cf9d3': (\n        'Quarterback deals through internal processes — CPQ quote-building, approval routing, contract execution — ensuring accurate, timely completion'"
)

with open('scripts/test_audit15_remediations.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated script successfully!')
