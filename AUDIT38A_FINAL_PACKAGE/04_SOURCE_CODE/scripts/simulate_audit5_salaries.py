import json
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Current salary stats
curr_salaries = [r for r in records if r['salaryMin'] is not None]
print(f"Current salary count: {len(curr_salaries)} / {len(records)} ({len(curr_salaries)/len(records)*100:.2f}%)")

# Specific additions
additions = {
    'job_16db3f40963e47c5': (100.0, 100.0, 'USD', 'HOURLY', 'HOURLY'), # Scale AI
    'job_671b00fff11cfc18': (41.0, 41.0, 'USD', 'HOURLY', 'HOURLY'),   # Together AI
    'job_689c9625b67fc607': (85.0, 165.0, 'USD', 'HOURLY', 'HOURLY'),  # Snorkel AI
    'job_ac563bb449616a82': (55.0, 65.0, 'USD', 'HOURLY', 'HOURLY'),   # CoreWeave
    'job_bfc1bda2dd9fdcc8': (40.0, 50.0, 'USD', 'HOURLY', 'HOURLY'),   # CoreWeave
    'job_90a3078b4542f9c4': (54.0, 60.0, 'USD', 'HOURLY', 'HOURLY'),   # Databricks
    'job_b031e8b7e7239b46': (54.0, 60.0, 'USD', 'HOURLY', 'HOURLY'),   # Databricks
    'job_fece52c6d4b2a2d4': (77400.0, 77400.0, 'USD', 'ANNUAL_BASE', 'ANNUAL'), # Figure AI
    'job_9395ac8eab83c8a2': (255000.0, 295000.0, 'EUR', 'ANNUAL_BASE', 'ANNUAL'), # Black Forest Labs
    'job_52cf5f192858c983': (70000.0, 70000.0, 'USD', 'ANNUAL_BASE', 'ANNUAL'), # Metics Media
    'job_df65ec2483015bf8': (3100.0, 4000.0, 'EUR', 'MONTHLY_BASE', 'MONTHLY'), # DPG Media
    'job_c9198a409b102f75': (500.0, 500.0, 'EUR', 'STIPEND', 'MONTHLY'), # Pacmed
    'job_bea17c7bbad33d34': (450.0, 450.0, 'EUR', 'STIPEND', 'MONTHLY'), # HG International
    'job_34fbc71b784fa7f5': (700.0, 900.0, 'EUR', 'STIPEND', 'MONTHLY'), # IG&H
    'job_ed0544426f0efc0a': (5000.0, 7000.0, 'EUR', 'MONTHLY_BASE', 'MONTHLY'), # 6Gorilla's
    'job_8b6a7fe68fff1038': (3000.0, 4500.0, 'EUR', 'MONTHLY_BASE', 'MONTHLY'), # TAGGRS
    'job_ba5d0da6c2aa3192': (60000.0, 90000.0, 'EUR', 'ANNUAL_BASE', 'ANNUAL'), # Right Search
    # SambaNova
    'job_f50c9c2b5d1ae59c': (10300000.0, 12500000.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_561df8dd257b27b9': (15700000.0, 19200000.0, 'JPY', 'ANNUAL_BASE', 'ANNUAL'),
    'job_257625b2d48c07c1': (3323700.0, 4062300.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_461a68d5fd1d433e': (32670000.0, 39900000.0, 'JPY', 'ANNUAL_BASE', 'ANNUAL'),
    'job_eadf9e7dc1eb5d90': (32670000.0, 39900000.0, 'JPY', 'ANNUAL_BASE', 'ANNUAL'),
    'job_89c1df16de24aba9': (15000000.0, 20000000.0, 'JPY', 'ANNUAL_BASE', 'ANNUAL'),
    'job_6f918d994f72d395': (8900000.0, 10800000.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_86d26fbdc7079f56': (8900000.0, 10800000.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_a0462dcb58f6f737': (8900000.0, 10800000.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_a3420cff829b095b': (10300000.0, 12500000.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_a5dfcc8c67f2315d': (10300000.0, 12500000.0, 'INR', 'ANNUAL_BASE', 'ANNUAL'),
    'job_db0abfd886c01521': (15000000.0, 20000000.0, 'JPY', 'ANNUAL_BASE', 'ANNUAL'),
}

new_salaries_count = len(curr_salaries) + len(additions)
print(f"New salary count: {new_salaries_count} / {len(records)} ({new_salaries_count/len(records)*100:.2f}%)")
print(f"Remaining null salaries: {len(records) - new_salaries_count}")

# Simulate types and periods
types = []
periods = []
currencies = []
for r in records:
    jid = r['jobId']
    if jid in additions:
        smin, smax, curr, ctype, cper = additions[jid]
        types.append(ctype)
        periods.append(cper)
        currencies.append(curr)
    elif r['salaryMin'] is not None:
        types.append(r['compensationType'])
        periods.append(r['compensationPeriod'])
        currencies.append(r['currency'])
    else:
        types.append(None)
        periods.append(None)
        currencies.append(None)

print("\nCompensation Types Breakdown:")
print(Counter(types))
print("\nCompensation Periods Breakdown:")
print(Counter(periods))
print("\nCurrencies Breakdown:")
print(Counter(currencies))
