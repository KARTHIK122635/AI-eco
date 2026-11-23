import json
import sys
sys.path.append('scripts')
from build_audit8_reasons import records, generate_audit8_reason

c1_titles = [r['jobTitle'] for r in records if generate_audit8_reason(r) == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']
c2_titles = [r['jobTitle'] for r in records if generate_audit8_reason(r) == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

print(f"Cluster 1 count: {len(c1_titles)}")
print("Sample Cluster 1 titles:")
for t in sorted(set(c1_titles))[:40]:
    print("  *", t)

print(f"\nCluster 2 count: {len(c2_titles)}")
print("Sample Cluster 2 titles:")
for t in sorted(set(c2_titles))[:40]:
    print("  *", t)
