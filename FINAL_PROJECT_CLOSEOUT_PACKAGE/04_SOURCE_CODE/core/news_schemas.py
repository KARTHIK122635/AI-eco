from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import re
import hashlib


KNOWN_AI_COMPANIES = [
    "OpenAI", "Google", "DeepMind", "Microsoft", "Anthropic", "Meta",
    "Nvidia", "Mistral", "Hugging Face", "Cohere", "Stability AI",
    "Apple", "Amazon", "AWS", "Baidu", "Alibaba", "Tencent", "ByteDance",
    "Tesla", "xAI", "Midjourney", "Scale AI", "Databricks", "Snowflake",
    "Intel", "AMD", "Qualcomm", "Salesforce", "IBM", "Oracle", "Perplexity",
    "Runway", "ElevenLabs", "Character.ai", "Suno", "Udio", "Writer",
    "Harvey", "Glean", "Physical Intelligence", "Covariant", "Figure AI"
]


def extract_related_companies(text: str) -> List[str]:
    """Identifies mentioned prominent AI entities/companies in text."""
    if not text:
        return []
    found = []
    text_lower = text.lower()
    for company in KNOWN_AI_COMPANIES:
        pattern = r'\b' + re.escape(company.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(company)
    return found


def classify_news_category(title: str, summary: str) -> str:
    """Classifies an article into an AI category based on title and summary."""
    combined = f"{title} {summary}".lower()
    if any(k in combined for k in ["llm", "large language model", "gpt", "gemini", "claude", "llama", "deepseek", "foundation model"]):
        return "LLMs & Foundation Models"
    elif any(k in combined for k in ["robot", "robotics", "autonomous", "humanoid", "self-driving", "embodied"]):
        return "Robotics & Embodied AI"
    elif any(k in combined for k in ["chip", "gpu", "tpu", "semiconductor", "hardware", "datacenter", "nvidia"]):
        return "AI Hardware & Infrastructure"
    elif any(k in combined for k in ["agent", "copilot", "assistant", "workflow", "automation"]):
        return "AI Agents & Applications"
    elif any(k in combined for k in ["image", "video", "generation", "diffusion", "sora", "multimodal", "audio", "voice", "speech"]):
        return "Generative Media & Multimodal"
    elif any(k in combined for k in ["regulation", "policy", "safety", "governance", "ethics", "copyright", "lawsuit", "treaty"]):
        return "Policy, Safety & Governance"
    elif any(k in combined for k in ["funding", "valuation", "seed", "series a", "series b", "acquisition", "ipo", "invest"]):
        return "AI Business & Investment"
    else:
        return "General AI & Industry"


def generate_news_id(url: str, title: str) -> str:
    """Generates a stable unique news ID based on canonical URL or title."""
    clean_target = (url or title).strip().lower()
    h = hashlib.sha256(clean_target.encode("utf-8")).hexdigest()[:16]
    return f"news_{h}"
