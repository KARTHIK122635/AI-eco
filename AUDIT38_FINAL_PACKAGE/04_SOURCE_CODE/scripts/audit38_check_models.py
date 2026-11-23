import os
import sys
import httpx

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.env_loader import load_project_env

load_project_env()

gemini_key = os.environ.get("GEMINI_API_KEY")

# Check which Gemini models are available
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
with httpx.Client(timeout=10.0) as client:
    r = client.get(url)
    print("Gemini Models Status:", r.status_code)
    if r.status_code == 200:
        models = [m["name"] for m in r.json().get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
        print("Available generation models:")
        for m in models[:10]:
            print(" ", m)
    else:
        print("Error:", r.text[:200])

# Check Groq with qwen/qwen3.8-27b or llama-3.3-70b-versatile
groq_key = os.environ.get("GROQ_API_KEY")
url_g = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {groq_key}"}
with httpx.Client(timeout=10.0) as client:
    r_g = client.get(url_g, headers=headers)
    print("\nGroq Models Status:", r_g.status_code)
    if r_g.status_code == 200:
        g_models = [m["id"] for m in r_g.json().get("data", [])]
        print("Available Groq models:")
        for m in g_models:
            print(" ", m)
    else:
        print("Error:", r_g.text[:200])
