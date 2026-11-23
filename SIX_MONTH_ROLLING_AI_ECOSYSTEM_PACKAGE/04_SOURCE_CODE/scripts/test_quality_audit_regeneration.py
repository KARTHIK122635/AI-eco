import json
import csv
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

# Complete dictionary of reason updates
REASON_UPDATES = {
    # 6 Section 2 targets
    'job_d207b42e585bf8e6': "Designs and executes digital campaign strategies, paid media initiatives, and public advocacy communications to advance policy goals.",
    'job_03adf198b79570b7': "Executes molecular biology and biochemistry experiments at the bench and maintains laboratory research protocols.",
    'job_80a480dfe5f61806': "Translates technical AI research into policy-ready guidance and provides strategic advisory for government policymakers and legislators.",
    'job_3ab4fad59bd0a42d': "Generates experimental and computational quantum chemistry datasets used to train and evaluate foundational AI models.",
    'job_b30c4117b32b2e1b': "Evaluates AI-designed therapeutic antibodies through experimental readouts to train and advance generative biological models.",
    'job_d2ffb1910190a82b': "Structures and executes data licensing agreements, commercial partner transactions, and data acquisition deals.",
    
    # 16 Engineering Managers resolving cross-category collision
    'job_ed400c89f47ddb17': "Leads software engineering teams developing foundational APIs, developer surfaces, and runtime infrastructure for Claude.",
    'job_090ae3e6187d0e95': "Leads software engineering teams building enterprise data connectors, secure integrations, and client platform interfaces.",
    'job_38be0729c2816ee2': "Leads engineering teams developing enterprise security controls, administrative governance consoles, and tenant isolation platforms.",
    'job_663af56a0aa1a7df': "Leads software engineering teams optimizing cluster scheduler efficiency, fleet resource utilization, and compute infrastructure.",
    'job_a5d0ab0901bbfb1f': "Leads applied AI engineering teams delivering custom production deployments, system integrations, and technical architectures for strategic accounts.",
    'job_ee230cb07fc26940': "Leads software engineering teams building customer-facing generative AI evaluation platforms and developer integration tools.",
    'job_d5c572c9f964159c': "Leads regional software engineering teams delivering customized AI data annotation platforms and enterprise software integrations.",
    'job_03985202c85fd055': "Directs regional engineering teams delivering customized AI data annotation platforms and enterprise software integrations.",
    'job_899abc934e16f6c3': "Leads software engineering teams developing programmatic data labeling pipelines, data delivery workflows, and ML platforms.",
    'job_8ef2c681dd8aea2b': "Leads software engineering teams developing cloud fleet provisioning controllers, hardware lifecycle automation, and cluster management platforms.",
    'job_cdd1b845e00af65b': "Leads software engineering teams developing conversational data analytics, generative BI platforms, and dashboarding systems.",
    'job_824d95e9aa181d43': "Directs software engineering teams developing conversational data analytics, generative BI platforms, and dashboarding systems.",
    'job_f603b5a46b44234f': "Directs traditional web development teams and technical architecture for online rental marketplace platforms.",
    'job_66b8d2841d8bf608': "Directs enterprise data architecture, corporate business planning applications, and legacy analytics engineering teams.",
    'job_dec08a00c3ca6fe1': "Leads software engineering teams developing digital advertising campaign workflows and predictive recommendation software.",
    'job_fec4fa258443cdac': "Directs software engineering teams, product delivery roadmaps, and technical architecture for industrial engineering software.",

    # CoreWeave Kubernetes engineers in AI_SUPPORTING_TECH
    'job_c3db74f350a55b42': "Develops Kubernetes platform extensions, custom resource controllers, and cluster management software.",
    'job_208b4929a459148e': "Develops Kubernetes platform extensions, custom resource controllers, and cluster management software.",
    'job_b2783ceb7df9a4a5': "Develops Kubernetes platform extensions, custom resource controllers, and cluster management software.",
    'job_ae720e9aa5afc795': "Develops Kubernetes platform extensions, custom resource controllers, and cluster management software.",

    # Anthropic Field Executive Architect
    'job_db8b6c46c7d0f6c0': "Advises strategic enterprise executive leaders on AI architecture adoption, cloud platform deployment, and technical software governance.",

    # German NON_AI_TECH roles
    'job_4dec34f8f167d351': "Engineers enterprise Linux operating systems, bare-metal Kubernetes server clusters, and traditional hardware compute platforms.",
    'job_ff7804510a9b3b72': "Builds and maintains enterprise cloud computing environments, Kubernetes platforms, and automated IT infrastructure pipelines.",
    'job_a76aae0327db4822': "Deploys conversational voice interfaces, commercial chatbot solutions, and enterprise telecommunications systems integrations.",
    'job_ba5d0da6c2aa3192': "Develops automated business process workflows, document extraction systems, and enterprise software integrations for real estate operations.",

    # Scale AI Fellows in NON_TECHNICAL
    'job_0d920108a62c8874': "Provides financial domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_124af3b5db71e7d9': "Provides creative domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_8ad086e5f89d9290': "Provides medical domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_9a8d370f471b9403': "Provides medical domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_4f01a4f5c61d76ca': "Provides research domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_05de6b17a46dcb71': "Provides research domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_105421a2eaf7d737': "Provides STEM domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",
    'job_21e78cd8d02add0c': "Provides STEM domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",

    # Research operations
    'job_26a658a430efb4db': "Manages technical publication operations, system cards, and scientific research artifact releases.",
    'job_7f1911a1ef41fe62': "Directs grant program administration, application review operations, and research milestone tracking for open AI benchmarks.",
    'job_25025ae20395340f': "Directs grant program administration, application review operations, and research milestone tracking for open AI benchmarks.",

    # Aleph Alpha Model Training
    'job_1b9058f92fab34da': "Conducts applied research, foundation model pre-training experimentation, and deep learning training pipeline development.",
    'job_366b4bea010eed1f': "Conducts applied research, foundation model pre-training experimentation, and deep learning training pipeline development.",

    # Remanence Platform Engineering
    'job_692c453001241683': "Builds scalable distributed cloud platforms, container orchestration systems, and infrastructure supporting AI agent execution."
}

