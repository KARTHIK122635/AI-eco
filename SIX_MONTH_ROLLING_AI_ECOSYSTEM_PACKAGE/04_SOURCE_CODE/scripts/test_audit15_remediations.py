import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {json.loads(line)['content']['data']['jobId']: json.loads(line)['content']['data'] for line in f}

remediations = {
    # 1. Scale Engagement Managers (5 listings)
    'job_cf830bd9939b555e': (
        'Oversee onboarding and successful implementation of customer accounts',
        'REPLACED',
        'Replaced introductory/promotional company overview ("Scale AI is at the forefront...") with exact verbatim customer onboarding responsibility bullet from You Will section.'
    ),
    'job_d28e40a44928956a': (
        'Oversee onboarding and successful implementation of customer accounts',
        'REPLACED',
        'Replaced introductory/promotional company overview ("Scale AI is at the forefront...") with exact verbatim customer onboarding responsibility bullet from You Will section.'
    ),
    'job_f724f26481fd28a7': (
        'Oversee onboarding and successful implementation of customer accounts',
        'REPLACED',
        'Replaced introductory/promotional company overview ("Scale AI is at the forefront...") with exact verbatim customer onboarding responsibility bullet from You Will section.'
    ),
    'job_ac9cb76ba1d920bd': (
        'Oversee onboarding and successful implementation of customer accounts',
        'REPLACED',
        'Replaced introductory/promotional company overview ("Scale AI is at the forefront...") with exact verbatim customer onboarding responsibility bullet from You Will section.'
    ),
    'job_a94a61fdf09a6a38': (
        'Oversee onboarding and successful implementation of customer accounts',
        'REPLACED',
        'Replaced introductory/promotional company overview ("Scale AI is at the forefront...") with exact verbatim customer onboarding responsibility bullet from You Will section.'
    ),

    # 2. Scale Subcontracts Manager
    'job_011867a56e3a13b5': (
        'Own day-to-day relationships with subcontractors supporting large Public Sector programs, including major defense primes and specialized technical partners Understand Scale’s overall technical solution and ensure each subcontractor clearly understands how its scope, interfaces, and deliverables fit into that solution Translate prime contract milestones and program requirements into clear subcontractor deliverables, timelines, dependencies, and acceptance criteria',
        'REPLACED',
        'Replaced company promotional statement ("Scale AI is at the forefront...") with exact verbatim subcontractor delivery and program governance duties from You Will section.'
    ),

    # 3. Scale Applied AI Engineers (3 listings)
    'job_d937a79251d4723a': (
        'Own the AI layer of production systems for public sector clients, including agents, model integration, and the backend services they run on Build production agents from established architectural patterns, with reliable tool calling, guardrails, and observability',
        'REPLACED',
        'Replaced team overview ("Scale\'s Global Public Sector team is focused on using AI...") with concrete production agent engineering responsibilities from What You\'ll Do.'
    ),
    'job_fe54132e071496e6': (
        'Own the AI layer of production systems for public sector clients, including agents, model integration, and the backend services they run on Build production agents from established architectural patterns, with reliable tool calling, guardrails, and observability',
        'REPLACED',
        'Replaced team overview ("Scale\'s Global Public Sector team is focused on using AI...") with concrete production agent engineering responsibilities from What You\'ll Do.'
    ),
    'job_98be80cbc2ea655c': (
        'Define standards for responsible AI, model governance, and production MLOps that get adopted broadly across the Global Public Sector team Build or validate the highest-risk parts of strategic AI systems and use those systems to establish standards other teams can adopt.',
        'REPLACED',
        'Replaced team overview ("Scale\'s Global Public Sector team is focused on using AI...") with concrete production MLOps and governance responsibilities from What You\'ll Do.'
    ),

    # 4. WPP Media SVP Data Science Lead
    'job_a2d39f78a759c157': (
        'Provide expert oversight across statistical modelling, econometrics, machine learning, AI, forecasting, optimisation, attribution, propensity modelling and experimentation, ensuring methodologies are robust, explainable, reproducible and appropriate to the business problem',
        'REPLACED',
        'Replaced company introductory branding ("About WPP Media WPP is the trusted growth partner...") with exact verbatim technical leadership responsibilities across ML, statistical modelling, and AI algorithms.'
    ),

    # 5. Scale STEM & SWE Fellows (Human Frontier Collective)
    'job_21e78cd8d02add0c': (
        'Design complex, domain-specific problems and datasets to rigorously evaluate AI models, and provide expert insights that enhance their accuracy, reasoning, and overall performance',
        'REPLACED',
        'Replaced program invitation ("Collaborative Work: Get invited...") with exact verbatim evaluation and domain dataset design duty statement.'
    ),
    'job_91fd8017f05b1d94': (
        'Design complex, domain-specific problems and datasets to rigorously evaluate AI models, and provide expert insights that enhance their accuracy, reasoning, and overall performance',
        'REPLACED',
        'Replaced program invitation ("Collaborative Work: Get invited...") with exact verbatim evaluation and domain dataset design duty statement.'
    ),
    'job_f3d068e4db415d90': (
        'Design complex, domain-specific problems and datasets to rigorously evaluate AI models, and provide expert insights that enhance their accuracy, reasoning, and overall performance',
        'REPLACED',
        'Replaced program invitation ("Collaborative Work: Get invited...") with exact verbatim evaluation and domain dataset design duty statement.'
    ),
    'job_3286c737ec6d7b38': (
        'Design complex, domain-specific problems and datasets to rigorously evaluate AI models, and provide expert insights that enhance their accuracy, reasoning, and overall performance',
        'REPLACED',
        'Replaced program invitation ("Collaborative Work: Get invited...") with exact verbatim evaluation and domain dataset design duty statement.'
    ),

    # 6. Scale ML Fellows & STEM Fellow (HFC)
    'job_54c421f13430cbf9': (
        'building AI safety and policy guardrails, helping models understand real-world deep learning workflows by designing, reviewing, and optimizing PyTorch models, evaluating complex ML code and AI-generated implementations for efficiency and correctness, and more.',
        'REPLACED',
        'Replaced recruitment criteria heading ("Who should apply Background : PhD...") with exact verbatim model optimization, PyTorch review, and evaluation project duties.'
    ),
    'job_6235766d8986181c': (
        'building AI safety and policy guardrails, helping models understand real-world deep learning workflows by designing, reviewing, and optimizing PyTorch models, evaluating complex ML code and AI-generated implementations for efficiency and correctness, and more.',
        'REPLACED',
        'Replaced recruitment criteria heading ("Who should apply Background : PhD...") with exact verbatim model optimization, PyTorch review, and evaluation project duties.'
    ),
    'job_8ee1224407ba5ba6': (
        'building AI safety and policy guardrails, helping models understand real-world deep learning workflows by designing, reviewing, and optimizing PyTorch models, evaluating complex ML code and AI-generated implementations for efficiency and correctness, and more.',
        'REPLACED',
        'Replaced recruitment criteria heading ("Who should apply Background : PhD...") with exact verbatim model optimization, PyTorch review, and evaluation project duties.'
    ),
    'job_105421a2eaf7d737': (
        'building AI safety and policy guardrails, helping models understand real-world deep learning workflows by designing, reviewing, and optimizing PyTorch models, evaluating complex ML code and AI-generated implementations for efficiency and correctness, and more.',
        'REPLACED',
        'Replaced recruitment criteria heading ("Who should apply Background: PhDs...") with exact verbatim model optimization, PyTorch review, and evaluation project duties.'
    ),

    # 7. Databricks AI Forward Deployed Engineers (5 listings)
    'job_67f7c6003e024de0': (
        'We deliver professional services engagements to help our customers build and productionize first-of-its-kind AI applications.',
        'REPLACED',
        'Replaced remote applicant welcome notice ("We welcome remote applicants located near our offices...") with exact verbatim customer production engagement duty statement.'
    ),
    'job_a21c829d51c3a7c7': (
        'We deliver professional services engagements to help our customers build and productionize first-of-its-kind AI applications.',
        'REPLACED',
        'Replaced remote applicant welcome notice ("We welcome remote applicants located near our offices...") with exact verbatim customer production engagement duty statement.'
    ),
    'job_807e6632f0af6e22': (
        'We deliver professional services engagements to help our customers build and productionize first-of-its-kind AI applications.',
        'REPLACED',
        'Replaced remote applicant welcome notice ("We welcome remote applicants located near our offices...") with exact verbatim customer production engagement duty statement.'
    ),
    'job_0cb38f99c8da449a': (
        'We deliver professional services engagements to help our customers build and productionize first-of-its-kind AI applications.',
        'REPLACED',
        'Replaced remote applicant welcome notice ("We welcome remote applicants located near our offices...") with exact verbatim customer production engagement duty statement.'
    ),
    'job_22abb2ef0edc96eb': (
        'We deliver professional services engagements to help our customers build and productionize first-of-its-kind AI applications.',
        'REPLACED',
        'Replaced remote applicant welcome notice ("We welcome remote applicants located near our offices...") with exact verbatim customer production engagement duty statement.'
    ),

    # 8. Databricks Systems PhD (2 listings)
    'job_22b89547b209fb71': (
        'design and implement in many areas that leapfrog existing state-of-the-art systems: Query compilation & optimization Distributed query execution and scheduling Vectorized engine execution Data security Resource Management Transaction coordination Efficient storage structures (encoding, indexes) Automatic physical data optimization',
        'REPLACED',
        'Replaced company vision intro ("To make it happen we’re building multi-cloud systems...") with exact verbatim database engine design and query optimization responsibilities.'
    ),
    'job_5f568e00d9abdc89': (
        'design and implement in many areas that leapfrog existing state-of-the-art systems: Query compilation & optimization Distributed query execution and scheduling Vectorized engine execution Data security Resource Management Transaction coordination Efficient storage structures (encoding, indexes) Automatic physical data optimization',
        'REPLACED',
        'Replaced company vision intro ("To make it happen we’re building multi-cloud systems...") with exact verbatim database engine design and query optimization responsibilities.'
    ),

    # 9. Databricks AI Gateway
    'job_53a205e783412830': (
        'Build the routing layer that picks the right model for each request across quality, cost, latency, availability, and remaining budget Improve reliability, latency, and efficiency of distributed AI workloads',
        'REPLACED',
        'Replaced company intro ("Founded by engineers, and customer obsessed...") with exact verbatim routing and API optimization duties from The Impact You Will Have.'
    ),

    # 10. Databricks FDE Managers (2 listings)
    'job_532de8f1c617312b': (
        'Oversee regional performance targets, including billable utilisation, team growth, and hiring, while championing delivery excellence and customer success across the FDE portfolio.',
        'REPLACED',
        'Replaced intro ("at the forefront of this transformation") with exact verbatim regional delivery excellence and customer success management duty statement.'
    ),
    'job_0dce34dafe76db5b': (
        'Drive regional performance targets—including billable utilisation, team growth, and hiring—while championing delivery excellence and customer success across the ANZ FDE portfolio',
        'REPLACED',
        'Replaced intro ("at the forefront of this transformation") with exact verbatim regional delivery excellence and team management duty statement.'
    ),

    # 11. CoreWeave Product Strategy Lead
    'job_76d112469d687bb9': (
        'Collaborating closely with product and engineering teams, you will guide the portfolio strategy to align different product areas to a common strategy, maintaining a balance between cutting-edge technology, user-friendliness, and market viability.',
        'REPLACED',
        'Replaced introductory opening ("we are seeking a Product Strategy Lead...") with exact verbatim portfolio strategy and product alignment duty statement from About the Role.'
    ),

    # 12. Anthropic Discovery Team
    'job_8dc41f7d1812076d': (
        'Develop approaches to address long-horizon task completion and complex reasoning challenges essential for scientific discovery Scaling research ideas from prototype to production Create benchmarks and evaluation frameworks to measure model capabilities in scientific workflows and computer use Implement distributed training systems and performance optimizations to support large-scale model development',
        'REPLACED',
        'Replaced team overview ("Currently the team is focused on...") with exact verbatim model training, benchmarking, and optimization responsibilities.'
    ),

    # 13. Anthropic Computational Biology
    'job_4d99a9d1ea3bffb4': (
        'Build, run, and maintain the analysis pipelines that back the team\'s experimental programs: sequence analysis at petabyte scale, structural bioinformatics, phylogenetic and comparative genomics, design and analysis of high-throughput functional screens, biological sequence modeling, etc.',
        'REPLACED',
        'Replaced promotional positioning ("positioning Anthropic at the forefront...") with exact verbatim computational pipeline engineering and genomic analysis responsibilities.'
    ),

    # 14. Vesoma Robotics Technician
    'job_68fc708b1be009aa': (
        'Run day-to-day operation and maintenance of a humanoid robot: mechanical assembly and disassembly, harness work, fault diagnosis, keeping the machine available for development and demos.',
        'REPLACED',
        'Replaced company founding history ("Founded by entrepreneurs...") with exact verbatim robot mechanical assembly, wiring harness, and diagnostic maintenance duties from Your Mission.'
    ),

    # 15. Remanence MTS Platform & Infra (2 listings)
    'job_692c453001241683': (
        'You’ll build the platform that brings our research into production, making Remanence easy to deploy and operate in customer clouds and on-premises.',
        'REPLACED',
        'Eliminated prepended promotional recruiting phrase ("We\'re building the most talent-dense AI team in Europe...") and retained exact verbatim platform production deployment duty.'
    ),
    'job_ae42444b365c6fd0': (
        'You’ll own the compute and execution platform supporting training, inference, task generation, and evaluation.',
        'REPLACED',
        'Eliminated prepended promotional recruiting phrase ("We’re building the most talent-dense AI team in Europe...") and retained exact verbatim compute orchestration platform duty.'
    ),

    # 16. Cresta Roles (4 listings)
    'job_25e3f7e51aa90718': (
        'Act as a consultative partner to customers—uncovering business objectives, technical environments, and operational challenges to map them to AI-driven solutions.',
        'REPLACED',
        'Replaced promotional opening ("you’ll be at the forefront of the AI transformation...") with exact verbatim customer solutions architecture responsibility bullet.'
    ),
    'job_2a9e9de2ae132ef2': (
        'Work with Cresta product and engineering teams, build and continuously improve the Cresta platform and new product requirements. Stay closely with customers and their requirements, analyze the technical tradeoffs, own the customer facing deliverables. Develop high quality, well designed, reusable, and well-tested system components, and contribute to the overall system designs.',
        'REPLACED',
        'Replaced team overview ("The Platform Frontend team is focused on...") with exact verbatim system design and component engineering responsibilities from Responsibilities section.'
    ),
    'job_32374717e76f356b': (
        'Work with Cresta product and engineering teams, build and continuously improve the Cresta platform and new product requirements. Stay closely with customers and their requirements, analyze the technical tradeoffs, own the customer facing deliverables. Develop high quality, well designed, reusable, and well-tested system components, and contribute to the overall system designs.',
        'REPLACED',
        'Replaced team overview ("The Platform Frontend team is focused on...") with exact verbatim system design and component engineering responsibilities from Responsibilities section.'
    ),
    'job_509fdfe033e3db16': (
        'Work with Cresta product and engineering teams, build and continuously improve the Cresta platform and new product requirements. Stay closely with customers and their requirements, analyze the technical tradeoffs, own the customer facing deliverables.',
        'REPLACED',
        'Replaced team overview ("The Platform team is focused on...") with exact verbatim native platform engineering responsibilities from Responsibilities section.'
    ),

    # 17. CoreWeave Data Center Commissioning/Quality Manager
    'job_84c88005f767d607': (
        'You will oversee the installation and testing of components and systems, including mission-critical systems such as generators, UPS systems, electrical distribution equipment, and redundancy protocols, as well as cooling systems such as chillers and CDUs.',
        'REPLACED',
        'Replaced excerpt starting with "Keep safety at the forefront..." with exact verbatim electrical, mechanical, and cooling commissioning quality assurance duty statement.'
    ),

    # 18. Anthropic Revenue Accounting
    'job_cf38eef2a2000eb3': (
        'Manage daily revenue accounting operations, including high-volume transaction processing, and ensure accurate revenue recognition in compliance with ASC 606',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim ASC 606 revenue recognition duty bullet from Responsibilities section.'
    ),

    # 19. Anthropic Deal Strategy / Deal Velocity (4 listings)
    'job_5775c24772fb2121': (
        'Financial Analysis : Conduct growth and margin analysis, discount impact assessment, and deal profitability modeling to support data-driven decision making',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim margin and pricing analysis responsibility bullet from Responsibilities section.'
    ),
    'job_a1f6d34afbcae1d9': (
        'Financial Analysis: Conduct growth and margin analysis, discount impact assessment, and deal profitability modeling to support data-driven decision making',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim margin and pricing analysis responsibility bullet from Responsibilities section.'
    ),
    'job_c906cdf09836f33d': (
        'Financial Analysis: Conduct growth and margin analysis, discount impact assessment, and deal profitability modeling to support data-driven decision making',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim margin and pricing analysis responsibility bullet from Responsibilities section.'
    ),
    'job_68f457a1316cf9d3': (
        'Quarterback deals through internal processes — CPQ quote-building, approval routing, contract execution — ensuring accurate, timely completion',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim margin and pricing analysis responsibility bullet from Responsibilities section.'
    ),

    # 20. Anthropic Safeguards Enforcement Analyst
    'job_6dea5a27dc7187e6': (
        'You will enforce our Usage Policy with a specific focus on detecting and mitigating bio risks, investigating potential violations, and help continuously strengthen our safeguards.',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim Usage Policy enforcement and bio risk investigation duty statement from About the Role.'
    ),

    # 21. Scale Enterprise AI Development Strategist
    'job_31186971b3277e47': (
        'Own outbound prospecting and customer engagement through Stage 2 qualification Drive customer outreach and education during the M1 phase of the sales process',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim pipeline qualification and platform education responsibilities from In This Role, You Will.'
    ),

    # 22. Scale ML Research Engineer General Agents
    'job_548f6ee384b89cb0': (
        'Design and implement end-to-end agent systems that combine LLM reasoning, tool use, memory, and control logic to solve recurring enterprise use cases.',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim agent system design and tool-use implementation responsibility bullet from You Will.'
    ),

    # 23. Cresta EMEA Marketing Manager
    'job_46455a37c5130d97': (
        'In partnership with the VP of International Marketing, develop and execute Cresta’s EMEA marketing strategy aligned to both regional pipeline and CARR goals and global marketing priorities Translate global campaigns and product launches into effective regional execution plans',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim regional marketing strategy and campaign execution duty bullets from Responsibilities.'
    ),

    # 24. CoreWeave Operations Accounting - Inventory Manager
    'job_779f5863550149fd': (
        'The Inventory Manager will be responsible for supporting the ongoing development, management and administration of our global inventory accounting operations activities. In this role, you will be responsible to support our data center inventory control specialists and data center operations leaders while maintaining proper financial reporting and controls.',
        'REPLACED',
        'Replaced excerpt containing "play a critical role" with exact verbatim global inventory accounting operations and financial reporting controls duty statement from What You\'ll Do.'
    ),
}

print(f"Total remediations configured: {len(remediations)}")

failed = []
for jid, (new_ev, status, rationale) in remediations.items():
    if jid not in jobs:
        failed.append((jid, "Job ID not found in canonical data"))
        continue
    jd = jobs[jid]['jobDescription']
    if new_ev not in jd:
        failed.append((jid, f"New evidence is NOT an exact substring:\n{new_ev[:80]}..."))

if failed:
    print(f"FAILED: {len(failed)} errors:")
    for f in failed:
        print(f"  {f[0]}: {f[1]}")
else:
    print("SUCCESS: ALL 100% of candidate replacements are EXACT VERBATIM SUBSTRINGS of their source jobDescription!")
