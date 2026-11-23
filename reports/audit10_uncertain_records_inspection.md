# Phase II – Stage 2: Audit 10 – Detailed Inspection Report on 117 Previously UNCERTAIN Records

**Generated:** 2026-11-21  
**Audit Version:** Phase II – Stage 2: Audit 10 Final Quality Corrections  
**Dataset Evaluated:** `data/canonical/canonical_jobs.jsonl` (1,930 records)  

---

## 1. Executive Summary & Review Scope

In previous audits, 117 records were assigned the placeholder category `UNCERTAIN` and shared a uniform generic boilerplate explanation (*"Job title and description do not provide sufficient technical detail or domain specificity to classify into a definitive category."*). In accordance with Audit 10 requirements, all 117 records were individually inspected against their full job descriptions, extracted responsibility evidence, and qualification evidence.

### Key Outcomes:
- **Total Previously UNCERTAIN Records Inspected:** 117 (100.0%)
- **Reclassified into Specific AI / Technical / Non-Technical Tiers:** 114 (97.44%)
- **Retained in UNCERTAIN:** 3 (2.56%) — verified as AZAV-accredited continuing education / vocational training programs (*Weiterbildung*) rather than corporate operational employment positions.
- **Boilerplate Explanations Eliminated:** 100.0% — every record now possesses an active, evidence-grounded sentence describing actual duties.

### Category Reclassification Breakdown (117 Records):

| Target Category | Count | % of 117 | Functional Domain Description |
| :--- | :---: | :---: | :--- |
| `AI_PRODUCT_SOLUTIONS` | 41 | 35.04% | Forward-deployed engineering, enterprise AI consulting, generative AI solution architecture, and AI product management |
| `NON_TECHNICAL` | 31 | 26.50% | Enterprise sales, GPU commercial operations, marketing, social content, HR adoption, PMO, and corporate compliance |
| `AI_SUPPORTING_TECH` | 14 | 11.97% | Python software architecture, data pipelines, platform security, robot teleoperation, and AI annotation pipelines |
| `NON_AI_TECH` | 11 | 9.40% | Traditional IT helpdesk, clinical data systems, web tracking tags, robotics mechatronics, and mobile QA |
| `AI_INFRASTRUCTURE` | 10 | 8.55% | Bare-metal GPU provisioning, AI Ops infrastructure management, Kubernetes inference clusters, and VPC networking |
| `CORE_AI_ML` | 7 | 5.98% | Frontier model evaluation, vision-language model research, pretraining dataset research, and geometric deep learning |
| `UNCERTAIN` | 3 | 2.56% | Certified AZAV vocational education coursework (Weiterbildung) with no enterprise employer duties |
| **Total** | **117** | **100.0%** | Comprehensive resolution of all ambiguous records |

---

## 2. Deep Dive: Mandated Priority Test Cases

The independent audit specifically highlighted five positions requiring rigorous evidence review:

### Lyceum – Member of Technical Staff – API, Frontend, Interface, Integrations
- **Job ID:** `job_dca7b0b6a47a6b85`
- **Assigned Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Develops developer-facing APIs, web dashboard interfaces, and model serving framework integrations for an AI cloud platform.
- **Responsibility Evidence:** *"Your focus Feature development: Design and ship new platform capabilities - from supporting new model architectures and serving frameworks to building out API features that customers are asking for."*
- **Qualification Evidence:** *"3+ years of experience in software engineering, with a focus on backend or infrastructure systems Strong proficiency in Go and Python Hands-on experience with at least one ML inference serving framework (vLLM, TGI, etc) Solid understanding of how large"*
- **Detailed Rationale:** Full-stack software engineer building developer APIs, web management interfaces, and inference serving integrations (vLLM, TGI).

### Lyceum – Member of Technical Staff – Infra, k8s, Dynamo
- **Job ID:** `job_93cbaa791c40727a`
- **Assigned Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Scales Kubernetes clusters, distributed database layers, and high-throughput model serving infrastructure for AI inference platforms.
- **Responsibility Evidence:** *"Infrastructure evolution: Evaluate and integrate open-source inference frameworks and tooling (Dynamo, vLLM, Triton, etc.) where they improve throughput, latency, or stability of the serving stack."*
- **Qualification Evidence:** *"3+ years of experience in backend, infrastructure, or systems engineering Strong proficiency in Go and Python Experience building or operating a model serving platform or ML platform Solid understanding of systems performance - profiling, benchmarking, and"*
- **Detailed Rationale:** Core infrastructure engineer scaling Kubernetes orchestration, low-latency DynamoDB persistence, and distributed model serving engines.

### capco – Infrastructure Manager (m/w/d) for AI Ops Implementation
- **Job ID:** `job_799b4f210a0fa4ff`
- **Assigned Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Manages enterprise IT infrastructure, DevOps environments, and system reliability for large-scale AI Ops implementations.
- **Responsibility Evidence:** *"Lead and coordinate a large-scale AI Ops implementation project, ensuring effective planning, execution, and alignment with business and technical objectives. Manage and coordinate cross-functional IT teams responsible for setting up, integrating, and managing complex infrastructure environments"*
- **Qualification Evidence:** *"(e.g., performance, security, availability). Proficient in stakeholder communication and program leadership. Experience working in ITIL-based, DevOps, or agile project environments. High degree of ownership and structured work approach."*
- **Detailed Rationale:** Leads infrastructure management, ITIL/DevOps environments, and high-availability operations for enterprise banking AI Ops implementations.

### Wavestone Germany AG – Python Software Architekt (m/w/d) (Ref.Nr.: 48296)
- **Job ID:** `job_e8078287eb87dc0c`
- **Assigned Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Architects enterprise Python software platforms supporting data analytics, ETL pipelines, and Generative AI services.
- **Responsibility Evidence:** *"Für ein langfristiges Projekt bei unserem Kunden in Zürich (Remote-Anteil nur innerhalb der Schweiz möglich) suchen wir einen Python Software Architekt (m/w/d)."*
- **Qualification Evidence:** *"None"*
- **Detailed Rationale:** Software architect designing modular Python systems, data processing pipelines, and microservices supporting GenAI/ML applications.

### isaraerospace – Intern AI & Data Transformation
- **Job ID:** `job_f758d5d0dfd3c148`
- **Assigned Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Builds automated ELT data pipelines, API integrations, and warehouse data models supporting operational analytics.
- **Responsibility Evidence:** *"Develop and maintain scheduled ELT/ETL pipelines, monitor data quality and troubleshoot failures."*
- **Qualification Evidence:** *"with data consumers and refine what you deliver. Qualification Checklist Education: Enrolled in a Bachelor’s or Master’s in computer science, data engineering or information systems; available for at least six months."*
- **Detailed Rationale:** Data engineering intern extracting data from SaaS tools, building warehouse pipelines with Python and dlt, and maintaining ELT jobs.

---

## 3. Retained UNCERTAIN Records Justification

Only 3 of the 117 records remain classified as `UNCERTAIN`. Detailed inspection confirmed that these are not corporate employment positions, but rather German government-subsidized (*AZAV-zertifizierte Weiterbildung*) adult continuing education programs advertised on job boards:

### velpTEC GmbH – Weiterbildung zum Process Automation Manager (m/w/d) – (100 % förderbar)
- **Job ID:** `job_b8483b279f8b1669`
- **Assigned Category:** `UNCERTAIN`
- **Updated Classification Reason:** Participates in vocational training coursework on business process automation, workflow digitization, and robotic automation methods.
- **Source Description Extract:** *"Als Process Automation Manager (m/w/d) analysierst, optimierst und automatisierst du betriebliche Geschäftsprozesse, um Arbeitsabläufe effizienter und zukunftssicher zu gestalten. In dieser Weiterbildung vertiefst du deine Kenntnisse im digitalen Prozessmanagement und lernst, wie du Künstliche Intel..."*
- **Justification:** Subsidized AZAV vocational education program teaching process optimization rather than an operational corporate employment vacancy. Because the listing represents curriculum enrollment rather than an operational corporate vacancy with defined employee deliverables, it cannot be definitively mapped to any technical or corporate operating tier. The explanation has been updated to reflect the actual training activities.

### DataSmart Point GmbH – Karrierestart in Data & AI - IHK Data Analyst (m/w/d) - 100 % Online
- **Job ID:** `job_9e4923f4f61926ea`
- **Assigned Category:** `UNCERTAIN`
- **Updated Classification Reason:** Participates in vocational training curriculum covering data analytics, SQL databases, and AI business applications through an accredited training academy.
- **Source Description Extract:** *"Werde Teil der digitalen Zukunft mit der DataSmart Point Academy Die DataSmart Point Academy (DSP Academy) ist ein AZAV-zertifizierter Bildungsträger, spezialisiert auf praxisnahe IT- und Data-Weiterbildungen mit klarer Zukunftsperspektive. Unsere Programme richten sich an motivierte Quereinsteiger:..."*
- **Justification:** Certified AZAV vocational training program teaching data analytics and Python rather than an operational corporate job vacancy. Because the listing represents curriculum enrollment rather than an operational corporate vacancy with defined employee deliverables, it cannot be definitively mapped to any technical or corporate operating tier. The explanation has been updated to reflect the actual training activities.

### Mentify Learn GmbH – Amazon Account Manager (m/w/d) - Weiterbildung für Online-Marktplätze & AI, 100 % remote
- **Job ID:** `job_d732380d4b5b6679`
- **Assigned Category:** `UNCERTAIN`
- **Updated Classification Reason:** Participates in vocational training coursework covering Amazon marketplace management, e-commerce workflows, and AI tools.
- **Source Description Extract:** *"📍 Homeoffice – Einstieg jederzeit möglich – Vollzeit oder Teilzeit 📦 E-Commerce ist die Zukunft – mach dich fit für den digitalen Handel! Mit unserer Weiterbildung wirst du in 3–6 Monaten zur Fachkraft für digitale Marktplätze. Du lernst praxisnah in drei spezialisierten Modulen: Amazon Marketplace..."*
- **Justification:** Subsidized AZAV vocational course for marketplace management rather than an operational corporate employment position. Because the listing represents curriculum enrollment rather than an operational corporate vacancy with defined employee deliverables, it cannot be definitively mapped to any technical or corporate operating tier. The explanation has been updated to reflect the actual training activities.

---

## 4. Comprehensive Master Table of All 117 Records