# Category updates
CATEGORY_UPDATES = {
    'job_1b9058f92fab34da': 'CORE_AI_ML',
    'job_366b4bea010eed1f': 'CORE_AI_ML',
    'job_692c453001241683': 'AI_SUPPORTING_TECH',
    'job_4a7d1b688879c80b': 'AI_SUPPORTING_TECH',
}

# Retained genuine review records with documented notes
RETAINED_REVIEWS = {
    'job_0fccf7a2e05aac14': "GENUINE_AMBIGUITY_EDUCATIONAL_COURSE: Listing represents state-subsidized AZAV vocational education (Bildungsgutschein) rather than standard commercial employment.",
    'job_87e7a826e1904b7b': "GENUINE_AMBIGUITY_CROSS_DISCIPLINARY: Leadership role spans technical cybersecurity operations and non-technical people management.",
    'job_61a941b22ab64bde': "GENUINE_AMBIGUITY_THREAT_INTELLIGENCE: Specialized national security intelligence and weapons risk analysis on the borderline between non-technical compliance and technical AI safety.",
    'job_20072b58f5dc3523': "GENUINE_AMBIGUITY_THREAT_INTELLIGENCE: Specialized national security intelligence and weapons risk analysis on the borderline between non-technical compliance and technical AI safety.",
    'job_91fd8017f05b1d94': "GENUINE_AMBIGUITY_FELLOWSHIP_ROLE: Software engineering fellowship role evaluating AI models on the borderline between non-technical expert annotation and technical development.",
    'job_f3d068e4db415d90': "GENUINE_AMBIGUITY_FELLOWSHIP_ROLE: Software engineering fellowship role evaluating AI models on the borderline between non-technical expert annotation and technical development.",
    'job_953d904c00132369': "GENUINE_AMBIGUITY_AGENCY_ROLE: Digital agency role bridging traditional e-commerce web consulting and rapid prototyping of AI solutions."
}

# Verify all JIDs exist in canonical
for jid in REASON_UPDATES:
    assert jid in jobs, f"Missing {jid} in jobs!"
for jid in CATEGORY_UPDATES:
    assert jid in jobs, f"Missing {jid} in jobs!"
for jid in RETAINED_REVIEWS:
    assert jid in jobs, f"Missing {jid} in jobs!"

print("Verified: All JIDs exist in canonical!")
print(f"Total reason updates: {len(REASON_UPDATES)}")
print(f"Total category updates: {len(CATEGORY_UPDATES)}")
print(f"Total retained reviews: {len(RETAINED_REVIEWS)}")
