import os
import sys
import httpx

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.env_loader import load_project_env

load_project_env()

gemini_key = os.environ.get("GEMINI_API_KEY")
for m in ["gemini-3.8-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
    payload = {"contents": [{"parts": [{"text": "Say hello"}]}]}
    with httpx.Client(timeout=10.0) as client:
        r = client.post(url, json=payload)
        print(f"Gemini {m}: {r.status_code}")
        if r.status_code == 200:
            print("Response:", r.json()["candidates"][0]["content"]["parts"][0]["text"].strip())
        else:
            print("Error:", r.text[:150])

groq_key = os.environ.get("GROQ_API_KEY")
url_g = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": f"Bearer {groq_key}"}
payload_g = {"model": "qwen/qwen3.8-27b", "messages": [{"role": "user", "content": "Say hello"}]}

with httpx.Client(timeout=10.0) as client:
    r_g = client.post(url_g, headers=headers, json=payload_g)
    print("\nGroq qwen/qwen3.8-27b:", r_g.status_code)
    if r_g.status_code == 200:
        print("Response:", r_g.json()["choices"][0]["message"]["content"].strip()[:100])
    else:
        print("Error:", r_g.text[:200])
