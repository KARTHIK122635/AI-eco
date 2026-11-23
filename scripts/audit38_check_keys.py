import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from core.env_loader import load_project_env

load_project_env()

keys = ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"]
for k in keys:
    val = os.environ.get(k)
    configured = bool(val and val.strip() and not val.startswith("your_"))
    print(f"{k}: {'CONFIGURED' if configured else 'NOT_CONFIGURED'}")