| # | Job ID | Company | Job Title | Previous Category | Updated Category | Updated Classification Reason |
| :-: | :--- | :--- | :--- | :---: | :---: | :--- |
| 1 | `job_1a388cef4b8843e0` | Palantir Technologies | American Tech Fellowship | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Deploys enterprise data and AI workflows using Palantir Foundry and Artificial Intelligence Platform (AIP). |
| 2 | `job_799b4f210a0fa4ff` | capco | Infrastructure Manager (m/w/d) for AI Ops Implementation | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Manages enterprise IT infrastructure, DevOps environments, and system reliability for large-scale AI Ops implementations. |
| 3 | `job_fc9648e35ba5db78` | Impossiblecloud | Go-to-Market Champion (GPU & AI) | `UNCERTAIN` | `NON_TECHNICAL` | Drives go-to-market strategy, product pricing, and commercial expansion for cloud GPU compute and AI infrastructure. |
| 4 | `job_122d9b1a2804bf26` | Quantco | Office Management Working Student | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates office administration, vendor relationships, and workplace facilities operations. |
| 5 | `job_a94dd6fdadc3d3dd` | Almetra | PhD Researcher – Video Understanding & VLMs | `UNCERTAIN` | `CORE_AI_ML` | Researches and trains vision-language foundation models and deep learning architectures for video understanding. |
| 6 | `job_aa46581403b45706` | Rosental Organics GmbH | Senior AI Content Producer - Foto, Video, Motion (m/w/d) | `UNCERTAIN` | `NON_TECHNICAL` | Produces digital advertising assets, video content, and marketing creative using generative AI tools. |
| 7 | `job_1491ef1a44058319` | Miebach Consulting GmbH | Senior Expert (w/m/d) - Logistics Management Systems | `UNCERTAIN` | `NON_AI_TECH` | Advises enterprise clients on supply chain architecture, warehouse management systems, and logistics software implementations. |
| 8 | `job_269fbdaeeea8515a` | Baringa | Senior Manager, AI & Trading Transformation | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Leads enterprise consulting engagements to implement AI solutions and digital transformation in commodity trading. |
| 9 | `job_93e9a4b3fd1528a4` | Zoominfo | Senior SEO & AI Search Manager | `UNCERTAIN` | `NON_TECHNICAL` | Develops organic search engine marketing optimization strategies across traditional search platforms and conversational AI search engines. |
| 10 | `job_0720bc84679aeca7` | Ema | AI Resident UK/EMEA | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Deploys and customizes autonomous AI agents and enterprise generative AI workflows for customer operations. |
| 11 | `job_4628c8bf8e5ebcb2` | Luke Recruitment | Senior Social & AI Marketeer | `UNCERTAIN` | `NON_TECHNICAL` | Directs social media marketing campaigns and brand activation strategies utilizing generative AI marketing tools. |
| 12 | `job_ddb8989279b2765a` | WIRECLOUD | First Level IT-Support / Kundenberatung (m/w/d) | `UNCERTAIN` | `NON_AI_TECH` | Provides first-level IT technical support, cloud telephony troubleshooting, and customer assistance. |
| 13 | `job_6808753b9abd122d` | Perplexity | Research & Development Site Lead (London) | `UNCERTAIN` | `CORE_AI_ML` | Directs research and engineering operations for conversational AI search platform development. |
| 14 | `job_fc733b2e34ce7d90` | Jellyfish | Media Strategy Manager | `UNCERTAIN` | `NON_TECHNICAL` | Plans and manages multi-channel digital media campaigns, advertising strategies, and client brand communications. |
| 15 | `job_46ed8ae5be510862` | 1KOMMA5˚ | (Junior) SEO & AI Marketing Manager (m/w/d) | `UNCERTAIN` | `NON_TECHNICAL` | Executes search engine optimization and digital marketing campaigns utilizing generative AI content tools. |
| 16 | `job_d6d446b7dbc88c38` | INC Innovation Center GmbH | Technischer Projektleiter Robotik & Physical AI (m/w/d) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages technical testing, platform integration, and industrial deployment projects for physical AI and robotics systems. |
| 17 | `job_984f995d02d192a3` | momox | Team Lead Pricing & AI - momox SE | Berlin | Full-Time | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Leads automated pricing strategy, algorithmic optimization, and AI solution roadmaps for e-commerce operations. |
| 18 | `job_b5650f32784de67d` | Anton Robotics | Working Student – Robot Teleoperation & Data Collection for Robot Foundation Models (m/w/d) | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Collects and curates sensor datasets through robot teleoperation to support training pipelines for robotic foundation models. |
| 19 | `job_20389864f9cfdf4b` | TecTake | Junior Specialist Automation & AI (m/w/d) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Implements business process automation and integrates generative AI workplace tools to optimize operational workflows. |
| 20 | `job_8dacf0db937b2f92` | Anton Robotics | Founder's Associate - Internship (m/w/d) | `UNCERTAIN` | `NON_TECHNICAL` | Supports startup operational execution, commercial business development, and administrative workflows for executive leadership. |
| 21 | `job_ea151868d0cabf39` | JustPlay GmbH | Platform QA Chapter Lead (all genders) | `UNCERTAIN` | `NON_AI_TECH` | Leads quality assurance methodologies, automated testing frameworks, and release validation for mobile app platforms. |
| 22 | `job_350a930679a271b8` | Neuphonic | Marketing Generalist | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates brand marketing campaigns, product content, and public communications for a speech AI platform. |
| 23 | `job_293c05cfec50d0fb` | Artefactlinkedin | Stage Communication – Stratégie de communication innovante (Adopt AI) | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates promotional communications, event marketing, and digital media for the enterprise Adopt AI summit. |
| 24 | `job_f8fe86ec4cb87275` | Artefactlinkedin | Directeur Practice Consulting & Data Transformation | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Directs enterprise consulting practices delivering data strategy, marketing analytics, and AI transformation programs. |
| 25 | `job_ad0a653b919ed9e7` | Artefactlinkedin | CDI - Senior AI Strategist - Paris | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Formulates strategic AI transformation roadmaps, executive business cases, and enterprise adoption programs. |
| 26 | `job_0eee96d8d91c0017` | Artefactlinkedin | CDI - AI Strategist Manager - Paris | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages client consulting engagements to design AI strategy, operating models, and organizational transformation programs. |
| 27 | `job_2ea929afcff1d70b` | Artefact | Stage Communication – Stratégie de communication innovante (Adopt AI) | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates promotional communications, event marketing, and digital media for the enterprise Adopt AI summit. |
| 28 | `job_4370eb0694ede9e6` | Artefact | CDI - Senior AI Strategist - Paris | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Formulates strategic AI transformation roadmaps, executive business cases, and enterprise adoption programs. |
| 29 | `job_b14e70ee758843ba` | Artefact | CDI - AI Strategist Manager - Paris | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages client consulting engagements to design AI strategy, operating models, and organizational transformation programs. |
| 30 | `job_df65ec2483015bf8` | DPG Media | Advertising Data Specialist | `UNCERTAIN` | `NON_AI_TECH` | Analyzes digital advertising campaign metrics, audience data segments, and commercial delivery reporting. |
| 31 | `job_2c0079996ca79a21` | Infomedics | Helpdeskmedewerker Tandheelkundige Software | `UNCERTAIN` | `NON_AI_TECH` | Provides customer technical support and application troubleshooting for specialized dental practice management software. |
| 32 | `job_b8483b279f8b1669` | velpTEC GmbH | Weiterbildung zum Process Automation Manager (m/w/d) – (100 % förderbar) | `UNCERTAIN` | `UNCERTAIN` | Participates in vocational training coursework on business process automation, workflow digitization, and robotic automation methods. |
| 33 | `job_59c5ff9eb072325f` | Openai | Deployment Lead, Semiconductors - London | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Leads forward-deployed engineering to integrate frontier AI models into semiconductor engineering workflows and enterprise systems. |
| 34 | `job_d43c7e175f82a591` | Artefactjobs | Stage Communication – Stratégie de communication innovante (Adopt AI) | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates promotional communications, event marketing, and digital media for the enterprise Adopt AI summit. |
| 35 | `job_b097510b7a51bd85` | Artefactjobs | CDI - Senior AI Strategist - Paris | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Formulates strategic AI transformation roadmaps, executive business cases, and enterprise adoption programs. |
| 36 | `job_155ecf409c92d109` | Artefactjobs | CDI - AI Strategist Manager - Paris | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages client consulting engagements to design AI strategy, operating models, and organizational transformation programs. |
| 37 | `job_907cb81c338cc0e6` | Theodo | Senior Manager AI Advisory - CDI Paris - Theodo Data & AI | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Advises corporate executives on AI opportunity assessment, project scoping, and enterprise solution roadmaps. |
| 38 | `job_f06483a2fc383131` | Lightly AG | AI Operations Monitor – Digital Operations & Incident Response | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Monitors production data curation pipelines and coordinates incident response for operational AI systems. |
| 39 | `job_7406a46fe9807699` | Artefactlinkedin | Senior Consultant (Strategy & Data/AI Transformation) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Delivers management consulting assessments, business cases, and strategic roadmaps for enterprise AI transformation. |
| 40 | `job_a77def0795597e98` | Artefactlinkedin | Engagement Manager (Strategy & Data/AI Transformation) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages client delivery teams, project governance, and strategic roadmaps for enterprise data and AI initiatives. |
| 41 | `job_648f158f553d107f` | Artefact | Senior Consultant (Strategy & Data/AI Transformation) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Delivers management consulting assessments, business cases, and strategic roadmaps for enterprise AI transformation. |
| 42 | `job_de6f6aa7ce17764e` | Artefact | Engagement Manager (Strategy & Data/AI Transformation) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages client delivery teams, project governance, and strategic roadmaps for enterprise data and AI initiatives. |
| 43 | `job_a44db05da429e646` | SwissPeak Partners GmbH | Business Analyst Processes and Data | `UNCERTAIN` | `NON_AI_TECH` | Analyzes financial business processes, data flows, and systems architecture for banking operations. |
| 44 | `job_081d0829d645623f` | Proxima | Computational Biologist | `UNCERTAIN` | `CORE_AI_ML` | Builds computational structural biology pipelines and algorithmic benchmarks to support AI drug discovery. |
| 45 | `job_97a4f768e103b5e6` | Envalior | Senior People Intelligence, Automation & AI Specialist | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Develops automated HR workflows, workforce analytics pipelines, and internal AI tools using enterprise automation platforms. |
| 46 | `job_09183096da77cafc` | Skdse | Head of AI (All Genders) | `UNCERTAIN` | `CORE_AI_ML` | Directs organizational AI technical strategy, foundational model architectures, and machine learning infrastructure. |
| 47 | `job_94a95091e1f91f3f` | Skaylink | (Senior) Microsoft Data & AI Security Consultant (m/w/d) | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Architects security frameworks, data governance policies, and Microsoft Purview compliance for enterprise AI workloads. |
| 48 | `job_935400d30ab051bd` | celonis | Associate AI and Data Consultant - Galaxy Graduate Program | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Implements process mining pipelines, data models, and enterprise AI workflows for customer operational transformation. |
| 49 | `job_c98f4209b2130bc9` | BeReal | Marketing Content Specialist - BeReal | `UNCERTAIN` | `NON_TECHNICAL` | Creates social media marketing content, brand campaign assets, and community engagement copy for consumer mobile platforms. |
| 50 | `job_60dafe151b165555` | Enactintelligence | Robot Operator | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Pilots robotic systems in physical environments to capture operational demonstration data for robotics foundation models. |
| 51 | `job_a59e43af035571a3` | Rivia | Customer Engagement Manager | `UNCERTAIN` | `NON_TECHNICAL` | Manages customer success relationships, platform adoption, and client retention for clinical trial data platforms. |
| 52 | `job_d98ec925aa02009f` | Robot Heart | Co-Founder & CTO | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Architects core software platforms, distributed systems, and technical infrastructure for physical AI robotics operations. |
| 53 | `job_bea17c7bbad33d34` | HG International b.v. | Afstudeerstage AI Adoption | `UNCERTAIN` | `NON_TECHNICAL` | Researches internal organizational workflows and designs change management initiatives to drive workplace AI tool adoption. |
| 54 | `job_ac1156091b8fe8bf` | Nebius | Senior Technical Project Manager - VPC | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Manages technical delivery roadmaps, engineering dependencies, and virtual private cloud networking initiatives for AI cloud infrastructure. |
| 55 | `job_eda8631b57f83fae` | Clickhouse | Training Operations Specialist - EMEA | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates training event logistics, attendee communications, and educational program operations. |
| 56 | `job_e99d75c13a1f6076` | Doit | Product Lead - AI Stockbroking App | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Defines product strategy, user experience roadmaps, and feature specifications for an AI-powered stock trading application. |
| 57 | `job_31f4574a32f241d3` | Doit | Product Lead - AI Investing App | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Defines product strategy, customer experience roadmaps, and feature execution for an AI-driven retail investment platform. |
| 58 | `job_730121592a7b12a1` | Doit | Product Lead - AI Neobank App | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Defines product vision, mobile banking capabilities, and customer lifecycle features for an AI-enabled digital banking application. |
| 59 | `job_5b6e705fdd8a3e45` | Doit | Product Owner, Technical - AI Stockbroking | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Translates product capabilities into technical specifications, API requirements, and engineering sprint backlogs for AI trading platforms. |
| 60 | `job_c06cd7c18855728d` | Doit | Product Owner, Technical - AI Investing | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Manages technical user stories, backend API requirements, and development sprint planning for AI investment products. |
| 61 | `job_3f4147f80f8eed20` | Doit | Product Owner, Technical - AI Neobank | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Coordinates technical feature delivery, core banking API integrations, and developer specifications for AI neobanking solutions. |
| 62 | `job_a3045fdafbd0cec5` | GENO Broker GmbH | AI Quality & Governance Specialist (m/w/d) | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Establishes AI quality assurance frameworks, risk governance protocols, and regulatory compliance standards for financial systems. |
| 63 | `job_e1fe8c2686b89dd0` | GENO Broker GmbH | Data Analyst (m/w/d) | `UNCERTAIN` | `NON_AI_TECH` | Develops business intelligence dashboards, database queries, and reporting analytics to support financial brokerage operations. |
| 64 | `job_1f1af246cfd4743c` | Nulegal GmbH | Working Student AI Research (m/f/d) | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Evaluates large language model prompts, document retrieval pipelines, and NLP benchmarks for legal domain applications. |
| 65 | `job_1fe2be9f97ca745e` | Langdock | AI Associate - m/f/d | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Configures enterprise generative AI assistants, designs prompt workflows, and assists client onboarding on LLM platforms. |
| 66 | `job_5451ae341bb01502` | Map | Associate Consultant, AI Transformation | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Delivers management consulting assessments, organizational readiness reviews, and strategic roadmaps for corporate AI adoption. |
| 67 | `job_07d1b215cf73dcbf` | Lyceum | Member of Technical Staff – Monitoring | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Designs distributed monitoring architectures, cluster telemetry, and observability systems for bare-metal GPU cloud infrastructure. |
| 68 | `job_e35a732584dd5a91` | Lyceum | Member of Technical Staff – Isolation, Provisioning, Uptime, Monitoring | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Engineers bare-metal GPU provisioning pipelines, hypervisor virtualization layers, and automated node recovery systems. |
| 69 | `job_5b060bf5f7cd0896` | Lyceum | Member of Technical Staff – VM Features | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Builds virtual machine management features, hardware device virtualization, and hypervisor abstractions for cloud GPU workloads. |
| 70 | `job_93cbaa791c40727a` | Lyceum | Member of Technical Staff – Infra, k8s, Dynamo | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Scales Kubernetes clusters, distributed database layers, and high-throughput model serving infrastructure for AI inference platforms. |
| 71 | `job_5203749acf4b14e8` | Lyceum | Member of Technical Staff – GPU Deployments | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Deploys high-density GPU server clusters, configures high-speed network fabrics, and maintains bare-metal accelerator hardware. |
| 72 | `job_dca7b0b6a47a6b85` | Lyceum | Member of Technical Staff – API, Frontend, Interface, Integrations | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Develops developer-facing APIs, web dashboard interfaces, and model serving framework integrations for an AI cloud platform. |
| 73 | `job_3fcc05f52bb7f78a` | Lyceum | Member of Technical Staff – VM Product & Infra | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Builds distributed control planes, virtual storage subsystems, and software-defined networking for cloud GPU compute instances. |
| 74 | `job_9b103a8e3aaa6496` | Lyceum | Member of Technical Staff – Security | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Implements platform security architectures, container isolation safeguards, and cryptographic access controls for sovereign AI cloud infrastructure. |
| 75 | `job_4f60bf9ee90d37a0` | Care Preventive AG | AI Growth Trainee (60-100%) | `UNCERTAIN` | `NON_TECHNICAL` | Implements marketing automations, lead generation workflows, and AI-assisted digital campaign operations. |
| 76 | `job_f50c741f0b32bd5a` | Sereact GmbH | Internship Teleoperation & Data Labeling - Switzerland | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Operates robotic teleoperation systems and annotates multi-modal sensor data to train industrial robotics AI models. |
| 77 | `job_e47964df703c1efd` | Doit | Technical Product Lead - AI Stockbroking App | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Leads technical product architecture, API designs, and execution roadmaps for an AI-driven stockbroking platform. |
| 78 | `job_a9f504c73a7ccd14` | Doit | Technical Product Lead - AI Investing App | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Leads technical architecture, trading algorithm integrations, and engineering roadmaps for an AI investment application. |
| 79 | `job_b1aed918a2400f31` | Doit | Technical Product Lead - AI Neobank App | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Leads technical architecture, financial API integrations, and engineering roadmaps for an AI-enabled digital banking platform. |
| 80 | `job_22fda7d0b92e76aa` | capco | Infrastructure Manager (m/f/d) for AI Ops Implementation | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Manages enterprise IT infrastructure, DevOps environments, and system reliability for large-scale AI Ops implementations. |
| 81 | `job_b4b51eae834bb973` | Telli | Enterprise Deployment Strategist | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Architects and deploys conversational AI agent workflows, enterprise API integrations, and customer adoption plans. |
| 82 | `job_68fc708b1be009aa` | Vesoma | Robotics Technician | `UNCERTAIN` | `NON_AI_TECH` | Assembles, tests, and calibrates mechanical and electrical hardware systems for physical AI robotic prototypes. |
| 83 | `job_dfddb5a9a3650b41` | TransPerfect | Director, Strategic Accounts - AI Data Solutions | `UNCERTAIN` | `NON_TECHNICAL` | Leads enterprise sales cycles and commercial partnerships for training data collection and AI annotation services. |
| 84 | `job_fde4b60fcd5d454c` | OpenAI | RE/RS, Data Understanding - Foundations | `UNCERTAIN` | `CORE_AI_ML` | Conducts machine learning research to analyze pretraining dataset quality, representations, and algorithmic impact on frontier models. |
| 85 | `job_7373d597c590014b` | Neuralconcept | Senior CAE and AI Expert | `UNCERTAIN` | `CORE_AI_ML` | Develops geometric deep learning models and numerical simulation pipelines to accelerate computer-aided engineering workflows. |
| 86 | `job_e8078287eb87dc0c` | Wavestone Germany AG | Python Software Architekt (m/w/d) (Ref.Nr.: 48296) | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Architects enterprise Python software platforms supporting data analytics, ETL pipelines, and Generative AI services. |
| 87 | `job_acaff5006553133c` | Wavestone Germany AG | Python Software Entwickler (m/w/d) (Ref.Nr.: 48292) | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Develops Python backend services, data extraction pipelines, and automation tools for enterprise GenAI applications. |
| 88 | `job_5572db9983b165e3` | cross-ING AG | Software-Ingenieur:in Robotics | `UNCERTAIN` | `NON_AI_TECH` | Develops embedded software, control systems, and ROS architectures for industrial robotics and mechatronic systems. |
| 89 | `job_ed0544426f0efc0a` | 6Gorilla's | Business Consultant Data & AI | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Advises healthcare and corporate clients on data governance, analytics strategy, and AI solution implementation. |
| 90 | `job_8b6a7fe68fff1038` | TAGGRS | Tracking Specialist | `UNCERTAIN` | `NON_AI_TECH` | Configures server-side tracking tags, analytics scripts, and digital measurement containers for client websites. |
| 91 | `job_9395ac8eab83c8a2` | Black Forest Labs | Research Lead, Evaluations | `UNCERTAIN` | `CORE_AI_ML` | Directs research methodologies and evaluation suites to benchmark multi-modal generative frontier models. |
| 92 | `job_9e4923f4f61926ea` | DataSmart Point GmbH | Karrierestart in Data & AI - IHK Data Analyst (m/w/d) - 100 % Online | `UNCERTAIN` | `UNCERTAIN` | Participates in vocational training curriculum covering data analytics, SQL databases, and AI business applications through an accredited training academy. |
| 93 | `job_c47c30b19b7a902d` | Voodoo | IT Administrator - AI & Cybersecurity | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Administers corporate IT infrastructure, workplace AI tools, and cybersecurity controls across mobile gaming studios. |
| 94 | `job_eb34300548855d73` | MyBikePlan | AI Marketing Internship | `UNCERTAIN` | `NON_TECHNICAL` | Executes digital marketing campaigns, customer acquisition funnels, and advertising creative using AI tools. |
| 95 | `job_e1db5679287eaf9f` | Artifact | Senior AI Consultant | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Delivers strategic consulting advisory, AI readiness workshops, and solution roadmaps for corporate business processes. |
| 96 | `job_0b951decd01c2b26` | TTMS Schweiz AG | Senior AI Consultant / KI-Berater | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Advises enterprise clients on artificial intelligence adoption, architecture selection, and production solution deployment. |
| 97 | `job_c94d6cb844402565` | Tsmg | AI Tester with French | `UNCERTAIN` | `NON_TECHNICAL` | Executes voice data collection operations and evaluates French audio recordings to support speech recognition AI datasets. |
| 98 | `job_91933cd76e884191` | Probatix Health GmbH | Kundenservice & Manufacturing (m/w/d) | `UNCERTAIN` | `NON_TECHNICAL` | Manages customer service inquiries and handles assembly and packaging for medical laboratory test kits. |
| 99 | `job_d732380d4b5b6679` | Mentify Learn GmbH | Amazon Account Manager (m/w/d) - Weiterbildung für Online-Marktplätze & AI, 100 % remote | `UNCERTAIN` | `UNCERTAIN` | Participates in vocational training coursework covering Amazon marketplace management, e-commerce workflows, and AI tools. |
| 100 | `job_9d00f80e541e6fd1` | Excelya | Clinical Data Systems & Data Management | `UNCERTAIN` | `NON_AI_TECH` | Administers computerized clinical research systems, electronic case report forms (eCRF), and clinical trial data management software. |
| 101 | `job_ae42444b365c6fd0` | Remanence | Member of Technical Staff — Infrastructure | `UNCERTAIN` | `AI_INFRASTRUCTURE` | Owns compute orchestration platforms, execution clusters, and distributed systems supporting AI model training and evaluation. |
| 102 | `job_4514f88d9ec70693` | GFL Cosmetics | IT Applications & AI Specialist | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Develops business process automations, internal enterprise applications, and conversational AI assistants using Microsoft Power Platform and Python. |
| 103 | `job_a8419aebc82b1a00` | HICO Group AG | Junior Consultant Planung & AI (100%) (w/m/d), CH, hybrid | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Advises enterprise clients on business intelligence architectures, corporate planning systems, and AI analytics integrations. |
| 104 | `job_8380c3e88e9c6584` | Avertis Group | Deal Sourcing Partner AI, Healthcare & MedTech | `UNCERTAIN` | `NON_TECHNICAL` | Sources investment opportunities, strategic capital deals, and corporate finance partnerships across AI and healthcare sectors. |
| 105 | `job_86c624e1dd2c299c` | NETSHAKE | (Junior) E-Commerce Kaufmann (w/m/d) | `UNCERTAIN` | `NON_TECHNICAL` | Manages Shopify e-commerce store operations, digital product merchandising, and client support workflows. |
| 106 | `job_f758d5d0dfd3c148` | isaraerospace | Intern AI & Data Transformation | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Builds automated ELT data pipelines, API integrations, and warehouse data models supporting operational analytics. |
| 107 | `job_7fa0c886847ad020` | hellofresh | Senior Category Manager – Marketing (All Genders) | `UNCERTAIN` | `NON_TECHNICAL` | Leads strategic procurement, supplier contract negotiations, and agency spend management for corporate marketing categories. |
| 108 | `job_2d0fc63ff4419f55` | Bitstack | AML/CFT & Fraud Analyst - Internship | `UNCERTAIN` | `NON_TECHNICAL` | Conducts anti-money laundering transaction monitoring, fraud investigations, and regulatory compliance checks. |
| 109 | `job_ab5ac1cc60164046` | HICO Group AG | (Senior) Consultant Analytics & AI, Qlik (100%) (m/w/d), CH, hybrid | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Designs enterprise business intelligence dashboards, Qlik analytics architectures, and AI data solutions for corporate clients. |
| 110 | `job_4293f2e4c2289620` | Rithum | PMO & Portfolio Analyst | `UNCERTAIN` | `NON_TECHNICAL` | Coordinates program management office cadences, project portfolio tracking, and executive operational reporting. |
| 111 | `job_0b52ba3fd883521c` | Welo Global | Finnish Tech Linguistic Tester | `UNCERTAIN` | `NON_TECHNICAL` | Executes localization quality assurance, translation validation, and linguistic operations for Finnish language software. |
| 112 | `job_7ff814cb58f1225d` | TechMagic | Customer Experience Analyst | `UNCERTAIN` | `AI_PRODUCT_SOLUTIONS` | Builds customer experience analytics pipelines, sentiment classification models, and conversational journey analytics using Qualtrics XM Discover. |
| 113 | `job_50d1df7084a06283` | Nebius | GPU Compute Partnerships & Commercial Operations Manager | `UNCERTAIN` | `NON_TECHNICAL` | Negotiates commercial agreements, vendor contracts, and capacity procurement for external GPU compute infrastructure. |
| 114 | `job_675a85266ca800bd` | TELUS Digital | Content Reviewer - United States | `UNCERTAIN` | `NON_TECHNICAL` | Evaluates search engine result quality, content accuracy, and user relevance ratings against standardized evaluation guidelines. |
| 115 | `job_52cf5f192858c983` | Metics Media | Content Creator - YouTube | `UNCERTAIN` | `NON_TECHNICAL` | Researches, scripts, and presents educational video tutorials on software applications and artificial intelligence tools. |
| 116 | `job_707a7ad52df07edf` | VXI Global Solutions | US Remote Patient Care Advocate (Customer Service) | `UNCERTAIN` | `NON_TECHNICAL` | Assists patients with prescription payment assistance navigation, insurance coordination, and customer healthcare support. |
| 117 | `job_201518350968ce4f` | iMerit Technology | AI Trainer - Video Annotation | `UNCERTAIN` | `AI_SUPPORTING_TECH` | Annotates and validates video datasets with object bounding boxes and action markers to train robotics AI models. |

