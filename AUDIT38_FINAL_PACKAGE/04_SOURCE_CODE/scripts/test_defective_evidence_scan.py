import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import json
import re

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]

# Let's see what happens if we look at evidence excerpts that:
# 1. Match company mission / intro / team intro / world-class / paint the vision / fellowship intro / data center intro
# Let's inspect the evidence of all jobs and see which ones are genuine defects!

def is_defective_evidence(j):
    ev = j.get('responsibilityEvidence', '') or ''
    title = j['jobTitle'].lower()
    
    # Priority roles mentioned explicitly by prompt:
    if any(p in title for p in [
        'finance fellow', 'billing platform', 'chip design rl', 'code rl',
        'principal software engineer, gps', 'medical fellow',
        'product marketing manager, healthcare'
    ]):
        # Check if ev has intro/team/etc.
        return True, 'priority_role'
    if 'data center technician' in title:
        if any(w in ev.lower() for w in ['operations team', 'work well with others', 'play a key role', 'covers hardware and network']):
            return True, 'data_center_technician_intro'
            
    # Check for obvious intro/promotional/qualification markers:
    if 'paint the vision' in ev.lower():
        return True, 'paint_the_vision'
    if 'exists to ensure' in ev.lower():
        return True, 'exists_to_ensure'
    if 'sit at the intersection' in ev.lower():
        return True, 'sit_at_intersection'
    if 'world-class' in ev.lower():
        return True, 'world_class'
    if 'collaborative work: get invited' in ev.lower():
        return True, 'collaborative_work'
    if 'ideal candidate' in ev.lower():
        return True, 'ideal_candidate'
    if 'years of experience' in ev.lower() or 'years experience' in ev.lower():
        return True, 'years_of_experience'
    if re.search(r'\bwho you are\b|\bwhat you\'ll need\b', ev, re.I):
        return True, 'qualification_header'
    if re.search(r'\bwe are looking for\b|\bwe’re looking for\b|\bwe are seeking\b', ev, re.I):
        return True, 'recruitment_pitch'
    if re.search(r'^as an? (?:applied ai|member|deployment manager|account executive|partners solutions architect)', ev, re.I):
        return True, 'as_an_intro'
    if re.search(r'\bour data center operations team\b', ev, re.I):
        return True, 'our_data_center_team'
    if re.search(r'^scale’s rapidly growing', ev, re.I):
        return True, 'scale_intro'
        
    return False, None

defects = []
for j in jobs:
    is_def, reason = is_defective_evidence(j)
    if is_def:
        defects.append((j, reason))

print(f"Total defects found by unified logic: {len(defects)}")
