import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

# Let's inspect each cluster and check if there are any specific mismatches
from collections import Counter
counts = Counter(r['classificationReason'] for r in records)

print("Checking medium clusters for unexpected job titles:")
for reason, count in counts.most_common():
    if 10 <= count <= 45:
        matching = [r for r in records if r['classificationReason'] == reason]
        r_low = reason.lower()
        
        # Let's inspect titles
        for m in matching:
            t_low = m['jobTitle'].lower()
            
            # Check 42: Builds and operates large-scale cloud compute platforms, containerized environments, and cluster resource managers.
            if 'cloud compute platforms' in r_low:
                if 'sales' in t_low or 'marketing' in t_low or 'hr' in t_low or 'product' in t_low:
                    print(f"Mismatch in cloud cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 41: Implements security controls, vulnerability management, and defensive systems protecting enterprise infrastructure.
            if 'security controls' in r_low:
                if not any(k in t_low for k in ['sec', 'trust', 'threat', 'defense', 'iam', 'safeguard', 'vulnerability', 'incident', 'network']):
                    print(f"Mismatch in security cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 41: Partners directly with enterprise customers to build, customize, and productionize generative AI applications.
            if 'partners directly with enterprise customers' in r_low:
                if not any(k in t_low for k in ['forward deployed', 'fde', 'customer', 'solution', 'deployed']):
                    print(f"Mismatch in FDE cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 39: Manages enterprise sales cycles, client negotiations, and commercial contract execution.
            if 'enterprise sales cycles' in r_low:
                if not any(k in t_low for k in ['sales', 'account executive', 'ae', 'bdr', 'sdr', 'commercial', 'deal', 'business development']):
                    print(f"Mismatch in sales cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 38: Manages strategic cloud partner relationships, co-selling motions, and enterprise go-to-market alliances.
            if 'cloud partner relationships' in r_low:
                if not any(k in t_low for k in ['partner', 'alliance', 'channel', 'ecosystem', 'co-sell']):
                    print(f"Mismatch in partner cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 38: Develops, maintains, and supports internal IT systems, enterprise applications, and corporate technology.
            if 'internal it systems' in r_low:
                if not any(k in t_low for k in ['it', 'support', 'helpdesk', 'system', 'corporate', 'service', 'audio', 'av', 'workplace', 'endpoint', 'desktop']):
                    print(f"Mismatch in IT cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 32: Builds financial forecasts, operating budgets, and capital allocation models to guide business planning.
            if 'financial forecasts' in r_low:
                if not any(k in t_low for k in ['finan', 'fp&a', 'budget', 'treasury', 'deal', 'pricing', 'model', 'capital', 'strategic finance']):
                    print(f"Mismatch in finance cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 31: Manages revenue recognition, financial reporting, accounting controls and audit readiness.
            if 'revenue recognition' in r_low:
                if not any(k in t_low for k in ['account', 'audit', 'tax', 'close', 'payroll', 'billing', 'revenue', 'controller', 'sox', 'financial reporting']):
                    print(f"Mismatch in accounting cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 29: Coordinates technical programs, cross-functional engineering deliverables, and software release timelines.
            if 'technical programs' in r_low:
                if not any(k in t_low for k in ['program', 'tpm', 'project', 'coordinator', 'delivery', 'release']):
                    print(f"Mismatch in TPM cluster: {m['jobId']} | {m['jobTitle']}")
                    
            # Check 27: Leads software engineering teams, technical project delivery, and engineering architecture.
            if 'leads software engineering teams' in r_low:
                if not any(k in t_low for k in ['manager', 'director', 'lead', 'head', 'vp']):
                    print(f"Mismatch in EM cluster: {m['jobId']} | {m['jobTitle']}")

print("Check finished.")