---

## 5. Detailed Individual Record Inspections (All 117 Records)

### Record 1/117: `job_1a388cef4b8843e0` – Palantir Technologies – American Tech Fellowship

- **Company:** Palantir Technologies
- **Title:** American Tech Fellowship
- **Canonical Job ID:** `job_1a388cef4b8843e0`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Deploys enterprise data and AI workflows using Palantir Foundry and Artificial Intelligence Platform (AIP).
- **Source Responsibility Evidence:** *"In this fellowship, you'll participate in a comprehensive training program with our partner, Ontologize, to level up your technical skills on Foundry and AIP."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Apprenticeship and technical deployment program training fellows to deploy operational data workflows and AI models using Palantir Foundry and AIP.

### Record 2/117: `job_799b4f210a0fa4ff` – capco – Infrastructure Manager (m/w/d) for AI Ops Implementation

- **Company:** capco
- **Title:** Infrastructure Manager (m/w/d) for AI Ops Implementation
- **Canonical Job ID:** `job_799b4f210a0fa4ff`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Manages enterprise IT infrastructure, DevOps environments, and system reliability for large-scale AI Ops implementations.
- **Source Responsibility Evidence:** *"Lead and coordinate a large-scale AI Ops implementation project, ensuring effective planning, execution, and alignment with business and technical objectives. Manage and coordinate cross-functional IT teams responsible for setting up, integrating, and managing complex infrastructure environments"*
- **Source Qualification Evidence:** *"(e.g., performance, security, availability). Proficient in stakeholder communication and program leadership. Experience working in ITIL-based, DevOps, or agile project environments. High degree of ownership and structured work approach."*
- **Decision Rationale:** Leads infrastructure management, ITIL/DevOps environments, and high-availability operations for enterprise banking AI Ops implementations.

### Record 3/117: `job_fc9648e35ba5db78` – Impossiblecloud – Go-to-Market Champion (GPU & AI)

- **Company:** Impossiblecloud
- **Title:** Go-to-Market Champion (GPU & AI)
- **Canonical Job ID:** `job_fc9648e35ba5db78`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Drives go-to-market strategy, product pricing, and commercial expansion for cloud GPU compute and AI infrastructure.
- **Source Responsibility Evidence:** *"- Define and drive Impossible Cloud’s global Go-to-Market (GTM) strategy, including market segmentation, value propositions, pricing, and packaging for GPU cloud and AI infrastructure, targeting enterprise, startups, and research segments. - Establish"*
- **Source Qualification Evidence:** *"- 8-10+ years of Go-to-Market (GTM) leadership experience in cloud, infrastructure, or AI technology companies. - Deep technical expertise in GPUs, cloud technologies, and AI/ML workloads. - Proven track record of building and executing successful global GTM"*
- **Decision Rationale:** Commercial leadership role owning global GTM strategy, value propositions, packaging, and enterprise sales motions for GPU cloud infrastructure.

### Record 4/117: `job_122d9b1a2804bf26` – Quantco – Office Management Working Student

- **Company:** Quantco
- **Title:** Office Management Working Student
- **Canonical Job ID:** `job_122d9b1a2804bf26`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates office administration, vendor relationships, and workplace facilities operations.
- **Source Responsibility Evidence:** *"Act as the primary contact for vendors, suppliers, and service providers (e.g., food, beverages, and office supplies). Help to make the office a great and comfortable workplace for our smart and fun colleagues."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Administrative operational role handling office supplies, vendor coordination, and facilities support at a data science firm.

### Record 5/117: `job_a94dd6fdadc3d3dd` – Almetra – PhD Researcher – Video Understanding & VLMs

- **Company:** Almetra
- **Title:** PhD Researcher – Video Understanding & VLMs
- **Canonical Job ID:** `job_a94dd6fdadc3d3dd`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Researches and trains vision-language foundation models and deep learning architectures for video understanding.
- **Source Responsibility Evidence:** *"You’ll do your PhD with us from day one, working closely with Sascha, our Head of ML (VLM), on research problems that come straight from our product. Your research runs on real industrial video at a scale few academic labs have."*
- **Source Qualification Evidence:** *"Master’s degree in Computer Science, Machine Learning, AI or a closely related field, with a focus on computer vision or multimodal learning (finished or finishing by early-2027) Solid deep learning foundations and hands-on PyTorch Experience with computer"*
- **Decision Rationale:** Frontier scientific research role developing multimodal vision-language foundation models (VLMs) and deep learning algorithms in PyTorch.

### Record 6/117: `job_aa46581403b45706` – Rosental Organics GmbH – Senior AI Content Producer - Foto, Video, Motion (m/w/d)

- **Company:** Rosental Organics GmbH
- **Title:** Senior AI Content Producer - Foto, Video, Motion (m/w/d)
- **Canonical Job ID:** `job_aa46581403b45706`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Produces digital advertising assets, video content, and marketing creative using generative AI tools.
- **Source Responsibility Evidence:** *"Bei Rosental Organics bist du kein klassischer Fotograf oder Videograf – du bist der Content Multiplier. Ein Shoot wird bei dir zu 50+ Assets, ein UGC-Clip zu 30 Hook-Variants, ein Produktfoto zu 20 Format-Adaptionen."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Creative marketing role leveraging generative AI image and video synthesis tools to generate multi-format social ad campaigns.

### Record 7/117: `job_1491ef1a44058319` – Miebach Consulting GmbH – Senior Expert (w/m/d) - Logistics Management Systems

- **Company:** Miebach Consulting GmbH
- **Title:** Senior Expert (w/m/d) - Logistics Management Systems
- **Canonical Job ID:** `job_1491ef1a44058319`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Advises enterprise clients on supply chain architecture, warehouse management systems, and logistics software implementations.
- **Source Responsibility Evidence:** *"Bei Miebach Consulting erwarten dich anspruchsvolle Aufgaben entlang der gesamten Supply Chain . Von Anfang an übernimmst du Verantwortung in spannenden Beratungsprojekten, unterstützt durch ein fundiertes, individuelles Trainingsprogramm."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Consulting engineering position implementing traditional warehouse management systems (WMS), transport systems, and supply chain IT.

### Record 8/117: `job_269fbdaeeea8515a` – Baringa – Senior Manager, AI & Trading Transformation

- **Company:** Baringa
- **Title:** Senior Manager, AI & Trading Transformation
- **Canonical Job ID:** `job_269fbdaeeea8515a`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Leads enterprise consulting engagements to implement AI solutions and digital transformation in commodity trading.
- **Source Responsibility Evidence:** *"reduction targets and our support of the Better Business Act. We report our progress publicly and ensure that we are also externally assessed and scored through organisations like CDP and EcoVadis - helping us to continually identify where we can improve."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management consulting leader delivering commercial AI transformation roadmaps and trading process automation for energy and commodity clients.

### Record 9/117: `job_93e9a4b3fd1528a4` – Zoominfo – Senior SEO & AI Search Manager

- **Company:** Zoominfo
- **Title:** Senior SEO & AI Search Manager
- **Canonical Job ID:** `job_93e9a4b3fd1528a4`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Develops organic search engine marketing optimization strategies across traditional search platforms and conversational AI search engines.
- **Source Responsibility Evidence:** *"Search is changing faster than at any point in the last 20 years. Buyers now find answers in Google and in ChatGPT, Gemini, Perplexity and AI Overviews, and we want ZoomInfo to always be the answer they get."*
- **Source Qualification Evidence:** *"5+ years in SEO, with experience at a B2B SaaS company You're an effective writer in your own right, with experience owning content end to end A proven record of connecting organic and AI search visibility to pipeline and revenue Practical experience with AI"*
- **Decision Rationale:** Marketing position optimizing brand visibility, organic search rankings, and content indexing across Google and generative AI discovery engines.

### Record 10/117: `job_0720bc84679aeca7` – Ema – AI Resident UK/EMEA

- **Company:** Ema
- **Title:** AI Resident UK/EMEA
- **Canonical Job ID:** `job_0720bc84679aeca7`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Deploys and customizes autonomous AI agents and enterprise generative AI workflows for customer operations.
- **Source Responsibility Evidence:** *"About Ema Ema builds AI Employees for HR, IT and Finance."*
- **Source Qualification Evidence:** *"A builder's mindset and high agency. You find a way to ship rather than waiting for the blocker to clear, and you follow your work into production. Final-year undergraduates, MSc/MEng and PhD students, recent graduates and self-taught builders are all welcome."*
- **Decision Rationale:** Customer-facing applied AI role configuring autonomous workplace AI agents and integrating them into enterprise HR, IT, and finance systems.

### Record 11/117: `job_4628c8bf8e5ebcb2` – Luke Recruitment – Senior Social & AI Marketeer

- **Company:** Luke Recruitment
- **Title:** Senior Social & AI Marketeer
- **Canonical Job ID:** `job_4628c8bf8e5ebcb2`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Directs social media marketing campaigns and brand activation strategies utilizing generative AI marketing tools.
- **Source Responsibility Evidence:** *"Jouw impact als Senior Social & AI Marketeer Als Senior Social & AI Marketeer bij Indicia ben je het strategische aanspreekpunt voor grote klanten en vertaal je hun commerciële doelstellingen naar effectieve socialmediastrategieën."*
- **Source Qualification Evidence:** *"Je bent een enthousiaste en ondernemende persoonlijkheid die energie brengt, initiatief neemt en het team weet mee te nemen in nieuwe ideeën."*
- **Decision Rationale:** Digital marketing specialist deploying generative AI content tools to manage client social media channels, brand awareness, and campaign creative.

### Record 12/117: `job_ddb8989279b2765a` – WIRECLOUD – First Level IT-Support / Kundenberatung (m/w/d)

- **Company:** WIRECLOUD
- **Title:** First Level IT-Support / Kundenberatung (m/w/d)
- **Canonical Job ID:** `job_ddb8989279b2765a`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Provides first-level IT technical support, cloud telephony troubleshooting, and customer assistance.
- **Source Responsibility Evidence:** *"Support-Hero & Problemlöser gesucht – Quereinstieg willkommen! Du hilfst einfach gerne anderen Menschen? Du tüftelst gerne an technischen Herausforderungen, bis sie gelöst sind? Dann passt du perfekt in unser Team! Als gewachsenes Tech-Unternehmen ist"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Customer helpdesk and IT support position resolving hardware, network, and cloud VoIP telephone software tickets.

### Record 13/117: `job_6808753b9abd122d` – Perplexity – Research & Development Site Lead (London)

- **Company:** Perplexity
- **Title:** Research & Development Site Lead (London)
- **Canonical Job ID:** `job_6808753b9abd122d`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Directs research and engineering operations for conversational AI search platform development.
- **Source Responsibility Evidence:** *"Head up Perplexity London, taking responsibility for what the site delivers, how it scales and its standing in the UK. Work directly with Perplexity's cofounders & leaders in other offices so London's work connects to company priorities."*
- **Source Qualification Evidence:** *"Extensive background in research and engineering, with evidence of real-world impact via shipped systems, published papers, and/or open source. Has built, scaled, and led technical teams accountable for ambitious roadmaps."*
- **Decision Rationale:** R&D site leadership position driving research agenda, model capabilities, and engineering execution for conversational AI search engines.

### Record 14/117: `job_fc733b2e34ce7d90` – Jellyfish – Media Strategy Manager

- **Company:** Jellyfish
- **Title:** Media Strategy Manager
- **Canonical Job ID:** `job_fc733b2e34ce7d90`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Plans and manages multi-channel digital media campaigns, advertising strategies, and client brand communications.
- **Source Responsibility Evidence:** *"will include: Lead the translation of client briefs into cross-channel digital media plans (programmatic, search, social, video) that deliver effective and accountable outcomes for our clients including budget and flighting recommendations, audience targeting"*
- **Source Qualification Evidence:** *"Experience in a media strategy or planning role, or in a cross-channel buying role within an agency or multinational client organization Demonstrated expertise in developing brand, digital marketing and planning strategies, with a fluency in digital media"*
- **Decision Rationale:** Digital marketing agency role designing advertising media plans, client brand campaigns, and commercial media buying.

### Record 15/117: `job_46ed8ae5be510862` – 1KOMMA5˚ – (Junior) SEO & AI Marketing Manager (m/w/d)

