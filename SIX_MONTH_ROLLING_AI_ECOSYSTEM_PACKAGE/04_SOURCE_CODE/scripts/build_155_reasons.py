import json
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    records = [json.loads(line)['content']['data'] for line in f]

biz_records = [r for r in records if r['classificationReason'] == 'Coordinates cross-functional business operations, program delivery, and operational planning cadences.']

print(f"Biz records: {len(biz_records)}")

def get_155_reason(r):
    jid = r['jobId']
    t = r['jobTitle'].strip()
    tl = t.lower()
    comp = r['companyName'].strip()
    resp = r.get('responsibilityEvidence', '') or ''
    rl = resp.lower()

    # Explicit examples from prompt:
    # - CMC & Manufacturing Lead, Life Sciences
    if 'cmc' in tl or 'manufacturing lead' in tl:
        return "Oversees chemistry, manufacturing, and controls (CMC) compliance, regulatory filings, and biopharma production operations."
    # - Customer Success Manager (handle double space or normal)
    if 'customer' in tl and 'success' in tl:
        return "Guides enterprise customer onboarding, relationship management, product adoption, and client retention."
    # - Director, IT SOX / Director, SOX Infrastructure
    if 'sox' in tl:
        if 'infrastructure' in tl:
            return "Leads internal control design, SOX compliance, and financial risk governance for compute and cloud infrastructure spend."
        return "Leads IT general controls audits, SOX compliance assessments, and financial system security governance."
    # - Data Center Asset Management, Commercial Associate
    if 'asset management' in tl:
        return "Manages commercial lease contracts, physical asset tracking, and procurement operations for data center facilities."
    # - Discovery Technical Operations Specialist
    if 'discovery' in tl or 'technical operations specialist' in tl:
        return "Coordinates electronic discovery technical operations, legal hold lifecycles, and litigation data governance."
    # - Docs Lead, Platform
    if 'docs lead' in tl or 'documentation' in tl:
        return "Leads developer documentation strategy, API reference authoring, and platform technical guides."

    # Other specific roles in 155:
    if 'gas supply' in tl:
        return "Manages natural gas supply procurement, pipeline transportation agreements, and utility capacity for data centers."
    if 'hardware lab' in tl or 'lab manager' in tl:
        return "Manages hardware laboratory facilities, equipment receiving, rack staging, power distribution, and physical lab safety."
    if 'incident manager' in tl:
        if 'safeguards' in tl:
            return "Manages trust and safety incident escalations, model abuse mitigation workflows, and policy enforcement responses."
        return "Coordinates technical incident triage, cross-functional response cadences, and post-incident reviews for security operations."
    if 'safeguards enforcement' in tl:
        if 'bio' in tl:
            return "Investigates biological safety risks, conducts misuse investigations, and enforces trust and safety policies."
        if 'takeover' in tl or 'credential' in tl:
            return "Investigates account takeover incidents, credential stuffing attacks, and identity abuse patterns."
        if 'access controls' in tl or 'identity' in tl:
            return "Enforces account access policies, investigates malicious credential usage, and manages platform access reviews."
        if 'integrity' in tl or 'authenticity' in tl:
            return "Enforces platform integrity policies, investigates synthetic content misuse, and mitigates coordinated abuse campaigns."
        if 'well-being' in tl or 'well being' in tl:
            return "Leads trust and safety enforcement for user well-being, severe harm mitigation, and sensitive safety workflows."
        return "Enforces trust and safety policies, evaluates safety incident queues, and conducts account abuse investigations."
    if 'threat investigator' in tl or 'threat intel' in tl:
        if 'cbrn' in tl or 'weapons' in tl:
            return "Investigates technical threats involving chemical, biological, radiological, and nuclear misuse of AI models."
        if 'cyber' in tl:
            return "Investigates cyber threat actors, nation-state adversary tactics, and malicious cyber operations targeting AI systems."
        return "Conducts strategic threat intelligence research, threat modeling, and adversary investigation."
    if 'data center commissioning' in tl or 'commissioning' in tl:
        return "Oversees electrical, mechanical, and safety commissioning quality assurance across data center construction projects."
    if 'data center capacity delivery' in tl or 'capacity delivery' in tl:
        return "Oversees regional data center capacity delivery, contractor milestones, and infrastructure facility handoffs."
    if 'capacity deployment lead' in tl or 'compute capacity' in tl:
        return "Coordinates compute fleet deployment operations, infrastructure capacity handoffs, and resource optimization."
    if 'data center operations coordinator' in tl or 'data center manager' in tl:
        return "Coordinates data center facilities maintenance, equipment break-fix logistics, and operational ticket resolution."
    if 'strategic sourcing lead - construction' in tl or 'development project manager, data center' in tl or 'expansion pmo' in tl or 'design management' in tl:
        return "Manages strategic data center construction programs, design delivery milestones, and capital project execution."
    if 'transaction manager' in tl or 'transaction principal' in tl:
        return "Executes commercial lease negotiations, real estate acquisitions, and transaction structuring for data center sites."
    if 'acquisitions and development' in tl:
        return "Directs site acquisitions, land entitlement processes, and real estate development for data center infrastructure."
    if 'debt capital' in tl or 'capital markets' in tl:
        return "Structures and executes debt capital transactions, credit facilities, and liquidity strategy to fund compute expansion."
    if 'order-to-cash' in tl or 'revenue assurance' in tl:
        return "Oversees global order-to-cash processes, customer revenue assurance controls, and enterprise billing integrity."
    if 'travel & expense' in tl:
        return "Directs global corporate travel policies, expense management operations, and corporate card program compliance."
    if 'vendor admin' in tl:
        return "Administers vendor master data governance, supplier onboarding workflows, and global accounts payable controls."
    if 'accounts receivable' in tl:
        return "Manages enterprise customer invoicing, receivables collections, and cash application accounting workflows."
    if 'financial reporting' in tl or 'gbs financial' in tl:
        return "Directs corporate financial reporting, statutory consolidations, and shared services accounting operations."
    if 'portfolio & investment' in tl or 'financial portfolio' in tl or 'borrower advocate' in tl:
        return "Manages loan portfolio performance tracking, mortgage servicing operations, and borrower resolution workflows."
    if 'pricing' in tl:
        return "Designs enterprise deal pricing structures, financial margin models, and commercial discounting frameworks."
    if 'risk & insurance' in tl or 'insurance' in tl:
        return "Manages corporate insurance policies, risk transfer programs, and commercial balance sheet protections."
    if 'ehs' in tl:
        return "Manages environmental health, occupational safety compliance, and operational EHS standards across data centers."
    if 'technical training' in tl or 'technical instructor' in tl or 'education specialist' in tl or 'training specialist' in tl:
        return "Designs technical training curricula, instructional materials, and customer enablement education programs."
    if 'gtm' in tl or 'growth strategy' in tl or 'revenue strategy' in tl:
        return "Drives go-to-market operational planning, sales territory strategy, and business execution cadences."
    if 'reseller' in tl or 'resale' in tl:
        return "Manages international reseller partner programs, channel distribution operations, and commercial partner enablement."
    if 'commercial activation' in tl or 'strategic pursuits' in tl or 'strategic deals' in tl:
        return "Leads strategic enterprise commercial agreements, deal orchestration, and delivery partner activation."
    if 'investor relations' in tl:
        return "Directs investor communications, quarterly earnings preparation, and strategic shareholder relationships."
    if 'national security' in tl or 'international affairs' in tl or 'public sector' in tl:
        return "Directs government relations, public sector policy engagements, and national security regulatory partnerships."
    if 'podcast' in tl or 'media manager' in tl:
        return "Manages podcast brand sponsorships, digital audio media partnerships, and public storytelling initiatives."
    if 'analyst relations' in tl:
        return "Directs industry analyst relations strategy, product briefings, and competitive market positioning."
    if 'web design manager' in tl or 'web & inbound' in tl:
        return "Manages web design strategy, digital brand user experiences, and inbound digital conversion initiatives."
    if 'contributor experience' in tl or 'community' in tl:
        return "Builds contributor community programs, feedback mechanisms, and engagement operations for AI training networks."
    if 'research associate, biology' in tl or 'research operations lead, biology' in tl:
        return "Coordinates laboratory research operations, wet-lab protocols, and experimental workflows in computational biology."
    if 'biological safety' in tl:
        return "Manages biological safety policy programs, bio-risk evaluations, and laboratory safety compliance frameworks."
    if 'research operations, external artifacts' in tl:
        return "Manages technical publication workflows, system cards, and scientific research artifact releases."
    if 'open benchmarks grants' in tl:
        return "Directs grant program administration, application review cadences, and research milestone tracking for open AI benchmarks."
    if 'human frontier collective' in tl:
        return "Provides domain advisory expertise, expert consensus workflows, and non-technical governance for AI evaluation."
    if 'technical deployment' in tl or 'deployment lead' in tl:
        return "Manages technical customer onboarding timelines, statements of work, and project delivery roadmaps."
    if 'quality operations' in tl or 'subject matter expert' in tl:
        return "Oversees data annotation quality standards, expert review calibration, and operational evaluation benchmarks."
    if 'head of strategic startups' in tl or 'head of asean' in tl or 'head of southern europe' in tl:
        return "Directs commercial market expansion, regional go-to-market teams, and executive customer relationships."
    if 'tabletop exercise' in tl:
        return "Designs and facilitates crisis simulation tabletop exercises evaluating frontier AI societal risks and governance responses."
    if 'infrastructure capacity planner' in tl or 'network capacity' in tl:
        return "Models multi-year compute and networking infrastructure capacity forecasts, hardware demand curves, and supply commitments."
    if 'bi analyst' in tl or 'data analyst' in tl:
        return "Builds business intelligence dashboards, commercial data models, and analytical reports supporting strategic decisions."
    if 'cx ops' in tl:
        return "Manages customer experience operations, billing dispute resolution, and frontline support queue workflows."
    if 'director of product' in tl or 'principal pm' in tl or 'product strategy principal' in tl:
        return "Guides commercial product strategy, competitive market intelligence, and product portfolio roadmaps."
    if 'director, product security' in tl:
        return "Directs product security strategy, application security governance, and vulnerability management programs."
    if 'security technology deployment' in tl or 'platform hardware security' in tl or 'continuous monitoring' in tl:
        return "Manages physical security system installations, hardware access controls, and infrastructure compliance monitoring."
    if 'senior director of it' in tl:
        return "Directs enterprise IT infrastructure, end-user technology services, corporate systems, and IT security operations."
    if 'vp, research' in tl or 'research manager' in tl:
        return "Leads research operational planning, scientific team governance, and machine learning research delivery."
    if 'head of growth' in tl or 'growth marketer' in tl:
        return "Develops growth acquisition strategies, enterprise search visibility initiatives, and experimentation roadmaps."
    if 'operations manager - supply' in tl or 'inventory control' in tl:
        return "Manages operational supply forecasting, physical hardware inventory audits, and logistics tracking."
    if 'program director' in tl or 'technical project manager' in tl or 'special projects' in tl or 'strategic delivery' in tl:
        return "Directs complex multi-phase enterprise transformation programs, operational project delivery, and milestone execution."
    if 'customer strategy director' in tl or 'ai success manager' in tl:
        return "Advises executive clients on AI transformation roadmaps, organizational adoption, and customer value realization."
    if 'team manager' in tl:
        return "Manages frontline operational teams, daily performance metrics, and workflow execution quality."
    if 'frontier data lead' in tl:
        return "Directs customer data delivery programs, statement of work milestones, and account expansion operations."
    if 'solution specialist' in tl or 'solutions specialist' in tl:
        return "Provides technical pre-sales solution expertise, customer architecture demonstrations, and workload sizing."
    if 'senior manager, managed databases' in tl or 'field engineering' in tl:
        return "Directs technical field engineering teams, database infrastructure operations, and customer solution delivery."

    return "Coordinates cross-functional business operations, program delivery, and operational planning cadences."

test_reasons = [get_155_reason(r) for r in biz_records]
counts = Counter(test_reasons)
print(f"\nDistinct reasons generated for 155: {len(counts)}")
print("Distribution:")
for r_text, c in counts.most_common():
    print(f"{c:2d}x: {r_text}")
