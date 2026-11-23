import json
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

backend_records = [r for r in records if r['classificationReason'] == 'Designs, builds, and maintains backend services, distributed systems, and APIs supporting AI platforms.']

def get_granular_backend_reason(r):
    jid = r['jobId']
    t = r['jobTitle'].strip()
    tl = t.lower()
    resp = r.get('responsibilityEvidence', '') or ''
    rl = resp.lower()

    # HR / People
    if 'people business partner' in tl or 'hr' in tl:
        return "Partners with engineering leadership on organizational talent planning, workforce strategy, and team development."

    # Specific subteams at Anthropic / CoreWeave / etc:
    if 'payment fraud' in tl:
        return "Engineers automated fraud detection systems, transaction verification pipelines, and payment risk models."
    if 'experimentation' in tl:
        return "Builds statistical experimentation frameworks, A/B testing infrastructure, and feature flagging platforms."
    if 'memory & search' in tl:
        return "Engineers long-term memory architectures, stateful retrieval layers, and distributed search indexing for AI models."
    if 'ml sampling path' in tl or 'sampling path' in tl:
        return "Optimizes low-latency machine learning sampling pipelines, token generation kernels, and inference execution paths."
    if 'developer acceleration' in tl:
        return "Builds developer productivity tooling, automated build environments, and developer acceleration infrastructure."
    if 'enterprise connectivity' in tl or 'platform connectivity' in tl:
        return "Engineers enterprise data connectivity protocols, secure ingress pipelines, and API integrations for client platforms."
    if 'platform distribution' in tl or 'platform portability' in tl:
        return "Engineers cross-cloud platform deployment frameworks, container portability, and distributed distribution systems."
    if 'platform intelligence' in tl or 'platform safety' in tl:
        return "Builds platform safety controls, automated policy enforcement mechanisms, and intelligent platform monitoring."
    if 'platform acceleration' in tl:
        return "Accelerates core platform service performance, distributed RPC throughput, and platform runtime efficiency."
    if 'claude science' in tl:
        return "Engineers scientific research workflows, data visualization platforms, and computational tooling for AI models."
    if 'claude design' in tl:
        return "Develops interactive design systems, collaborative UI tools, and frontend design architecture for AI platforms."
    if 'support technology' in tl:
        return "Engineers customer support tooling, automated issue routing infrastructure, and agent diagnostic platforms."
    if 'beneficial deployments' in tl:
        return "Builds reliable software platforms, data integrations, and tooling for beneficial public-interest AI deployments."
    if 'labs' in tl:
        return "Develops exploratory product prototypes, experimental software architectures, and novel AI application workflows."
    if 'research productivity' in tl or 'research tools' in tl:
        return "Builds internal developer platforms, compilation tools, and workflow automation accelerating research productivity."
    if 'people products' in tl:
        return "Develops internal people operations software, employee directory systems, and HR technology workflows."
    if 'consumer' in tl:
        return "Builds consumer-facing application features, user session management, and responsive frontend-backend workflows."
    if 'enterprise ai products' in tl or 'enterprise (platform)' in tl:
        return "Engineers enterprise security controls, administrative consoles, and tenant isolation for enterprise AI platforms."
    if 'search' in tl and 'engineer' in tl:
        return "Engineers machine learning search infrastructure, retrieval ranking algorithms, and discovery systems."
    if 'kubernetes' in tl:
        return "Develops Kubernetes core extensions, custom resource definitions, and container cluster management controllers."
    if 'source control' in tl:
        return "Builds automated code governance pipelines, source control integrations, and compliance policy enforcement tooling."
    if 'ingestion core' in tl:
        return "Engineers high-throughput data ingestion pipelines, streaming connectors, and distributed buffer architectures."
    if 'arc team' in tl or 'arc software' in tl:
        return "Engineers distributed architecture, compute cluster reliability, and system resilience across AI compute platforms."
    if 'ecommerce' in tl or 'e-commerce' in tl:
        return "Develops scalable e-commerce software backends, shopping catalog integrations, and transaction systems."

    # Standard check from earlier
    from build_282_reasons import get_282_reason
    return get_282_reason(r)

test_reasons = [get_granular_backend_reason(r) for r in backend_records]
counts = Counter(test_reasons)
print(f"Distinct reasons for 282: {len(counts)}")
for r_text, c in counts.most_common():
    print(f"{c:2d}x: {r_text}")