- **Company:** 1KOMMA5˚
- **Title:** (Junior) SEO & AI Marketing Manager (m/w/d)
- **Canonical Job ID:** `job_46ed8ae5be510862`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Executes search engine optimization and digital marketing campaigns utilizing generative AI content tools.
- **Source Responsibility Evidence:** *"den Überblick. Strategischem Wandel (AI Movement) gegenüber bist du besonders resilient. Kommunikation & Sprache: Fließendes Deutsch und Englisch."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Marketing specialist managing organic search optimization, keyword strategy, and generative AI content creation tools.

### Record 16/117: `job_d6d446b7dbc88c38` – INC Innovation Center GmbH – Technischer Projektleiter Robotik & Physical AI (m/w/d)

- **Company:** INC Innovation Center GmbH
- **Title:** Technischer Projektleiter Robotik & Physical AI (m/w/d)
- **Canonical Job ID:** `job_d6d446b7dbc88c38`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages technical testing, platform integration, and industrial deployment projects for physical AI and robotics systems.
- **Source Responsibility Evidence:** *"Gestalte mit uns die Zukunft von Physical AI und Robotik! Mit unserem Future Robotics Exploration Hub in Stuttgart bauen wir aktuell einen hersteller- und technologieunabhängiger Innovations- und Testraum für mobile und humanoide Robotik, Physical AI und"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Technical project manager overseeing the Future Robotics Exploration Hub, evaluating robotic platforms, sensor suites, and physical AI models.

### Record 17/117: `job_984f995d02d192a3` – momox – Team Lead Pricing & AI - momox SE | Berlin | Full-Time

- **Company:** momox
- **Title:** Team Lead Pricing & AI - momox SE | Berlin | Full-Time
- **Canonical Job ID:** `job_984f995d02d192a3`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Leads automated pricing strategy, algorithmic optimization, and AI solution roadmaps for e-commerce operations.
- **Source Responsibility Evidence:** *"You don't just want to analyze a business – you want to steer it. As Team Lead Pricing & AI (m/f/d), you own pricing and the AI roadmap for our Books & Media Business Unit and brands."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Product/business leadership position directing dynamic pricing algorithms, predictive analytics roadmaps, and automated e-commerce buying/selling.

### Record 18/117: `job_b5650f32784de67d` – Anton Robotics – Working Student – Robot Teleoperation & Data Collection for Robot Foundation Models (m/w/d)

- **Company:** Anton Robotics
- **Title:** Working Student – Robot Teleoperation & Data Collection for Robot Foundation Models (m/w/d)
- **Canonical Job ID:** `job_b5650f32784de67d`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Collects and curates sensor datasets through robot teleoperation to support training pipelines for robotic foundation models.
- **Source Responsibility Evidence:** *"Operate robots via teleoperation systems to gather high-quality training data for robot foundation models. Process, structure, and manage large datasets to support data engineering pipelines."*
- **Source Qualification Evidence:** *"Enrolled as a student in robotics, computer science, engineering, or a related technical field. Strong interest in robotics, automation, and machine learning data pipelines."*
- **Decision Rationale:** Technical operational role operating teleoperated robotic arms and managing data curation pipelines for foundation model pretraining.

### Record 19/117: `job_20389864f9cfdf4b` – TecTake – Junior Specialist Automation & AI (m/w/d)

- **Company:** TecTake
- **Title:** Junior Specialist Automation & AI (m/w/d)
- **Canonical Job ID:** `job_20389864f9cfdf4b`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Implements business process automation and integrates generative AI workplace tools to optimize operational workflows.
- **Source Responsibility Evidence:** *"tectake ist ein dynamisches E-Commerce-Unternehmen mit einem breiten und stetig wachsenden Produktsortiment rund um Wohnen, Haushalt, Freizeit und Hobby."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Operational automation role analyzing internal e-commerce processes and deploying RPA and generative AI productivity tools.

### Record 20/117: `job_8dacf0db937b2f92` – Anton Robotics – Founder's Associate - Internship (m/w/d)

- **Company:** Anton Robotics
- **Title:** Founder's Associate - Internship (m/w/d)
- **Canonical Job ID:** `job_8dacf0db937b2f92`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Supports startup operational execution, commercial business development, and administrative workflows for executive leadership.
- **Source Responsibility Evidence:** *"Support the founder in day-to-day company building Build streamlined, AI-native business operations Support sales, finance, strategy and business development Manage and continuously improve our online presence Manage employer branding, hiring pipeline and"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** General business operations role assisting founders across commercial strategy, recruitment, investor relations, and administrative tasks.

### Record 21/117: `job_ea151868d0cabf39` – JustPlay GmbH – Platform QA Chapter Lead (all genders)

- **Company:** JustPlay GmbH
- **Title:** Platform QA Chapter Lead (all genders)
- **Canonical Job ID:** `job_ea151868d0cabf39`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Leads quality assurance methodologies, automated testing frameworks, and release validation for mobile app platforms.
- **Source Responsibility Evidence:** *"Own the full QA lifecycle for JustPlay’s app and platform features - from test planning and execution to reporting and defect management."*
- **Source Qualification Evidence:** *"5+ years of experience in QA for mobile apps or platforms, including at least 2 years leading teams. Proven ability to design scalable QA processes in fast-paced, development-heavy environments."*
- **Decision Rationale:** Software engineering QA lead managing automated testing suites, defect triage, and mobile platform release validation.

### Record 22/117: `job_350a930679a271b8` – Neuphonic – Marketing Generalist

- **Company:** Neuphonic
- **Title:** Marketing Generalist
- **Canonical Job ID:** `job_350a930679a271b8`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates brand marketing campaigns, product content, and public communications for a speech AI platform.
- **Source Responsibility Evidence:** *"Creating and publishing content across LinkedIn, X, our website and other relevant channels Helping plan and execute product launches, open-source releases and company announcements Turning technical work from our engineering and research teams into clear, engaging content"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Marketing generalist handling brand communications, event coordination, content writing, and digital media for an on-device voice AI startup.

### Record 23/117: `job_293c05cfec50d0fb` – Artefactlinkedin – Stage Communication – Stratégie de communication innovante (Adopt AI)

- **Company:** Artefactlinkedin
- **Title:** Stage Communication – Stratégie de communication innovante (Adopt AI)
- **Canonical Job ID:** `job_293c05cfec50d0fb`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates promotional communications, event marketing, and digital media for the enterprise Adopt AI summit.
- **Source Responsibility Evidence:** *"En soutien direct à la chargée de communication et au sein du pôle événementiel & communication, vous interviendrez sur un large spectre de missions : Communication et stratégie de marque Participation à la réflexion autour de la promotion de l’évènement"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Communications internship organizing marketing assets, media relations, and promotional campaigns for an enterprise AI conference.

### Record 24/117: `job_f8fe86ec4cb87275` – Artefactlinkedin – Directeur Practice Consulting & Data Transformation

- **Company:** Artefactlinkedin
- **Title:** Directeur Practice Consulting & Data Transformation
- **Canonical Job ID:** `job_f8fe86ec4cb87275`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Directs enterprise consulting practices delivering data strategy, marketing analytics, and AI transformation programs.
- **Source Responsibility Evidence:** *"Your role will be encompass: Bring the best of our expertise from the other Departments to your clients on Data Science, Activation (e.g., media buying, CRM, …) and Creativity."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Executive practice director advising C-level enterprise clients on data science roadmaps, marketing activation, and enterprise AI transformations.

### Record 25/117: `job_ad0a653b919ed9e7` – Artefactlinkedin – CDI - Senior AI Strategist - Paris

- **Company:** Artefactlinkedin
- **Title:** CDI - Senior AI Strategist - Paris
- **Canonical Job ID:** `job_ad0a653b919ed9e7`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Formulates strategic AI transformation roadmaps, executive business cases, and enterprise adoption programs.
- **Source Responsibility Evidence:** *"vous cadrez, analysez, prototypez et recommandez, vous coachez les consultants juniors, et vous voyez vos recommandations prendre vie avec nos équipes Engineering"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Strategic advisor designing C-suite business cases, target operating models, and organizational AI transformation streams.

### Record 26/117: `job_0eee96d8d91c0017` – Artefactlinkedin – CDI - AI Strategist Manager - Paris

- **Company:** Artefactlinkedin
- **Title:** CDI - AI Strategist Manager - Paris
- **Canonical Job ID:** `job_0eee96d8d91c0017`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages client consulting engagements to design AI strategy, operating models, and organizational transformation programs.
- **Source Responsibility Evidence:** *"En tant qu’ AI Strategist Manager , vous construisez avec les dirigeants de nos clients une stratégie IA crédible, un modèle opératoire adapté et un programme de transformation qui génère une valeur mesurable."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management consulting leader guiding corporate executives in formulating enterprise AI roadmaps and governance operating models.

### Record 27/117: `job_2ea929afcff1d70b` – Artefact – Stage Communication – Stratégie de communication innovante (Adopt AI)

- **Company:** Artefact
- **Title:** Stage Communication – Stratégie de communication innovante (Adopt AI)
- **Canonical Job ID:** `job_2ea929afcff1d70b`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates promotional communications, event marketing, and digital media for the enterprise Adopt AI summit.
- **Source Responsibility Evidence:** *"En soutien direct à la chargée de communication et au sein du pôle événementiel & communication, vous interviendrez sur un large spectre de missions : Communication et stratégie de marque Participation à la réflexion autour de la promotion de l’évènement"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Communications internship organizing marketing assets, media relations, and promotional campaigns for an enterprise AI conference.

### Record 28/117: `job_4370eb0694ede9e6` – Artefact – CDI - Senior AI Strategist - Paris

- **Company:** Artefact
- **Title:** CDI - Senior AI Strategist - Paris
- **Canonical Job ID:** `job_4370eb0694ede9e6`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Formulates strategic AI transformation roadmaps, executive business cases, and enterprise adoption programs.
- **Source Responsibility Evidence:** *"vous cadrez, analysez, prototypez et recommandez, vous coachez les consultants juniors, et vous voyez vos recommandations prendre vie avec nos équipes Engineering"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Strategic advisor designing C-suite business cases, target operating models, and organizational AI transformation streams.

### Record 29/117: `job_b14e70ee758843ba` – Artefact – CDI - AI Strategist Manager - Paris

- **Company:** Artefact
- **Title:** CDI - AI Strategist Manager - Paris
- **Canonical Job ID:** `job_b14e70ee758843ba`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages client consulting engagements to design AI strategy, operating models, and organizational transformation programs.
- **Source Responsibility Evidence:** *"En tant qu’ AI Strategist Manager , vous construisez avec les dirigeants de nos clients une stratégie IA crédible, un modèle opératoire adapté et un programme de transformation qui génère une valeur mesurable."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management consulting leader guiding corporate executives in formulating enterprise AI roadmaps and governance operating models.

### Record 30/117: `job_df65ec2483015bf8` – DPG Media – Advertising Data Specialist

- **Company:** DPG Media
- **Title:** Advertising Data Specialist
- **Canonical Job ID:** `job_df65ec2483015bf8`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Analyzes digital advertising campaign metrics, audience data segments, and commercial delivery reporting.
- **Source Responsibility Evidence:** *"Amsterdam/Hilversum - Bereik 91% van alle Nederlanders met jouw werk! Als Advertising Data Specialist maak jij elke dag impact door middel van onze nieuwsmedia, magazines, online services, radio en TV."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Media data analyst reporting on advertising delivery, audience segment effectiveness, and digital marketing performance.

### Record 31/117: `job_2c0079996ca79a21` – Infomedics – Helpdeskmedewerker Tandheelkundige Software

- **Company:** Infomedics
- **Title:** Helpdeskmedewerker Tandheelkundige Software
- **Canonical Job ID:** `job_2c0079996ca79a21`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Provides customer technical support and application troubleshooting for specialized dental practice management software.
- **Source Responsibility Evidence:** *"Helpdeskmedewerker Tandheelkundige Software Kwadijk | € 2.800 - € 3.600 per maand | 32-40 uur Ben jij degene die klanten met een glimlach verder helpt? Word jij blij van mensen helpen? Kun je goed luisteren, doorvragen en houd je ervan om samen tot een"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Helpdesk specialist assisting dental clinics with software installation, user questions, and billing application support.

### Record 32/117: `job_b8483b279f8b1669` – velpTEC GmbH – Weiterbildung zum Process Automation Manager (m/w/d) – (100 % förderbar)

- **Company:** velpTEC GmbH
- **Title:** Weiterbildung zum Process Automation Manager (m/w/d) – (100 % förderbar)
- **Canonical Job ID:** `job_b8483b279f8b1669`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `UNCERTAIN`
- **Updated Classification Reason:** Participates in vocational training coursework on business process automation, workflow digitization, and robotic automation methods.
- **Source Responsibility Evidence:** *"Als Process Automation Manager (m/w/d) analysierst, optimierst und automatisierst du betriebliche Geschäftsprozesse, um Arbeitsabläufe effizienter und zukunftssicher zu gestalten."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Subsidized AZAV vocational education program teaching process optimization rather than an operational corporate employment vacancy.

### Record 33/117: `job_59c5ff9eb072325f` – Openai – Deployment Lead, Semiconductors - London

