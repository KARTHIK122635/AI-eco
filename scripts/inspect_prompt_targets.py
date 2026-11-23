import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

target_ids = [
    'job_090ae3e6187d0e95', # Engineering Manager, Connectivity - London
    'job_99a16541f25f6011', # Staff Infrastructure Engineer, Cluster Infrastructure
    'job_8fa1c552d19c1545', # Staff+ Software Engineer, Platform Connectivity
    'job_312c813f6ac2ff0d', # Technical Program Manager, Science Strategy & Communications
    'job_95b43ad5f542500c', # Strategic Finance Manager, BU Partnership (Scale AI)
    'job_5fcaf184c259b65a', # Technical Support Engineer II (CoreWeave)
    'job_61fd4233c744a6f8', # Technical Support Engineer II - CoreWeave Forge
    'job_a8b0b2fba1f2d038', # Technical Support Engineer II - CoreWeave Forge
    'job_61144ba521cc8449', # Senior Staff Software Engineer, AI Runtime (Databricks)
    'job_1b9058f92fab34da', # AI R&D Engineer – Model Training (Aleph Alpha)
    'job_366b4bea010eed1f', # Senior AI R&D Engineer – Model Training (Aleph Alpha)
    'job_889d2fb771307d3f', # Senior Backend Software Engineer (Cloud Monetization Platform) (Nebius)
    'job_2c80e5fb066f0e51', # Senior Site Reliability Engineer (Data Platform) (Nebius)
    'job_10c062ac3703d86a', # Senior Site Reliability Engineer (Data Platform) (Nebius)
    'job_56be0fafcdaa036c', # Senior AI Engineer / Consultant (Artifact)
    'job_2131aa478b54ee53', # AI Engineer / Consultant (Artifact)
    'job_3c5d6884b25b32d7', # AI Engineer / Consultant - Internship (Artifact)
]

for jid in target_ids:
    j = jobs[jid]
    print(f"=== {jid} | {j['companyName']} | {j['jobTitle']} ===")
    print("Reason:", j.get('classificationReason'))
    desc = j['jobDescription']
    for kw in ['responsibilities', 'responsibility', 'what you\'ll do', 'what you will do', 'you will', 'tasks']:
        m = re.search(r'\b' + kw + r'\b', desc, re.I)
        if m:
            print("Section from:", kw)
            print(desc[m.start():m.start()+500])
            print("---")
            break
    print("=" * 60)
