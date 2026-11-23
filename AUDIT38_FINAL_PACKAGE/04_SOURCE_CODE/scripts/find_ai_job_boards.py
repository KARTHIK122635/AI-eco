import json
import re
import httpx

client = httpx.Client(timeout=4.0, headers={"User-Agent": "AIEcosystemCollector/1.0"})

# Load some startup names from canonical_startups.jsonl
slugs = set()
with open("data/canonical/canonical_startups.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        name = data.get("content", {}).get("entityName", "")
        # convert to slug
        slug = re.sub(r'[^a-z0-9]', '', name.lower())
        if 3 <= len(slug) <= 20:
            slugs.add(slug)

print(f"Total candidate slugs from startups: {len(slugs)}")

# Add known major AI companies
known_ai = [
    "cohere", "mistral", "mistralai", "runway", "runwayml", "elevenlabs", "glean",
    "perplexity", "perplexityai", "shieldai", "stability", "stabilityai", "synthesia",
    "cerebras", "sambanovasystems", "groq", "deepl", "pinecone", "weaviate", "wandb",
    "anyscale", "modal", "togetherai", "lambdalabs", "coreweave", "jasper", "characterai",
    "figure", "appliedintuition", "cognition", "poolside", "deepgram", "replicate",
    "baseten", "snorkelaI", "snorkel", "labelbox", "hebbia", "tome", "harvey", "cresta",
    "samba", "adept", "inflection", "writer", "abacusai", "c3ai", "dataminr", "shield",
    "scale", "scaleai", "anthropic", "databricks", "huggingface", "openai", "palantir",
    "instabase", "cleanlab", "coactive", "deci", "octoml", "predibase", "cartesia",
    "vllm", "modular", "dust", "qdrant", "chroma", "milvus", "zilliz", "haystack",
    "langchain", "llamaindex", "unstructured", "fixie", "mem0", "braintrust"
]
for k in known_ai:
    slugs.add(k)

# Test a subset of popular AI companies
active_gh = {}
print(f"Testing {len(known_ai)} curated AI companies on Greenhouse...")
for k in known_ai:
    try:
        r = client.get(f"https://boards-api.greenhouse.io/v1/boards/{k}/jobs")
        if r.status_code == 200:
            count = len(r.json().get("jobs", []))
            if count > 0:
                active_gh[k] = count
                print(f"  GH: {k} -> {count} jobs")
    except:
        pass

print(f"\nTotal active GH boards found: {len(active_gh)}, total jobs: {sum(active_gh.values())}")

# Also test curated on Lever
active_lever = {}
print(f"\nTesting curated AI companies on Lever...")
for k in known_ai:
    try:
        r = client.get(f"https://api.lever.co/v0/postings/{k}?mode=json")
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                active_lever[k] = len(data)
                print(f"  Lever: {k} -> {len(data)} jobs")
    except:
        pass

print(f"\nTotal active Lever boards found: {len(active_lever)}, total jobs: {sum(active_lever.values())}")