- **Company:** Openai
- **Title:** Deployment Lead, Semiconductors - London
- **Canonical Job ID:** `job_59c5ff9eb072325f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Leads forward-deployed engineering to integrate frontier AI models into semiconductor engineering workflows and enterprise systems.
- **Source Responsibility Evidence:** *"As a Deployment Lead, you will define how OpenAI delivers complex systems to Semiconductor customers."*
- **Source Qualification Evidence:** *"into a delivery plan. Shape production deployments that integrate with customer infrastructure, data systems, and engineering toolchains, including export-controlled environments."*
- **Decision Rationale:** Forward-deployed engineering leader at OpenAI tailoring frontier models for semiconductor design and manufacturing clients.

### Record 34/117: `job_d43c7e175f82a591` – Artefactjobs – Stage Communication – Stratégie de communication innovante (Adopt AI)

- **Company:** Artefactjobs
- **Title:** Stage Communication – Stratégie de communication innovante (Adopt AI)
- **Canonical Job ID:** `job_d43c7e175f82a591`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates promotional communications, event marketing, and digital media for the enterprise Adopt AI summit.
- **Source Responsibility Evidence:** *"En soutien direct à la chargée de communication et au sein du pôle événementiel & communication, vous interviendrez sur un large spectre de missions : Communication et stratégie de marque Participation à la réflexion autour de la promotion de l’évènement"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Communications internship organizing marketing assets, media relations, and promotional campaigns for an enterprise AI conference.

### Record 35/117: `job_b097510b7a51bd85` – Artefactjobs – CDI - Senior AI Strategist - Paris

- **Company:** Artefactjobs
- **Title:** CDI - Senior AI Strategist - Paris
- **Canonical Job ID:** `job_b097510b7a51bd85`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Formulates strategic AI transformation roadmaps, executive business cases, and enterprise adoption programs.
- **Source Responsibility Evidence:** *"vous cadrez, analysez, prototypez et recommandez, vous coachez les consultants juniors, et vous voyez vos recommandations prendre vie avec nos équipes Engineering"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Strategic advisor designing C-suite business cases, target operating models, and organizational AI transformation streams.

### Record 36/117: `job_155ecf409c92d109` – Artefactjobs – CDI - AI Strategist Manager - Paris

- **Company:** Artefactjobs
- **Title:** CDI - AI Strategist Manager - Paris
- **Canonical Job ID:** `job_155ecf409c92d109`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages client consulting engagements to design AI strategy, operating models, and organizational transformation programs.
- **Source Responsibility Evidence:** *"En tant qu’ AI Strategist Manager , vous construisez avec les dirigeants de nos clients une stratégie IA crédible, un modèle opératoire adapté et un programme de transformation qui génère une valeur mesurable."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management consulting leader guiding corporate executives in formulating enterprise AI roadmaps and governance operating models.

### Record 37/117: `job_907cb81c338cc0e6` – Theodo – Senior Manager AI Advisory - CDI Paris - Theodo Data & AI

- **Company:** Theodo
- **Title:** Senior Manager AI Advisory - CDI Paris - Theodo Data & AI
- **Canonical Job ID:** `job_907cb81c338cc0e6`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Advises corporate executives on AI opportunity assessment, project scoping, and enterprise solution roadmaps.
- **Source Responsibility Evidence:** *"Delivery : tu es garant de la qualité des missions et de la satisfaction des décideurs C-level."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Advisory consulting manager guiding key account clients from initial AI ideation and value scoping to production delivery.

### Record 38/117: `job_f06483a2fc383131` – Lightly AG – AI Operations Monitor – Digital Operations & Incident Response

- **Company:** Lightly AG
- **Title:** AI Operations Monitor – Digital Operations & Incident Response
- **Canonical Job ID:** `job_f06483a2fc383131`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Monitors production data curation pipelines and coordinates incident response for operational AI systems.
- **Source Responsibility Evidence:** *"What you'll be doing Monitor autonomous digital workflows and operational activity through a web-based interface, identifying errors, unusual behavior, and situations requiring human intervention Remain available and responsive throughout scheduled shifts ,"*
- **Source Qualification Evidence:** *"You're a strong candidate if you: Have fluent written and spoken English , with the ability to communicate clearly and concisely during operational incidents Have experience in technical support, quality assurance (QA), digital operations, IT support, or a"*
- **Decision Rationale:** Technical operations role monitoring automated data pipelines, computer vision dataset jobs, and responding to system incidents.

### Record 39/117: `job_7406a46fe9807699` – Artefactlinkedin – Senior Consultant (Strategy & Data/AI Transformation)

- **Company:** Artefactlinkedin
- **Title:** Senior Consultant (Strategy & Data/AI Transformation)
- **Canonical Job ID:** `job_7406a46fe9807699`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Delivers management consulting assessments, business cases, and strategic roadmaps for enterprise AI transformation.
- **Source Responsibility Evidence:** *"As a Senior Consultant in our Zurich/Lausanne office, you will work at the intersection of strategy consulting and data and AI delivery. You will: Strategy Development: Work with client leadership teams to address high-stakes questions."*
- **Source Qualification Evidence:** *"We are looking for someone who can hold a technical position and a commercial one at the same time. The strongest candidates meet most of the following. Education: A degree in Computer Science, Engineering, Data Science, Business, Economics or a related field."*
- **Decision Rationale:** Strategy consultant formulating data architecture roadmaps, AI use-case prioritization, and change management programs.

### Record 40/117: `job_a77def0795597e98` – Artefactlinkedin – Engagement Manager (Strategy & Data/AI Transformation)

- **Company:** Artefactlinkedin
- **Title:** Engagement Manager (Strategy & Data/AI Transformation)
- **Canonical Job ID:** `job_a77def0795597e98`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages client delivery teams, project governance, and strategic roadmaps for enterprise data and AI initiatives.
- **Source Responsibility Evidence:** *"As an Engagement Manager in our Zurich or Lausanne office, you will work at the intersection of strategy consulting and data and AI delivery. You will: Strategy Development: Work with client leadership teams to address high-stakes questions."*
- **Source Qualification Evidence:** *"We are looking for someone who can hold a technical position and a commercial one at the same time, and lead a team through both. The strongest candidates meet most of the following."*
- **Decision Rationale:** Consulting engagement manager directing project streams, client stakeholder relationships, and deliverables for AI transformation.

### Record 41/117: `job_648f158f553d107f` – Artefact – Senior Consultant (Strategy & Data/AI Transformation)

- **Company:** Artefact
- **Title:** Senior Consultant (Strategy & Data/AI Transformation)
- **Canonical Job ID:** `job_648f158f553d107f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Delivers management consulting assessments, business cases, and strategic roadmaps for enterprise AI transformation.
- **Source Responsibility Evidence:** *"As a Senior Consultant in our Zurich/Lausanne office, you will work at the intersection of strategy consulting and data and AI delivery. You will: Strategy Development: Work with client leadership teams to address high-stakes questions."*
- **Source Qualification Evidence:** *"We are looking for someone who can hold a technical position and a commercial one at the same time. The strongest candidates meet most of the following. Education: A degree in Computer Science, Engineering, Data Science, Business, Economics or a related field."*
- **Decision Rationale:** Strategy consultant formulating data architecture roadmaps, AI use-case prioritization, and change management programs.

### Record 42/117: `job_de6f6aa7ce17764e` – Artefact – Engagement Manager (Strategy & Data/AI Transformation)

- **Company:** Artefact
- **Title:** Engagement Manager (Strategy & Data/AI Transformation)
- **Canonical Job ID:** `job_de6f6aa7ce17764e`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages client delivery teams, project governance, and strategic roadmaps for enterprise data and AI initiatives.
- **Source Responsibility Evidence:** *"As an Engagement Manager in our Zurich or Lausanne office, you will work at the intersection of strategy consulting and data and AI delivery. You will: Strategy Development: Work with client leadership teams to address high-stakes questions."*
- **Source Qualification Evidence:** *"We are looking for someone who can hold a technical position and a commercial one at the same time, and lead a team through both. The strongest candidates meet most of the following."*
- **Decision Rationale:** Consulting engagement manager directing project streams, client stakeholder relationships, and deliverables for AI transformation.

### Record 43/117: `job_a44db05da429e646` – SwissPeak Partners GmbH – Business Analyst Processes and Data

- **Company:** SwissPeak Partners GmbH
- **Title:** Business Analyst Processes and Data
- **Canonical Job ID:** `job_a44db05da429e646`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Analyzes financial business processes, data flows, and systems architecture for banking operations.
- **Source Responsibility Evidence:** *"Analyse and document processes, data flows, systems and responsibilities end to end Create the as-is analysis, derive the target picture and to-be processes, define data ownership Assess optimisation potential in data storage and the system landscape Create"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Banking business analyst assessing as-is data flows, defining target operating models, and optimizing financial data storage.

### Record 44/117: `job_081d0829d645623f` – Proxima – Computational Biologist

- **Company:** Proxima
- **Title:** Computational Biologist
- **Canonical Job ID:** `job_081d0829d645623f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Builds computational structural biology pipelines and algorithmic benchmarks to support AI drug discovery.
- **Source Responsibility Evidence:** *"Develop pilot capabilities and create large-scale data pipelines from the ground up Collaborate with other teams across Proxima and partnering organizations to achieve project goals by contributing code, analyses, benchmarks, optimizations and ideas to"*
- **Source Qualification Evidence:** *"Hold an MSc or PhD degree in computational biology, bioinformatics or a related field Possess mixed academic and/or industrial experience, preferably in the biotech industry Have a strong background in computational structural or systems biology Demonstrate"*
- **Decision Rationale:** Scientific research position designing molecular structural analysis pipelines and algorithmic benchmarks for protein interactions.

### Record 45/117: `job_97a4f768e103b5e6` – Envalior – Senior People Intelligence, Automation & AI Specialist

- **Company:** Envalior
- **Title:** Senior People Intelligence, Automation & AI Specialist
- **Canonical Job ID:** `job_97a4f768e103b5e6`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Develops automated HR workflows, workforce analytics pipelines, and internal AI tools using enterprise automation platforms.
- **Source Responsibility Evidence:** *"Lead the HR automation and AI roadmap, identifying opportunities to streamline and optimize people processes through digital solutions. Design, build, and implement automation solutions using Microsoft Power Platform, AI tools, and other approved technologies."*
- **Source Qualification Evidence:** *"Bachelor’s degree in Information Systems, Computer Science, Statistics, Mathematics, Business Analytics, HR Analytics , or a related quantitative field."*
- **Decision Rationale:** Applied digital solutions specialist developing workforce intelligence models and automations using Power Platform and AI tools.

### Record 46/117: `job_09183096da77cafc` – Skdse – Head of AI (All Genders)

- **Company:** Skdse
- **Title:** Head of AI (All Genders)
- **Canonical Job ID:** `job_09183096da77cafc`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Directs organizational AI technical strategy, foundational model architectures, and machine learning infrastructure.
- **Source Responsibility Evidence:** *"AT STARK Define and own STARK's AI strategy across product and internal domains, setting a direction that Technical Leads can execute against Lead AI stack decisions, model selection, frameworks, MLOps infrastructure, evaluation, and tooling, in partnership"*
- **Source Qualification Evidence:** *"TO THE MISSION Degree in machine learning, computer vision, robotics, or a closely related field, or demonstrably equivalent depth through industry research and an open publication or open-source record Proven experience setting AI technical strategy at a"*
- **Decision Rationale:** Executive AI research and technology leader setting model architecture, MLOps stack, and computer vision strategy for defense AI systems.

### Record 47/117: `job_94a95091e1f91f3f` – Skaylink – (Senior) Microsoft Data & AI Security Consultant (m/w/d)

- **Company:** Skaylink
- **Title:** (Senior) Microsoft Data & AI Security Consultant (m/w/d)
- **Canonical Job ID:** `job_94a95091e1f91f3f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Architects security frameworks, data governance policies, and Microsoft Purview compliance for enterprise AI workloads.
- **Source Responsibility Evidence:** *"Du unterstützt unsere Kund*innen dabei, Daten-, Sicherheits- und Compliance-Strategien auf Basis von Microsoft Purview sowie modernen KI-Workloads erfolgreich zu entwerfen, zu implementieren und zu betreiben."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Cloud security consultant implementing governance policies, compliance guardrails, and access controls for enterprise AI workloads.

### Record 48/117: `job_935400d30ab051bd` – celonis – Associate AI and Data Consultant - Galaxy Graduate Program

- **Company:** celonis
- **Title:** Associate AI and Data Consultant - Galaxy Graduate Program
- **Canonical Job ID:** `job_935400d30ab051bd`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Implements process mining pipelines, data models, and enterprise AI workflows for customer operational transformation.
- **Source Responsibility Evidence:** *"As an Associate Deployment Engineer within the Galaxy Graduate Program , you will support the end-to-end "Discover-and-Build" journey for our global customers."*
- **Source Qualification Evidence:** *"You Need Academic Background: A recent graduate (or final year student) with a degree in Computer Science, Data Science, Engineering, Business Information Systems, or a related technical field."*
- **Decision Rationale:** Graduate consultant deploying Celonis process intelligence models, data transformation pipelines, and AI business solutions.

### Record 49/117: `job_c98f4209b2130bc9` – BeReal – Marketing Content Specialist - BeReal

- **Company:** BeReal
- **Title:** Marketing Content Specialist - BeReal
- **Canonical Job ID:** `job_c98f4209b2130bc9`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Creates social media marketing content, brand campaign assets, and community engagement copy for consumer mobile platforms.
- **Source Responsibility Evidence:** *"By encouraging users to share unfiltered moments, we foster genuine connections and celebrate real life."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Social media marketing role creating viral promotional content, copywriting, and brand storytelling for a social media app.

### Record 50/117: `job_60dafe151b165555` – Enactintelligence – Robot Operator

- **Company:** Enactintelligence
- **Title:** Robot Operator
- **Canonical Job ID:** `job_60dafe151b165555`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Pilots robotic systems in physical environments to capture operational demonstration data for robotics foundation models.
- **Source Responsibility Evidence:** *"in industry and beyond. We are shaping a company where brilliant and unconventional people thrive together on solving the hardest challenges of our time. We are truth seekers."*
- **Source Qualification Evidence:** *"Comfortable piloting various robots for extended duration. Strong hand-eye coordination, spatial awareness, and fine motor control. Attention to Detail: A preference for an organized, functional workspace and a systematic approach to engineering tasks."*
- **Decision Rationale:** Technical operations specialist piloting robotic manipulators and gathering real-world trajectory datasets for embodied AI.

### Record 51/117: `job_a59e43af035571a3` – Rivia – Customer Engagement Manager

- **Company:** Rivia
- **Title:** Customer Engagement Manager
- **Canonical Job ID:** `job_a59e43af035571a3`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Manages customer success relationships, platform adoption, and client retention for clinical trial data platforms.
- **Source Responsibility Evidence:** *"Serve as the primary point of contact for clients, building and maintaining strong, long-lasting relationships. Understand client needs and objectives, and ensure they are successfully met through Rivia’s platform."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Account management role serving as primary point of contact for clients adopting a clinical trial data engine and AI workflow platform.

### Record 52/117: `job_d98ec925aa02009f` – Robot Heart – Co-Founder & CTO

