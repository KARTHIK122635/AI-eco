import asyncio
import httpx

candidates = [
    "cohere", "elevenlabs", "runwayml", "runway", "perplexity", "perplexityai",
    "mistralai", "mistral", "glean", "shieldai", "stabilityai", "synthesia",
    "cerebras", "sambanovasystems", "groq", "deepl", "pinecone", "weaviate",
    "wandb", "anyscale", "modal", "togetherai", "lambdalabs", "coreweave",
    "jasper", "characterai", "figure", "appliedintuition", "cognition",
    "poolside", "deepgram", "replicate", "baseten", "snorkel", "labelbox",
    "hebbia", "tome", "harvey", "cresta", "writer", "abacusai", "c3ai",
    "dataminr", "scaleai", "anthropic", "databricks", "huggingface", "openai",
    "palantir", "instabase", "cleanlab", "modular", "qdrant", "chroma",
    "zilliz", "langchain", "llamaindex", "unstructured", "braintrust"
]

async def check_gh(client, token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    try:
        r = await client.get(url, timeout=3.0)
        if r.status_code == 200:
            jobs = r.json().get("jobs", [])
            if len(jobs) > 0:
                print(f"[GH 200] {token}: {len(jobs)} jobs", flush=True)
                return ("gh", token, len(jobs))
    except:
        pass
    return None

async def check_lever(client, token):
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    try:
        r = await client.get(url, timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"[Lever 200] {token}: {len(data)} jobs", flush=True)
                return ("lever", token, len(data))
    except:
        pass
    return None

async def main():
    async with httpx.AsyncClient(headers={"User-Agent": "AIEcosystemCollector/1.0"}) as client:
        tasks = []
        for c in candidates:
            tasks.append(check_gh(client, c))
            tasks.append(check_lever(client, c))
        results = await asyncio.gather(*tasks)
        valid = [r for r in results if r is not None]
        print(f"\nTotal valid boards found: {len(valid)}", flush=True)
        gh_tot = sum(r[2] for r in valid if r[0] == 'gh')
        lever_tot = sum(r[2] for r in valid if r[0] == 'lever')
        print(f"Total GH jobs: {gh_tot}, Total Lever jobs: {lever_tot}, Total: {gh_tot + lever_tot}", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
