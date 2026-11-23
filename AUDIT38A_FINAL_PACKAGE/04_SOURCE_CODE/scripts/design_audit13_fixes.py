import json
import csv
import re
from collections import Counter

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = {j['jobId']: j for j in [json.loads(line)['content']['data'] for line in f]}

# 1. Reason updates for the 6 target positions and others
REASON_UPDATES = {
    'job_d207b42e585bf8e6': "Designs and executes digital campaign strategies, paid media initiatives, and public advocacy communications to advance policy goals.",
    'job_03adf198b79570b7': "Executes molecular biology and biochemistry experiments at the bench and maintains laboratory research protocols.",
    'job_80a480dfe5f61806': "Translates technical AI research into policy-ready guidance and provides strategic advisory for government policymakers and legislators.",
    'job_3ab4fad59bd0a42d': "Generates experimental and computational quantum chemistry datasets used to train and evaluate foundational AI models.",
    'job_b30c4117b32b2e1b': "Evaluates AI-designed therapeutic antibodies through experimental readouts to train and advance generative biological models.",
    'job_d2ffb1910190a82b': "Structures and executes data licensing agreements, commercial partner transactions, and data acquisition deals.",
    
    # EM distinct reasons
    'job_ed400c89f47ddb17': "Leads software engineering teams developing foundational APIs, developer surfaces, and runtime infrastructure for Claude.",
    'job_090ae3e6187d0e95': "Leads software engineering teams building enterprise data connectors, secure integrations, and client platform interfaces.",
    'job_38be0729c2816ee2': "Leads engineering teams developing enterprise security controls, administrative governance consoles, and tenant isolation platforms.",
    'job_663af56a0aa1a7df': "Leads software engineering teams optimizing cluster scheduler efficiency, fleet resource utilization, and compute infrastructure.",
    'job_a5d0ab0901bbfb1f': "Leads applied AI engineering teams delivering custom production deployments, system integrations, and technical architectures for strategic accounts.",
    'job_ee230cb07fc26940': "Leads software engineering teams building customer-facing generative AI evaluation platforms and developer integration tools.",
    'job_d5c572c9f964159c': "Leads regional software engineering teams delivering customized AI data annotation platforms and enterprise software integrations.",
    'job_0059623e088488b4': "Leads engineering teams developing model registries, experiment tracking repositories, and ML workflow orchestration platforms.",
    'job_8bcae9c56667104b': "Leads software engineering teams building core backend microservices, distributed data systems, and experimentation platforms.",
    'job_8148b13d29ae61e1': "Leads engineering teams developing distributed telemetry pipelines, cluster metrics monitoring, and observability platforms.",
    'job_223b56dc665b1aa5': "Leads software engineering teams developing conversational data analytics, generative BI platforms, and dashboarding systems.",
    'job_1e4d95e9aa181d43': "Leads software engineering teams developing conversational data analytics, generative BI platforms, and dashboarding systems.",
    'job_f603b5a46b44234f': "Leads traditional software engineering teams and technical architecture for online rental marketplace platforms.",
    'job_66b8d2841d8bf608': "Directs enterprise software engineering, business planning data architectures, and corporate analytics systems.",
    'job_dec08a00c3ca6fe1': "Leads software engineering teams developing digital advertising workflow automation and ad performance recommendation engines.",
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
    'job_7cd2b2ec29a67a80': "Provides STEM domain advisory expertise, expert consensus workflows, and operational quality reviews for AI evaluation.",

    # Research operations
    'job_26a658a430efb4db': "Manages technical publication operations, system cards, and scientific research artifact releases.",
    'job_4fa3cfbf3448f219': "Directs grant program administration, application review operations, and research milestone tracking for open AI benchmarks.",
    'job_8dc675e87a22ebfe': "Directs grant program administration, application review operations, and research milestone tracking for open AI benchmarks."
}

# 2. Category updates for clearly miscategorized jobs
CATEGORY_UPDATES = {
    'job_1b9058f92fab34da': 'CORE_AI_ML', # Aleph Alpha Model Training
    'job_366b4bea010eed1f': 'CORE_AI_ML', # Aleph Alpha Model Training
    'job_692c453001241683': 'AI_SUPPORTING_TECH', # Remanence Platform Engineering
    'job_4a7d1b688879c80b': 'AI_SUPPORTING_TECH', # LINKIT AI Platform Engineer
}

print(f"Total reason updates planned: {len(REASON_UPDATES)}")
print(f"Total category updates planned: {len(CATEGORY_UPDATES)}")