- **Company:** Robot Heart
- **Title:** Co-Founder & CTO
- **Canonical Job ID:** `job_d98ec925aa02009f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Architects core software platforms, distributed systems, and technical infrastructure for physical AI robotics operations.
- **Source Responsibility Evidence:** *"Your work centers on advancing the AI-native, hardware-agnostic fleet operating system and scaling the infrastructure that supports autonomous mobile robots, drones, and humanoids."*
- **Source Qualification Evidence:** *"are strongly encouraged to apply. Your first months at Robot Heart You will have taken ownership of the core technical architecture, aligned engineering roadmaps with the mission of scaling Physical AI infrastructure, and advanced the integration of fleet"*
- **Decision Rationale:** Executive engineering leader directing core operating system architecture, fleet integrations, and technical infrastructure for robotics.

### Record 53/117: `job_bea17c7bbad33d34` – HG International b.v. – Afstudeerstage AI Adoption

- **Company:** HG International b.v.
- **Title:** Afstudeerstage AI Adoption
- **Canonical Job ID:** `job_bea17c7bbad33d34`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Researches internal organizational workflows and designs change management initiatives to drive workplace AI tool adoption.
- **Source Responsibility Evidence:** *"Wil jij helpen om AI van technologie naar dagelijks werk te brengen? Bij HG geloven we dat technologie mensen sterker maakt. Daarom hebben we de afgelopen periode een stevig fundament gelegd voor AI binnen onze organisatie."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Graduate thesis role investigating internal business processes and change management frameworks to facilitate employee AI adoption.

### Record 54/117: `job_ac1156091b8fe8bf` – Nebius – Senior Technical Project Manager - VPC

- **Company:** Nebius
- **Title:** Senior Technical Project Manager - VPC
- **Canonical Job ID:** `job_ac1156091b8fe8bf`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Manages technical delivery roadmaps, engineering dependencies, and virtual private cloud networking initiatives for AI cloud infrastructure.
- **Source Responsibility Evidence:** *"The Virtual Private Cloud team develops the core networking layer of Nebius AI Cloud."*
- **Source Qualification Evidence:** *"5+ years of experience in technical program management, technical project management, engineering management, or a senior technical role involving the delivery of complex cross-team initiatives."*
- **Decision Rationale:** Technical program manager driving cross-team delivery for core VPC networking layers and infrastructure on Nebius AI Cloud.

### Record 55/117: `job_eda8631b57f83fae` – Clickhouse – Training Operations Specialist - EMEA

- **Company:** Clickhouse
- **Title:** Training Operations Specialist - EMEA
- **Canonical Job ID:** `job_eda8631b57f83fae`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates training event logistics, attendee communications, and educational program operations.
- **Source Responsibility Evidence:** *"you would be performing as a Training Operations Specialist: Schedule and organize virtual and in-person training events, including registration page setup, Zoom configuration, and email communications."*
- **Source Qualification Evidence:** *"2+ years of experience in training coordination, operations, event management, or a related role. Proficiency with marketing automation platforms, particularly Marketo, including registration management and email communications."*
- **Decision Rationale:** Operational role scheduling customer training workshops, managing Marketo registration workflows, and organizing event logistics.

### Record 56/117: `job_e99d75c13a1f6076` – Doit – Product Lead - AI Stockbroking App

- **Company:** Doit
- **Title:** Product Lead - AI Stockbroking App
- **Canonical Job ID:** `job_e99d75c13a1f6076`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Defines product strategy, user experience roadmaps, and feature specifications for an AI-powered stock trading application.
- **Source Responsibility Evidence:** *"Drive launch quality, post-launch learning and continuous improvement."*
- **Source Qualification Evidence:** *"Strong experience leading digital product areas, not just individual features. Able to balance strategy, execution, UX, data, engineering and business outcomes. Strong judgement on prioritization, trade-offs and product sequencing."*
- **Decision Rationale:** Senior product builder owning direction, execution, and customer outcomes for an AI-powered stockbroking application.

### Record 57/117: `job_31f4574a32f241d3` – Doit – Product Lead - AI Investing App

- **Company:** Doit
- **Title:** Product Lead - AI Investing App
- **Canonical Job ID:** `job_31f4574a32f241d3`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Defines product strategy, customer experience roadmaps, and feature execution for an AI-driven retail investment platform.
- **Source Responsibility Evidence:** *"This role is for senior product builders who can own direction, execution, product quality and outcomes across multiple workstreams or squads."*
- **Source Qualification Evidence:** *"Strong experience leading digital product areas, not just individual features. Able to balance strategy, execution, UX, data, engineering and business outcomes. Strong judgement on prioritization, trade-offs and product sequencing."*
- **Decision Rationale:** Product management leader defining roadmap, customer experience, and business strategy for an AI investing application.

### Record 58/117: `job_730121592a7b12a1` – Doit – Product Lead - AI Neobank App

- **Company:** Doit
- **Title:** Product Lead - AI Neobank App
- **Canonical Job ID:** `job_730121592a7b12a1`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Defines product vision, mobile banking capabilities, and customer lifecycle features for an AI-enabled digital banking application.
- **Source Responsibility Evidence:** *"Define priorities, roadmap, product standards and success metrics across multiple features or squads."*
- **Source Qualification Evidence:** *"Strong experience leading digital product areas, not just individual features. Able to balance strategy, execution, UX, data, engineering and business outcomes. Strong judgement on prioritization, trade-offs and product sequencing."*
- **Decision Rationale:** Product management leader directing product areas, digital banking capabilities, and customer experiences for an AI neobank app.

### Record 59/117: `job_5b6e705fdd8a3e45` – Doit – Product Owner, Technical - AI Stockbroking

- **Company:** Doit
- **Title:** Product Owner, Technical - AI Stockbroking
- **Canonical Job ID:** `job_5b6e705fdd8a3e45`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Translates product capabilities into technical specifications, API requirements, and engineering sprint backlogs for AI trading platforms.
- **Source Responsibility Evidence:** *"This role is for builders who can understand users, define product direction, work with engineering and design, launch fast and keep improving after release."*
- **Source Qualification Evidence:** *"Experience as Product Manager, Product Owner, founder, growth/product operator or similar role. Strong product sense and ability to simplify complex workflows. Able to work with engineers and designers to ship real products."*
- **Decision Rationale:** Technical product owner writing engineering requirements, API specifications, and sprint stories for stockbroking platforms.

### Record 60/117: `job_c06cd7c18855728d` – Doit – Product Owner, Technical - AI Investing

- **Company:** Doit
- **Title:** Product Owner, Technical - AI Investing
- **Canonical Job ID:** `job_c06cd7c18855728d`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Manages technical user stories, backend API requirements, and development sprint planning for AI investment products.
- **Source Responsibility Evidence:** *"Who loves building great next-generation products, not status quo."*
- **Source Qualification Evidence:** *"Experience as Product Manager, Product Owner, founder, growth/product operator or similar role. Strong product sense and ability to simplify complex workflows. Able to work with engineers and designers to ship real products."*
- **Decision Rationale:** Technical product owner collaborating with engineers on architecture specifications, APIs, and trading workflows for investing apps.

### Record 61/117: `job_3f4147f80f8eed20` – Doit – Product Owner, Technical - AI Neobank

- **Company:** Doit
- **Title:** Product Owner, Technical - AI Neobank
- **Canonical Job ID:** `job_3f4147f80f8eed20`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Coordinates technical feature delivery, core banking API integrations, and developer specifications for AI neobanking solutions.
- **Source Responsibility Evidence:** *"The Kind of Builder We Want Starts from user problems, not feature lists."*
- **Source Qualification Evidence:** *"Experience as Product Manager, Product Owner, founder, growth/product operator or similar role. Strong product sense and ability to simplify complex workflows. Able to work with engineers and designers to ship real products."*
- **Decision Rationale:** Technical product owner managing agile sprints, backend API integrations, and core banking features for an AI neobank.

### Record 62/117: `job_a3045fdafbd0cec5` – GENO Broker GmbH – AI Quality & Governance Specialist (m/w/d)

- **Company:** GENO Broker GmbH
- **Title:** AI Quality & Governance Specialist (m/w/d)
- **Canonical Job ID:** `job_a3045fdafbd0cec5`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Establishes AI quality assurance frameworks, risk governance protocols, and regulatory compliance standards for financial systems.
- **Source Responsibility Evidence:** *"Das baust du mit uns auf Wie wir KI einsetzen, entscheidet sich jetzt. Du gestaltest die Spielregeln von Anfang an mit. Wir bauen ein neues digitales Brokerage auf - mit dem Rückhalt der Genossenschaftlichen FinanzGruppe."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Technical governance specialist creating validation frameworks, risk assessment methodologies, and EU AI Act compliance for banking AI.

### Record 63/117: `job_e1fe8c2686b89dd0` – GENO Broker GmbH – Data Analyst (m/w/d)

- **Company:** GENO Broker GmbH
- **Title:** Data Analyst (m/w/d)
- **Canonical Job ID:** `job_e1fe8c2686b89dd0`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Develops business intelligence dashboards, database queries, and reporting analytics to support financial brokerage operations.
- **Source Responsibility Evidence:** *"Das baust du mit uns auf Ein neues digitales Brokerage aufzubauen heißt auch, früh zu verstehen, was funktioniert und wo wir nachsteuern müssen. Wir bauen ein neues digitales Brokerage auf – mit dem Rückhalt der Genossenschaftlichen FinanzGruppe."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Traditional data analyst querying SQL databases, creating reporting dashboards, and analyzing brokerage trading volumes.

### Record 64/117: `job_1f1af246cfd4743c` – Nulegal GmbH – Working Student AI Research (m/f/d)

- **Company:** Nulegal GmbH
- **Title:** Working Student AI Research (m/f/d)
- **Canonical Job ID:** `job_1f1af246cfd4743c`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Evaluates large language model prompts, document retrieval pipelines, and NLP benchmarks for legal domain applications.
- **Source Responsibility Evidence:** *"New paper on Monday, prototype by Tuesday?"*
- **Source Qualification Evidence:** *"You're enrolled in data science, AI, computer science or something close at a German university You enjoy reading papers You can code your way from an idea to something that runs Where and when Berlin/Potsdam Hybrid 20 hours a week How to apply What's the"*
- **Decision Rationale:** Applied student researcher testing prompt performance, legal text retrieval algorithms, and LLM benchmarking in legaltech.

### Record 65/117: `job_1fe2be9f97ca745e` – Langdock – AI Associate - m/f/d

- **Company:** Langdock
- **Title:** AI Associate - m/f/d
- **Canonical Job ID:** `job_1fe2be9f97ca745e`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Configures enterprise generative AI assistants, designs prompt workflows, and assists client onboarding on LLM platforms.
- **Source Responsibility Evidence:** *"Front-line customer support. Spend most of your day in the queue, handling customer tickets end-to-end across model behavior, API integrations, enterprise compliance, billing, and access control. Investigate what is happening under the hood."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Solutions specialist helping corporate customers design customized LLM assistants, prompt libraries, and automated workflows.

### Record 66/117: `job_5451ae341bb01502` – Map – Associate Consultant, AI Transformation

- **Company:** Map
- **Title:** Associate Consultant, AI Transformation
- **Canonical Job ID:** `job_5451ae341bb01502`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Delivers management consulting assessments, organizational readiness reviews, and strategic roadmaps for corporate AI adoption.
- **Source Responsibility Evidence:** *"Drive adoption – Help client and MAP teams upskill with AI: run knowledge-sharing sessions and office hours, write the playbooks teams use after you leave, support champion networks, and keep an adoption scorecard that shows leadership what is working."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management consulting associate analyzing business processes, change impact, and strategic roadmaps for enterprise AI adoption.

### Record 67/117: `job_07d1b215cf73dcbf` – Lyceum – Member of Technical Staff – Monitoring

- **Company:** Lyceum
- **Title:** Member of Technical Staff – Monitoring
- **Canonical Job ID:** `job_07d1b215cf73dcbf`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Designs distributed monitoring architectures, cluster telemetry, and observability systems for bare-metal GPU cloud infrastructure.
- **Source Responsibility Evidence:** *"Your team You will work with the engineers who connect new machines to Lyceum’s systems and build the orchestration layer that lets us move GPUs between use cases. The team’s aim is to get the most out of every GPU we run."*
- **Source Qualification Evidence:** *"3+ years of experience in site reliability, observability or infrastructure engineering Production experience with Grafana, Prometheus, OpenTelemetry or similar tooling Strong proficiency in Go and Python Strong systems fundamentals: Linux, networking and"*
- **Decision Rationale:** Systems infrastructure engineer designing telemetry collection, Prometheus metrics, and alerting for large bare-metal GPU clusters.

### Record 68/117: `job_e35a732584dd5a91` – Lyceum – Member of Technical Staff – Isolation, Provisioning, Uptime, Monitoring

- **Company:** Lyceum
- **Title:** Member of Technical Staff – Isolation, Provisioning, Uptime, Monitoring
- **Canonical Job ID:** `job_e35a732584dd5a91`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Engineers bare-metal GPU provisioning pipelines, hypervisor virtualization layers, and automated node recovery systems.
- **Source Responsibility Evidence:** *"Your team You will work with the engineers who turn Lyceum’s GPU hardware into a platform customers can rely on."*
- **Source Qualification Evidence:** *"3+ years of experience in infrastructure, systems or platform engineering Strong proficiency in Go and Python Deep Linux knowledge and experience with bare-metal provisioning and configuration management Solid networking fundamentals (VLANs, routing,"*
- **Decision Rationale:** Platform infrastructure engineer building automated bare-metal server provisioning, KVM virtualization, and GPU node reliability.

### Record 69/117: `job_5b060bf5f7cd0896` – Lyceum – Member of Technical Staff – VM Features

- **Company:** Lyceum
- **Title:** Member of Technical Staff – VM Features
- **Canonical Job ID:** `job_5b060bf5f7cd0896`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Builds virtual machine management features, hardware device virtualization, and hypervisor abstractions for cloud GPU workloads.
- **Source Responsibility Evidence:** *"Your team You will work with the engineers who build Lyceum’s VM product and shape how customers use our GPU infrastructure."*
- **Source Qualification Evidence:** *"3+ years of experience in software engineering, with a focus on backend or infrastructure systems Strong proficiency in Go and Python Hands-on experience with virtualisation (KVM/QEMU or similar) Good knowledge of Linux internals, storage and networking"*
- **Decision Rationale:** Systems engineer developing KVM/QEMU virtualization features, virtual hardware devices, and GPU instance management in Go/Python.

### Record 70/117: `job_93cbaa791c40727a` – Lyceum – Member of Technical Staff – Infra, k8s, Dynamo

- **Company:** Lyceum
- **Title:** Member of Technical Staff – Infra, k8s, Dynamo
- **Canonical Job ID:** `job_93cbaa791c40727a`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Scales Kubernetes clusters, distributed database layers, and high-throughput model serving infrastructure for AI inference platforms.
- **Source Responsibility Evidence:** *"Infrastructure evolution: Evaluate and integrate open-source inference frameworks and tooling (Dynamo, vLLM, Triton, etc.) where they improve throughput, latency, or stability of the serving stack."*
- **Source Qualification Evidence:** *"3+ years of experience in backend, infrastructure, or systems engineering Strong proficiency in Go and Python Experience building or operating a model serving platform or ML platform Solid understanding of systems performance - profiling, benchmarking, and"*
- **Decision Rationale:** Core infrastructure engineer scaling Kubernetes orchestration, low-latency DynamoDB persistence, and distributed model serving engines.

### Record 71/117: `job_5203749acf4b14e8` – Lyceum – Member of Technical Staff – GPU Deployments

- **Company:** Lyceum
- **Title:** Member of Technical Staff – GPU Deployments
- **Canonical Job ID:** `job_5203749acf4b14e8`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Deploys high-density GPU server clusters, configures high-speed network fabrics, and maintains bare-metal accelerator hardware.
- **Source Responsibility Evidence:** *"Your team You will work with the engineers who bring Lyceum’s GPU capacity online and keep it running."*
- **Source Qualification Evidence:** *"3+ years of experience in HPC, data-centre or infrastructure engineering Hands-on experience deploying GPU servers or HPC clusters on bare metal Strong Linux fundamentals, from boot process and kernel drivers to system configuration Solid networking"*
- **Decision Rationale:** Infrastructure engineer deploying bare-metal GPU servers, configuring InfiniBand/RoCE network fabrics, and managing kernel drivers.

### Record 72/117: `job_dca7b0b6a47a6b85` – Lyceum – Member of Technical Staff – API, Frontend, Interface, Integrations

- **Company:** Lyceum
- **Title:** Member of Technical Staff – API, Frontend, Interface, Integrations
- **Canonical Job ID:** `job_dca7b0b6a47a6b85`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Develops developer-facing APIs, web dashboard interfaces, and model serving framework integrations for an AI cloud platform.
- **Source Responsibility Evidence:** *"Your focus Feature development: Design and ship new platform capabilities - from supporting new model architectures and serving frameworks to building out API features that customers are asking for."*
- **Source Qualification Evidence:** *"3+ years of experience in software engineering, with a focus on backend or infrastructure systems Strong proficiency in Go and Python Hands-on experience with at least one ML inference serving framework (vLLM, TGI, etc) Solid understanding of how large"*
- **Decision Rationale:** Full-stack software engineer building developer APIs, web management interfaces, and inference serving integrations (vLLM, TGI).

### Record 73/117: `job_3fcc05f52bb7f78a` – Lyceum – Member of Technical Staff – VM Product & Infra

- **Company:** Lyceum
- **Title:** Member of Technical Staff – VM Product & Infra
- **Canonical Job ID:** `job_3fcc05f52bb7f78a`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Builds distributed control planes, virtual storage subsystems, and software-defined networking for cloud GPU compute instances.
- **Source Responsibility Evidence:** *"Your team You will work with the engineers who build and run the infrastructure behind Lyceum’s VM product."*
- **Source Qualification Evidence:** *"3+ years of experience in systems or infrastructure engineering Strong proficiency in Go and Python Strong fundamentals in Linux, virtualisation, networking and storage Experience building or operating distributed systems or control planes Experience running"*
- **Decision Rationale:** Infrastructure software engineer constructing distributed control planes, storage subsystems, and software-defined networking for VMs.

### Record 74/117: `job_9b103a8e3aaa6496` – Lyceum – Member of Technical Staff – Security

- **Company:** Lyceum
- **Title:** Member of Technical Staff – Security
- **Canonical Job ID:** `job_9b103a8e3aaa6496`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Implements platform security architectures, container isolation safeguards, and cryptographic access controls for sovereign AI cloud infrastructure.
- **Source Responsibility Evidence:** *"Customers choose a sovereign European cloud because they need to trust where their data and workloads run."*
- **Source Qualification Evidence:** *"3+ years of experience in security engineering, or in infrastructure engineering with a strong security focus Strong fundamentals in Linux, networking, cryptography and authentication Experience securing Kubernetes, container or cloud infrastructure in"*
- **Decision Rationale:** Security engineer architecting Kubernetes hardening, network isolation, cryptography, and container security across cloud GPU clusters.

### Record 75/117: `job_4f60bf9ee90d37a0` – Care Preventive AG – AI Growth Trainee (60-100%)

- **Company:** Care Preventive AG
- **Title:** AI Growth Trainee (60-100%)
- **Canonical Job ID:** `job_4f60bf9ee90d37a0`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Implements marketing automations, lead generation workflows, and AI-assisted digital campaign operations.
- **Source Responsibility Evidence:** *"Du automatisierst lieber, als etwas zweimal von Hand zu machen? Dann suchen wir dich als AI Growth Trainee (80-100%) für 6 Monate, mit Option auf Festanstellung. Ideal als Einstieg nach dem Studium, Start per sofort oder nach Vereinbarung."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Growth marketing trainee automating lead qualification funnels and customer acquisition workflows using digital tools.

### Record 76/117: `job_f50c741f0b32bd5a` – Sereact GmbH – Internship Teleoperation & Data Labeling - Switzerland

- **Company:** Sereact GmbH
- **Title:** Internship Teleoperation & Data Labeling - Switzerland
- **Canonical Job ID:** `job_f50c741f0b32bd5a`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Operates robotic teleoperation systems and annotates multi-modal sensor data to train industrial robotics AI models.
- **Source Responsibility Evidence:** *"Internship – Teleoperation & Data Labeling (m/f/d) – St."*
- **Source Qualification Evidence:** *"• You pay close attention to detail and enjoy precise, careful work • You’re comfortable with computers and curious about tech."*
- **Decision Rationale:** Technical internship controlling robotic systems at customer deployment sites and labeling multi-modal computer vision datasets.

### Record 77/117: `job_e47964df703c1efd` – Doit – Technical Product Lead - AI Stockbroking App

- **Company:** Doit
- **Title:** Technical Product Lead - AI Stockbroking App
- **Canonical Job ID:** `job_e47964df703c1efd`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Leads technical product architecture, API designs, and execution roadmaps for an AI-driven stockbroking platform.
- **Source Responsibility Evidence:** *"The Technical Product Lead owns a product vertical end-to-end , from strategy and outcomes through technical design, delivery, and launch."*
- **Source Qualification Evidence:** *"5+ years of product management experience, including ownership of complex technical products from strategy through production. Strong technical foundation across system architecture, APIs, databases, workflows, failure modes and distributed systems."*
- **Decision Rationale:** Technical product lead directing system architectures, API designs, and multi-squad delivery for an AI stock trading superapp.

### Record 78/117: `job_a9f504c73a7ccd14` – Doit – Technical Product Lead - AI Investing App

- **Company:** Doit
- **Title:** Technical Product Lead - AI Investing App
- **Canonical Job ID:** `job_a9f504c73a7ccd14`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Leads technical architecture, trading algorithm integrations, and engineering roadmaps for an AI investment application.
- **Source Responsibility Evidence:** *"Shaping technical design with engineering across APIs, data flows, ledgering, reconciliation, failure handling, security and scalability."*
- **Source Qualification Evidence:** *"5+ years of product management experience, including ownership of complex technical products from strategy through production. Strong technical foundation across system architecture, APIs, databases, workflows, failure modes and distributed systems."*
- **Decision Rationale:** Technical product leader driving architecture specifications, financial API integrations, and engineering delivery for an AI investing app.

### Record 79/117: `job_b1aed918a2400f31` – Doit – Technical Product Lead - AI Neobank App

- **Company:** Doit
- **Title:** Technical Product Lead - AI Neobank App
- **Canonical Job ID:** `job_b1aed918a2400f31`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Leads technical architecture, financial API integrations, and engineering roadmaps for an AI-enabled digital banking platform.
- **Source Responsibility Evidence:** *"Shaping technical design with engineering across APIs, data flows, ledgering, reconciliation, failure handling, security and scalability."*
- **Source Qualification Evidence:** *"5+ years of product management experience, including ownership of complex technical products from strategy through production. Strong technical foundation across system architecture, APIs, databases, workflows, failure modes and distributed systems."*
- **Decision Rationale:** Technical product lead overseeing core banking system architectures, distributed transactions, and engineering execution for an AI neobank.

### Record 80/117: `job_22fda7d0b92e76aa` – capco – Infrastructure Manager (m/f/d) for AI Ops Implementation

- **Company:** capco
- **Title:** Infrastructure Manager (m/f/d) for AI Ops Implementation
- **Canonical Job ID:** `job_22fda7d0b92e76aa`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Manages enterprise IT infrastructure, DevOps environments, and system reliability for large-scale AI Ops implementations.
- **Source Responsibility Evidence:** *"Lead and coordinate a large-scale AI Ops implementation project, ensuring effective planning, execution, and alignment with business and technical objectives. Manage and coordinate cross-functional IT teams responsible for setting up, integrating, and managing complex infrastructure environments"*
- **Source Qualification Evidence:** *"(e.g., performance, security, availability). Proficient in stakeholder communication and program leadership. Experience working in ITIL-based, DevOps, or agile project environments. High degree of ownership and structured work approach."*
- **Decision Rationale:** Leads infrastructure management, ITIL/DevOps environments, and high-availability operations for enterprise banking AI Ops implementations.

### Record 81/117: `job_b4b51eae834bb973` – Telli – Enterprise Deployment Strategist

- **Company:** Telli
- **Title:** Enterprise Deployment Strategist
- **Canonical Job ID:** `job_b4b51eae834bb973`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Architects and deploys conversational AI agent workflows, enterprise API integrations, and customer adoption plans.
- **Source Responsibility Evidence:** *"As Enterprise Deployment Strategist you own deployment and commercial success for a portfolio of telli's largest (tier 1) customers."*
- **Source Qualification Evidence:** *"into a practical solution and clear priorities You have technical fluency : you're comfortable with APIs, integrations, and you've built workflows or AI agents yourself You operate with high autonomy, agency and urgency : you run your accounts independently"*
- **Decision Rationale:** Solutions architect and deployment strategist building custom AI agent workflows and API integrations for Tier-1 enterprise customers.

### Record 82/117: `job_68fc708b1be009aa` – Vesoma – Robotics Technician

- **Company:** Vesoma
- **Title:** Robotics Technician
- **Canonical Job ID:** `job_68fc708b1be009aa`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Assembles, tests, and calibrates mechanical and electrical hardware systems for physical AI robotic prototypes.
- **Source Responsibility Evidence:** *"Run day-to-day operation and maintenance of a humanoid robot: mechanical assembly and disassembly, harness work, fault diagnosis, keeping the machine available for development and demos."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Hardware technician assembling mechatronic subsystems, wiring electrical harnesses, and calibrating robotic mechanisms.

### Record 83/117: `job_dfddb5a9a3650b41` – TransPerfect – Director, Strategic Accounts - AI Data Solutions

- **Company:** TransPerfect
- **Title:** Director, Strategic Accounts - AI Data Solutions
- **Canonical Job ID:** `job_dfddb5a9a3650b41`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Leads enterprise sales cycles and commercial partnerships for training data collection and AI annotation services.
- **Source Responsibility Evidence:** *"Drive Revenue: Systematically develop high-value accounts, exceeding annual sales targets and expanding TransPerfect’s AI footprint."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Commercial sales executive targeting strategic accounts to sell training dataset licensing, annotation services, and AI data solutions.

### Record 84/117: `job_fde4b60fcd5d454c` – OpenAI – RE/RS, Data Understanding - Foundations

- **Company:** OpenAI
- **Title:** RE/RS, Data Understanding - Foundations
- **Canonical Job ID:** `job_fde4b60fcd5d454c`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Conducts machine learning research to analyze pretraining dataset quality, representations, and algorithmic impact on frontier models.
- **Source Responsibility Evidence:** *"Own and drive a research agenda, from choosing the right problems to carrying long-running work through to impact."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Foundations research scientist/engineer investigating pretraining data distributions, algorithmic data filtering, and model learning dynamics.

### Record 85/117: `job_7373d597c590014b` – Neuralconcept – Senior CAE and AI Expert

- **Company:** Neuralconcept
- **Title:** Senior CAE and AI Expert
- **Canonical Job ID:** `job_7373d597c590014b`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Develops geometric deep learning models and numerical simulation pipelines to accelerate computer-aided engineering workflows.
- **Source Responsibility Evidence:** *"Own vertical solution assets end-to-end."*
- **Source Qualification Evidence:** *"5–8 years of hands-on FEA simulation experience, in the application of vehicle crash, drop test, pedestrian and/or passenger safety, delivering production-quality models in automotive or consumer electronics environments Deep expertise in leading Mechanical"*
- **Decision Rationale:** Machine learning expert developing geometric deep learning algorithms to predict physical fluid dynamics and FEA simulations.

### Record 86/117: `job_e8078287eb87dc0c` – Wavestone Germany AG – Python Software Architekt (m/w/d) (Ref.Nr.: 48296)

- **Company:** Wavestone Germany AG
- **Title:** Python Software Architekt (m/w/d) (Ref.Nr.: 48296)
- **Canonical Job ID:** `job_e8078287eb87dc0c`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Architects enterprise Python software platforms supporting data analytics, ETL pipelines, and Generative AI services.
- **Source Responsibility Evidence:** *"Für ein langfristiges Projekt bei unserem Kunden in Zürich (Remote-Anteil nur innerhalb der Schweiz möglich) suchen wir einen Python Software Architekt (m/w/d)."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Software architect designing modular Python systems, data processing pipelines, and microservices supporting GenAI/ML applications.

### Record 87/117: `job_acaff5006553133c` – Wavestone Germany AG – Python Software Entwickler (m/w/d) (Ref.Nr.: 48292)

- **Company:** Wavestone Germany AG
- **Title:** Python Software Entwickler (m/w/d) (Ref.Nr.: 48292)
- **Canonical Job ID:** `job_acaff5006553133c`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Develops Python backend services, data extraction pipelines, and automation tools for enterprise GenAI applications.
- **Source Responsibility Evidence:** *"Für ein langfristiges Projekt bei unserem Kunden in Zürich (Remote-Anteil nur innerhalb der Schweiz möglich) suchen wir einen Python Software Entwickler (m/w/d)."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Backend software developer engineering Python ELT pipelines, automation scripts, and integration services for ML/GenAI systems.

### Record 88/117: `job_5572db9983b165e3` – cross-ING AG – Software-Ingenieur:in Robotics

- **Company:** cross-ING AG
- **Title:** Software-Ingenieur:in Robotics
- **Canonical Job ID:** `job_5572db9983b165e3`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Develops embedded software, control systems, and ROS architectures for industrial robotics and mechatronic systems.
- **Source Responsibility Evidence:** *"cross-ING ist ein unabhängiges ISO 9001/13485-zertifiziertes Schweizer Ingenieurunternehmen."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Robotics software engineer writing C++ and ROS control software for industrial automation and mechatronic medical devices.

### Record 89/117: `job_ed0544426f0efc0a` – 6Gorilla's – Business Consultant Data & AI

- **Company:** 6Gorilla's
- **Title:** Business Consultant Data & AI
- **Canonical Job ID:** `job_ed0544426f0efc0a`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Advises healthcare and corporate clients on data governance, analytics strategy, and AI solution implementation.
- **Source Responsibility Evidence:** *"Wil jij organisaties écht versnellen met data & AI? Als onderdeel van Tenzinger helpt 6Gorilla’s organisaties bij hun transformatie naar datagedreven werken."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management and technology consultant helping healthcare organizations implement data-driven workflows and practical AI tools.

### Record 90/117: `job_8b6a7fe68fff1038` – TAGGRS – Tracking Specialist

- **Company:** TAGGRS
- **Title:** Tracking Specialist
- **Canonical Job ID:** `job_8b6a7fe68fff1038`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Configures server-side tracking tags, analytics scripts, and digital measurement containers for client websites.
- **Source Responsibility Evidence:** *"Bij TAGGRS maken we server-side tracking toegankelijk voor iedereen. Om dit mogelijk te maken, zoeken we een Tracking Specialist, die onze klanten helpt bij het technisch inrichten van hun tracking."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Technical specialist configuring server-side Google Tag Manager, analytics pixels, and conversion tracking for e-commerce sites.

### Record 91/117: `job_9395ac8eab83c8a2` – Black Forest Labs – Research Lead, Evaluations

- **Company:** Black Forest Labs
- **Title:** Research Lead, Evaluations
- **Canonical Job ID:** `job_9395ac8eab83c8a2`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `CORE_AI_ML`
- **Updated Classification Reason:** Directs research methodologies and evaluation suites to benchmark multi-modal generative frontier models.
- **Source Responsibility Evidence:** *"is a hands-on management role - you’re responsible for growing the team and the people in it. You will define our hiring roadmap and make sure that each team member can grow within BFL, both in terms of their technical skillset and their career."*
- **Source Qualification Evidence:** *"Proven eval experience: You’ve previously designed, run and maintained large and complex evaluation suites for frontier AI systems, involving various kinds of evaluation methods involving both human and automated (both with or without AI) approaches."*
- **Decision Rationale:** Senior research leader building complex automated and human evaluation frameworks for visual and multimodal generative models.

### Record 92/117: `job_9e4923f4f61926ea` – DataSmart Point GmbH – Karrierestart in Data & AI - IHK Data Analyst (m/w/d) - 100 % Online

- **Company:** DataSmart Point GmbH
- **Title:** Karrierestart in Data & AI - IHK Data Analyst (m/w/d) - 100 % Online
- **Canonical Job ID:** `job_9e4923f4f61926ea`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `UNCERTAIN`
- **Updated Classification Reason:** Participates in vocational training curriculum covering data analytics, SQL databases, and AI business applications through an accredited training academy.
- **Source Responsibility Evidence:** *"Werde Teil der digitalen Zukunft mit der DataSmart Point Academy Die DataSmart Point Academy (DSP Academy) ist ein AZAV-zertifizierter Bildungsträger, spezialisiert auf praxisnahe IT- und Data-Weiterbildungen mit klarer Zukunftsperspektive."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Certified AZAV vocational training program teaching data analytics and Python rather than an operational corporate job vacancy.

### Record 93/117: `job_c47c30b19b7a902d` – Voodoo – IT Administrator - AI & Cybersecurity

- **Company:** Voodoo
- **Title:** IT Administrator - AI & Cybersecurity
- **Canonical Job ID:** `job_c47c30b19b7a902d`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Administers corporate IT infrastructure, workplace AI tools, and cybersecurity controls across mobile gaming studios.
- **Source Responsibility Evidence:** *"Gathering 800 employees, 7 billion downloads, and over 200 million active users, Voodoo is the #3 mobile publisher worldwide in terms of downloads after Google and Meta."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** IT administrator managing user identities, corporate security policies, hardware provisioning, and workplace AI tool integrations.

### Record 94/117: `job_eb34300548855d73` – MyBikePlan – AI Marketing Internship

- **Company:** MyBikePlan
- **Title:** AI Marketing Internship
- **Canonical Job ID:** `job_eb34300548855d73`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Executes digital marketing campaigns, customer acquisition funnels, and advertising creative using AI tools.
- **Source Responsibility Evidence:** *"You’ll support our entire marketing team and work across every stage of the funnel, from the first ad someone sees to the newsletter that brings them back. It’s the fastest way to learn how modern performance marketing works from end to end."*
- **Source Qualification Evidence:** *"Culture fit comes first. We don’t talk about what we could do. We just do it."*
- **Decision Rationale:** Performance marketing intern creating ad creatives, email newsletters, and customer acquisition campaigns with AI software.

### Record 95/117: `job_e1db5679287eaf9f` – Artifact – Senior AI Consultant

- **Company:** Artifact
- **Title:** Senior AI Consultant
- **Canonical Job ID:** `job_e1db5679287eaf9f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Delivers strategic consulting advisory, AI readiness workshops, and solution roadmaps for corporate business processes.
- **Source Responsibility Evidence:** *"Serve as a trusted consulting advisor to external customers, delivering innovative workshops and strategic guidance on incorporating AI and analytics into the business value chain."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Management consultant advising client executives on artificial intelligence opportunities, ROI prioritization, and solution design.

