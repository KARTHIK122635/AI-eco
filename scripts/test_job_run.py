import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from sources.ai_job_collector import AIJobCollector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def main():
    collector = AIJobCollector(timeout=15.0)
    jobs = await collector.run()
    print(f"\n==========================================")
    print(f"Total Unique AI Jobs Collected: {len(jobs)}")
    print(f"==========================================")
    
    # Analyze by source
    by_src = {}
    by_cat = {}
    by_emp = {}
    by_exp = {}
    by_remote = {}
    sal_count = 0
    skills_count = 0
    
    for j in jobs:
        src = j["sourceName"]
        by_src[src] = by_src.get(src, 0) + 1
        cat = j["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1
        emp = j["employmentType"]
        by_emp[emp] = by_emp.get(emp, 0) + 1
        exp = j["experienceLevel"]
        by_exp[exp] = by_exp.get(exp, 0) + 1
        rem = j["remoteType"]
        by_remote[rem] = by_remote.get(rem, 0) + 1
        if j["salaryMin"] is not None:
            sal_count += 1
        if j["requiredSkills"]:
            skills_count += 1
            
    print("\nSource Distribution:")
    for s, c in sorted(by_src.items(), key=lambda x: -x[1]):
        print(f"  {s:<35}: {c}")
        
    print("\nCategory Distribution:")
    for cat, c in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"  {cat:<30}: {c}")
        
    print(f"\nSalaries populated: {sal_count} ({sal_count/len(jobs)*100:.1f}%)")
    print(f"Skills extracted:   {skills_count} ({skills_count/len(jobs)*100:.1f}%)")
    print(f"\nSample Job Record:")
    if jobs:
        import pprint
        pprint.pprint(jobs[0])

if __name__ == '__main__':
    asyncio.run(main())
