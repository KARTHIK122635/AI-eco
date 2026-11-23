import asyncio
import httpx

variations = [
    ("gh", "cohereai"), ("gh", "cerebrassystems"), ("gh", "groqinc"), ("gh", "groq"),
    ("gh", "pinecone-io"), ("gh", "weaviate-io"), ("gh", "weightsbiases"), ("gh", "wandb-inc"),
    ("gh", "lambda"), ("gh", "lambdalabs"), ("gh", "appliedintuition"), ("gh", "cognitionlabs"),
    ("gh", "synthesia"), ("gh", "gleantech"), ("gh", "runwayml"), ("gh", "runwayteam"),
    ("gh", "eleven-labs"), ("gh", "elevenlabsio"), ("gh", "deepgram"), ("gh", "baseten"),
    ("gh", "replicate"), ("gh", "snorkelai"), ("gh", "hebbia"), ("gh", "harvey"),
    ("lever", "cohere"), ("lever", "cohereai"), ("lever", "runway"), ("lever", "elevenlabs"),
    ("lever", "glean"), ("lever", "perplexity"), ("lever", "perplexityai"), ("lever", "groq"),
    ("lever", "pinecone"), ("lever", "weaviate"), ("lever", "anyscale"), ("lever", "modal"),
    ("lever", "replicate"), ("lever", "deepgram"), ("lever", "harvey"), ("lever", "hebbia"),
    ("lever", "snorkel"), ("lever", "appliedintuition"), ("lever", "cognition"), ("lever", "poolside"),
    ("lever", "mistral"), ("lever", "mistralai"), ("lever", "shieldai"), ("lever", "synthesia"),
    ("lever", "cerebras"), ("lever", "wandb"), ("lever", "weightsandbiases"), ("lever", "deepl")
]

async def check(client, kind, token):
    if kind == "gh":
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    else:
        url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    try:
        r = await client.get(url, timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            jobs = data.get("jobs", []) if kind == "gh" else data
            if isinstance(jobs, list) and len(jobs) > 0:
                print(f"[{kind.upper()} 200] {token}: {len(jobs)} jobs", flush=True)
                return (kind, token, len(jobs))
    except:
        pass
    return None

async def main():
    async with httpx.AsyncClient(headers={"User-Agent": "AIEcosystemCollector/1.0"}) as client:
        tasks = [check(client, k, t) for k, t in variations]
        results = await asyncio.gather(*tasks)
        valid = [r for r in results if r is not None]
        print(f"\nFound {len(valid)} additional boards, total jobs: {sum(r[2] for r in valid)}", flush=True)

if __name__ == '__main__':
    asyncio.run(main())