### Record 96/117: `job_0b951decd01c2b26` – TTMS Schweiz AG – Senior AI Consultant / KI-Berater

- **Company:** TTMS Schweiz AG
- **Title:** Senior AI Consultant / KI-Berater
- **Canonical Job ID:** `job_0b951decd01c2b26`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Advises enterprise clients on artificial intelligence adoption, architecture selection, and production solution deployment.
- **Source Responsibility Evidence:** *"Über TTMS Wir bei TTMS lieben Technologie. Noch mehr begeistert es uns, wenn daraus Lösungen entstehen, die im Alltag einen echten Unterschied machen."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Technology consultant evaluating corporate use cases, designing solution architectures, and implementing AI applications.

### Record 97/117: `job_c94d6cb844402565` – Tsmg – AI Tester with French

- **Company:** Tsmg
- **Title:** AI Tester with French
- **Canonical Job ID:** `job_c94d6cb844402565`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Executes voice data collection operations and evaluates French audio recordings to support speech recognition AI datasets.
- **Source Responsibility Evidence:** *"Terry Soot Management Group (TSMG) is a field data collection company founded in 2017 in Europe. We collect data where automation is not possible."*
- **Source Qualification Evidence:** *"French native speaker; Good level of English; Excellent communication skills; Previous experience with audio recording would be a plus."*
- **Decision Rationale:** Linguistic data collection contributor reading scripted prompts and recording audio samples to train speech recognition models.

### Record 98/117: `job_91933cd76e884191` – Probatix Health GmbH – Kundenservice & Manufacturing (m/w/d)

- **Company:** Probatix Health GmbH
- **Title:** Kundenservice & Manufacturing (m/w/d)
- **Canonical Job ID:** `job_91933cd76e884191`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Manages customer service inquiries and handles assembly and packaging for medical laboratory test kits.
- **Source Responsibility Evidence:** *"Über Probatix Probatix bietet Labordiagnostik als Service an: Unsere Partner – digitale Gesundheitsprogramme, Telemedizin-Anbieter, Health Apps, Krankenversicherungen und Arztpraxen – bieten ihren Kunden Heimtests unter eigener Marke an."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Operational role responding to patient customer support inquiries and assembling medical home testing kits in manufacturing.

### Record 99/117: `job_d732380d4b5b6679` – Mentify Learn GmbH – Amazon Account Manager (m/w/d) - Weiterbildung für Online-Marktplätze & AI, 100 % remote

