import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

SPECIFIC_TARGET_EXCERPTS = {
    'job_d207b42e585bf8e6': "Design paid and digital campaign strategies for legislative and policy goals, including objectives, audiences, messaging, tactics, phasing, and budget",
    'job_80a480dfe5f61806': "Translate technical research, model capability, and scientific content into policy-ready language for federal, state, and international policymakers, their staff, and legislators.",
    'job_03adf198b79570b7': "Execute molecular biology and biochemistry experiments at the bench under the direction of senior scientists Maintain meticulous, reproducible records and contribute to shared protocols",
    'job_3ab4fad59bd0a42d': "Generate experimental and computational data, for example from quantum mechanical calculations, that research teams use to train and evaluate AI models",
    'job_b30c4117b32b2e1b': "Evaluate AI-designed antibodies, drive them to experimental readout, and feed results back to research teams",
    'job_d2ffb1910190a82b': "Invent the deal structures. You'll work with Scale’s legal team to define the first version of how these transactions get priced. Close. Own it from cold outreach to signature.",
    'job_db2382f595bbb7fd': "Respond to user support cases, in English and Japanese, with a variety of complexity, from simple billing or account questions for individuals to complex API debugging for large businesses",
    'job_38af1bff8a24f3e0': "Respond to user support cases with a variety of complexity, from simple billing or account questions for individuals to complex API debugging for large businesses",
}

# Verify specific targets
for jid, text in SPECIFIC_TARGET_EXCERPTS.items():
    job = [j for j in jobs if j['jobId'] == jid][0]
    desc = job['jobDescription']
    assert text in desc, f"Missing target {jid}: {text}"

suspect_patterns = [
    r'^\s*we are hiring\b',
    r'^\s*we\'re hiring\b',
    r'^\s*we’re hiring\b',
    r'^\s*we are looking\b',
    r'^\s*we\'re looking\b',
    r'^\s*we’re looking\b',
    r'^\s*we are seeking\b',
    r'^\s*we\'re seeking\b',
    r'^\s*we’re seeking\b',
    r'^\s*join\b',
    r'^\s*about (?:the|us|anthropic|scale|openai|coreweave|our|this|zilliz|google|databricks)\b',
    r'^\s*who we are\b',
    r'is seeking\b',
    r'is looking\b',
    r'is hiring\b',
    r'team is building\b',
    r'is building the\b',
    r'is building a\b',
    r'builds RL environments\b',
    r'^\s*at [a-zA-Z0-9\s]+, we\b',
    r'^\s*our mission is\b',
    r'^\s*come join\b',
    r'^\s*overview\b',
    r'^\s*the role\b',
    r'^\s*the position\b',
    r'^\s*about the role\b',
    r'^\s*about the team\b',
    r'^\s*we are an equal\b',
    r'^\s*anthropic is\b',
    r'^\s*scale is\b',
    r'^\s*coreweave is\b',
    r'^\s*openai is\b',
    r'^\s*databricks is\b',
    r'^\s*cresta is\b',
    r'^\s*together ai is\b',
    r'^\s*figure ai is\b',
    r'^\s*snorkel is\b',
    r'^\s*cohere is\b',
    r'^\s*mistral is\b',
    r'^\s*we believe\b',
    r'^\s*we value\b',
    r'^\s*we think\b',
    r'^\s*you will join\b',
    r'^\s*in this role, you will join\b'
]

def is_suspect(text):
    if not text:
        return True
    for p in suspect_patterns:
        if re.search(p, text.strip(), re.I):
            return True
    return False

# Zilliz special handling if description has no responsibilities
# Let's inspect all Zilliz jobs in canonical
zilliz_jobs = [j for j in jobs if 'zilliz' in j['companyName'].lower()]
print(f"Total Zilliz jobs: {len(zilliz_jobs)}")
for zj in zilliz_jobs:
    print(zj['jobId'], zj['jobTitle'], len(zj['jobDescription']))