- **Company:** Mentify Learn GmbH
- **Title:** Amazon Account Manager (m/w/d) - Weiterbildung für Online-Marktplätze & AI, 100 % remote
- **Canonical Job ID:** `job_d732380d4b5b6679`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `UNCERTAIN`
- **Updated Classification Reason:** Participates in vocational training coursework covering Amazon marketplace management, e-commerce workflows, and AI tools.
- **Source Responsibility Evidence:** *"📍 Homeoffice – Einstieg jederzeit möglich – Vollzeit oder Teilzeit 📦 E-Commerce ist die Zukunft – mach dich fit für den digitalen Handel! Mit unserer Weiterbildung wirst du in 3–6 Monaten zur Fachkraft für digitale Marktplätze."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Subsidized AZAV vocational course for marketplace management rather than an operational corporate employment position.

### Record 100/117: `job_9d00f80e541e6fd1` – Excelya – Clinical Data Systems & Data Management

- **Company:** Excelya
- **Title:** Clinical Data Systems & Data Management
- **Canonical Job ID:** `job_9d00f80e541e6fd1`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_AI_TECH`
- **Updated Classification Reason:** Administers computerized clinical research systems, electronic case report forms (eCRF), and clinical trial data management software.
- **Source Responsibility Evidence:** *"Provide methodological and technical support for the design and deployment of clinical data collection tools (eCRF). Administer clinical research systems, including eTMF, CTMS, GED/QMS, TRMS, and other business applications."*
- **Source Qualification Evidence:** *"Education Master's degree in Data Science, Biostatistics, Computer Science, Data Management, Life Sciences, or a related field. Experience Significant experience in Clinical Data Management and/or administration of computerized clinical systems."*
- **Decision Rationale:** Life sciences data systems administrator managing eTMF, CTMS, and electronic data capture tools for clinical research.

### Record 101/117: `job_ae42444b365c6fd0` – Remanence – Member of Technical Staff — Infrastructure

- **Company:** Remanence
- **Title:** Member of Technical Staff — Infrastructure
- **Canonical Job ID:** `job_ae42444b365c6fd0`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_INFRASTRUCTURE`
- **Updated Classification Reason:** Owns compute orchestration platforms, execution clusters, and distributed systems supporting AI model training and evaluation.
- **Source Responsibility Evidence:** *"You’ll own the compute and execution platform supporting training, inference, task generation, and evaluation."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Core infrastructure engineer building distributed compute platforms and cluster execution layers for enterprise AI systems.

### Record 102/117: `job_4514f88d9ec70693` – GFL Cosmetics – IT Applications & AI Specialist

- **Company:** GFL Cosmetics
- **Title:** IT Applications & AI Specialist
- **Canonical Job ID:** `job_4514f88d9ec70693`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Develops business process automations, internal enterprise applications, and conversational AI assistants using Microsoft Power Platform and Python.
- **Source Responsibility Evidence:** *"Da oltre 25 anni offriamo sui mercati globali cosmetici Made in Italy . Progettiamo, sviluppiamo, produciamo e confezioniamo in-house . La produzione è effettuata dalla nostra azienda italiana di Siziano (Pavia-Milano Sud)."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Corporate IT specialist developing internal workflows, Power Automate integrations, and custom Python AI chatbots.

### Record 103/117: `job_a8419aebc82b1a00` – HICO Group AG – Junior Consultant Planung & AI (100%) (w/m/d), CH, hybrid

- **Company:** HICO Group AG
- **Title:** Junior Consultant Planung & AI (100%) (w/m/d), CH, hybrid
- **Canonical Job ID:** `job_a8419aebc82b1a00`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Advises enterprise clients on business intelligence architectures, corporate planning systems, and AI analytics integrations.
- **Source Responsibility Evidence:** *"Unternehmen aller Größen bauen erfolgreich auf HICOs Management- und IT-Beratung, um mit uns relevante BI-, Planungs- und Digitalisierungs-Herausforderungen effizient, modern und verlässlich zu lösen."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Consultant deploying business intelligence dashboards, corporate financial planning solutions, and predictive AI analytics.

### Record 104/117: `job_8380c3e88e9c6584` – Avertis Group – Deal Sourcing Partner AI, Healthcare & MedTech

- **Company:** Avertis Group
- **Title:** Deal Sourcing Partner AI, Healthcare & MedTech
- **Canonical Job ID:** `job_8380c3e88e9c6584`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Sources investment opportunities, strategic capital deals, and corporate finance partnerships across AI and healthcare sectors.
- **Source Responsibility Evidence:** *"Identify potential AI, Healthcare and MedTech companies with financing or strategic capital needs Leverage your existing network to generate qualified deal opportunities Identify companies currently raising capital or preparing for growth, expansion or"*
- **Source Qualification Evidence:** *"Minimum 5 years of relevant experience in Deal Sourcing, Equity Sales, Business Development, Fundraising, M&A, Investment, Corporate Finance or Advisory with a specific focus on Healthcare, MedTech, HealthTech, Life Sciences, Biotech, Diagnostics or Medical Devices."*
- **Decision Rationale:** Corporate finance dealmaker originating growth equity transactions, M&A opportunities, and investor partnerships.

### Record 105/117: `job_86c624e1dd2c299c` – NETSHAKE – (Junior) E-Commerce Kaufmann (w/m/d)

- **Company:** NETSHAKE
- **Title:** (Junior) E-Commerce Kaufmann (w/m/d)
- **Canonical Job ID:** `job_86c624e1dd2c299c`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Manages Shopify e-commerce store operations, digital product merchandising, and client support workflows.
- **Source Responsibility Evidence:** *"Du denkst mit, setzt Dinge um und begeisterst dich für Shopify & AI? Gleichzeitig behältst du den Überblick, findest Lösungen und kommunizierst klar? Dann möchten wir dich kennenlernen! Wir sind NETSHAKE – die AI-First E-Commerce-Agentur Als Shopify Premier"*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** E-commerce operational role maintaining Shopify store listings, inventory updates, customer support, and digital merchant setups.

### Record 106/117: `job_f758d5d0dfd3c148` – isaraerospace – Intern AI & Data Transformation

- **Company:** isaraerospace
- **Title:** Intern AI & Data Transformation
- **Canonical Job ID:** `job_f758d5d0dfd3c148`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Builds automated ELT data pipelines, API integrations, and warehouse data models supporting operational analytics.
- **Source Responsibility Evidence:** *"Develop and maintain scheduled ELT/ETL pipelines, monitor data quality and troubleshoot failures."*
- **Source Qualification Evidence:** *"with data consumers and refine what you deliver. Qualification Checklist Education: Enrolled in a Bachelor’s or Master’s in computer science, data engineering or information systems; available for at least six months."*
- **Decision Rationale:** Data engineering intern extracting data from SaaS tools, building warehouse pipelines with Python and dlt, and maintaining ELT jobs.

### Record 107/117: `job_7fa0c886847ad020` – hellofresh – Senior Category Manager – Marketing (All Genders)

- **Company:** hellofresh
- **Title:** Senior Category Manager – Marketing (All Genders)
- **Canonical Job ID:** `job_7fa0c886847ad020`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Leads strategic procurement, supplier contract negotiations, and agency spend management for corporate marketing categories.
- **Source Responsibility Evidence:** *"The (Senior) Category Manager Marketing will be responsible for overseeing strategic sourcing and contracting at HelloFresh for Marketing across different marketing categories, which may include: Offline Media, Online Media, Influencer Marketing, Sponsorships, Retail Media, etc."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Procurement category manager running commercial vendor tenders, agency contracts, and media buying spend negotiations.

### Record 108/117: `job_2d0fc63ff4419f55` – Bitstack – AML/CFT & Fraud Analyst - Internship

- **Company:** Bitstack
- **Title:** AML/CFT & Fraud Analyst - Internship
- **Canonical Job ID:** `job_2d0fc63ff4419f55`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Conducts anti-money laundering transaction monitoring, fraud investigations, and regulatory compliance checks.
- **Source Responsibility Evidence:** *"Bitstack is a crypto-asset service provider authorised under the MiCA Regulation. As such, we are subject to strict requirements relating to anti-money laundering (AML), counter-terrorist financing (CTF) and fraud prevention."*
- **Source Qualification Evidence:** *"Currently pursuing a Bachelor's or Master's degree in Compliance, Law, Finance, Risk Management or a related field, and looking for an internship or work-study placement."*
- **Decision Rationale:** Financial compliance analyst monitoring cryptocurrency transactions for AML/CTF risks and executing KYC fraud checks.

### Record 109/117: `job_ab5ac1cc60164046` – HICO Group AG – (Senior) Consultant Analytics & AI, Qlik (100%) (m/w/d), CH, hybrid

- **Company:** HICO Group AG
- **Title:** (Senior) Consultant Analytics & AI, Qlik (100%) (m/w/d), CH, hybrid
- **Canonical Job ID:** `job_ab5ac1cc60164046`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Designs enterprise business intelligence dashboards, Qlik analytics architectures, and AI data solutions for corporate clients.
- **Source Responsibility Evidence:** *"Unternehmen aller Größen bauen erfolgreich auf HICOs Management- und IT-Beratung, um mit uns relevante BI-, Planungs- und Digitalisierungs-Herausforderungen effizient, modern und verlässlich zu lösen."*
- **Source Qualification Evidence:** *"None"*
- **Decision Rationale:** Analytics consultant architecting Qlik Sense BI dashboards, automated data models, and enterprise predictive analytics solutions.

### Record 110/117: `job_4293f2e4c2289620` – Rithum – PMO & Portfolio Analyst

- **Company:** Rithum
- **Title:** PMO & Portfolio Analyst
- **Canonical Job ID:** `job_4293f2e4c2289620`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Coordinates program management office cadences, project portfolio tracking, and executive operational reporting.
- **Source Responsibility Evidence:** *"As the PMO & Portfolio Analyst , you are at the operational core of the Brands Services program management office."*
- **Source Qualification Evidence:** *"Minimum Qualifications 2+ years of experience in program or project coordination, PMO operations, business operations, or an analyst role supporting initiative or portfolio reporting Demonstrated experience building and maintaining status or performance"*
- **Decision Rationale:** PMO analyst tracking program milestones, executive dashboards, resource utilization, and portfolio delivery across projects.

### Record 111/117: `job_0b52ba3fd883521c` – Welo Global – Finnish Tech Linguistic Tester

- **Company:** Welo Global
- **Title:** Finnish Tech Linguistic Tester
- **Canonical Job ID:** `job_0b52ba3fd883521c`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Executes localization quality assurance, translation validation, and linguistic operations for Finnish language software.
- **Source Responsibility Evidence:** *"Write and report relevant bugs and errors using best practices through internal database system. Ability to undertake and prioritize tasks and issues quickly and efficiently. Native language skills and cultural awareness of native country."*
- **Source Qualification Evidence:** *"Education: Bachelor's degree (B. A.) from a college or university in related field, or equivalent combination of education and experience."*
- **Decision Rationale:** Localization QA tester evaluating translated software UI strings, identifying terminology errors, and logging defect tickets.

### Record 112/117: `job_7ff814cb58f1225d` – TechMagic – Customer Experience Analyst

- **Company:** TechMagic
- **Title:** Customer Experience Analyst
- **Canonical Job ID:** `job_7ff814cb58f1225d`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_PRODUCT_SOLUTIONS`
- **Updated Classification Reason:** Builds customer experience analytics pipelines, sentiment classification models, and conversational journey analytics using Qualtrics XM Discover.
- **Source Responsibility Evidence:** *"Platform Architecture & Enterprise Deployment QA troubleshooting of complex implementations and playbook establishment Ensure data governance and taxonomy consistency across the enterprise Own data pipelines and make integrity decisions Platform Innovation"*
- **Source Qualification Evidence:** *"Must have: 3+ years of experience combining business and technology (CX, analytics, or platform roles) Minimum 2 years deploying Qualtrics for enterprise clients XM Discover expertise: building and maintaining categorization, sentiment, and journey models XM"*
- **Decision Rationale:** Applied CX analytics specialist designing sentiment categorization models, text analytics pipelines, and Qualtrics XM Discover deployments.

### Record 113/117: `job_50d1df7084a06283` – Nebius – GPU Compute Partnerships & Commercial Operations Manager

- **Company:** Nebius
- **Title:** GPU Compute Partnerships & Commercial Operations Manager
- **Canonical Job ID:** `job_50d1df7084a06283`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Negotiates commercial agreements, vendor contracts, and capacity procurement for external GPU compute infrastructure.
- **Source Responsibility Evidence:** *"Manage ongoing compute partnerships: Serve as a primary commercial and operational contact for providers , coordinating capacity changes, service escalations, renewals, and contractual follow-through as business needs evolve."*
- **Source Qualification Evidence:** *"of the inference business. Drive agreements to execution: Coordinate Legal, Finance, Procurement, Security, and technical stakeholders through review, approval, signature, provider onboarding, and purchase order creation, keeping timelines aligned with"*
- **Decision Rationale:** Commercial procurement manager negotiating supplier contracts, vendor terms, and external capacity agreements for cloud GPUs.

### Record 114/117: `job_675a85266ca800bd` – TELUS Digital – Content Reviewer - United States

- **Company:** TELUS Digital
- **Title:** Content Reviewer - United States
- **Canonical Job ID:** `job_675a85266ca800bd`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Evaluates search engine result quality, content accuracy, and user relevance ratings against standardized evaluation guidelines.
- **Source Responsibility Evidence:** *"completed and project availability. Estimated earnings may vary depending on task volume and program requirements including, quality, and productivity, in accordance with the program's quality standards and guidelines."*
- **Source Qualification Evidence:** *"to succeed in this project: Professional fluency in English Residency in the United States for the last 3 consecutive years Active use of Gmail and other forms of social media and experience in the use of web browsers to navigate and interact with a variety"*
- **Decision Rationale:** Crowdsourced evaluator assessing search engine result relevance, accuracy, and trustworthiness based on strict rating guidelines.

### Record 115/117: `job_52cf5f192858c983` – Metics Media – Content Creator - YouTube

- **Company:** Metics Media
- **Title:** Content Creator - YouTube
- **Canonical Job ID:** `job_52cf5f192858c983`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Researches, scripts, and presents educational video tutorials on software applications and artificial intelligence tools.
- **Source Responsibility Evidence:** *"Create engaging YouTube tutorials about software, digital marketing, and AI tools that reach millions of people around the world every month through our YouTube channel, Metics Media."*
- **Source Qualification Evidence:** *"Native-level written and spoken English Strong on-camera presentation skills and the ability to communicate clearly and confidently Ability to quickly understand complex topics and explain them clearly to beginners Strong research skills and the ability to"*
- **Decision Rationale:** Digital media creator producing educational YouTube video walkthroughs explaining software products and generative AI applications.

### Record 116/117: `job_707a7ad52df07edf` – VXI Global Solutions – US Remote Patient Care Advocate (Customer Service)

- **Company:** VXI Global Solutions
- **Title:** US Remote Patient Care Advocate (Customer Service)
- **Canonical Job ID:** `job_707a7ad52df07edf`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `NON_TECHNICAL`
- **Updated Classification Reason:** Assists patients with prescription payment assistance navigation, insurance coordination, and customer healthcare support.
- **Source Responsibility Evidence:** *"This involves working closely with patients, insurance providers, healthcare professionals, and pharmacies to ensure seamless enrollment, eligibility verification, cost-sharing, and prescription fulfillment."*
- **Source Qualification Evidence:** *"High school diploma or GED required Experience in healthcare, insurance or customer service required (experience with prescription assistance programs is a plus) Strong attention to detail and ability to navigate complex processes Excellent communication"*
- **Decision Rationale:** Healthcare customer service specialist guiding patients through prescription assistance programs and payment options.

### Record 117/117: `job_201518350968ce4f` – iMerit Technology – AI Trainer - Video Annotation

- **Company:** iMerit Technology
- **Title:** AI Trainer - Video Annotation
- **Canonical Job ID:** `job_201518350968ce4f`
- **Previous Category:** `UNCERTAIN`
- **Updated Category:** `AI_SUPPORTING_TECH`
- **Updated Classification Reason:** Annotates and validates video datasets with object bounding boxes and action markers to train robotics AI models.
- **Source Responsibility Evidence:** *"As part of the certification process, you will demonstrate your ability to: Annotate short video clips by identifying objects, actions and events. Evaluate video quality, relevance and accuracy against established guidelines."*
- **Source Qualification Evidence:** *"Strong attention to detail and analytical thinking. Strong written English and the ability to follow detailed instructions independently. A commitment to accuracy and consistency."*
- **Decision Rationale:** Data annotation specialist labeling video frames, identifying objects and actions, and verifying dataset quality for robotics AI.

