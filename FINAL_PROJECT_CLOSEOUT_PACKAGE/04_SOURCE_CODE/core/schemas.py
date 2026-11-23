from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
import re


AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "large language model", "llm", "generative ai", "genai", "computer vision",
    "natural language processing", "nlp", "speech recognition", "text-to-speech",
    "speech-to-speech", "voice ai", "ai agent", "autonomous agent", "transformer",
    "diffusion model", "reinforcement learning", "foundation model", "prompt engineering",
    "ai copilot", "ai assistant", "vector database", "fine-tuning", "lora", "embedding"
]


def evaluate_ai_evidence(name: str, description: str, tags: List[str]) -> Dict[str, Any]:
    """
    Evaluates whether an entity has concrete supporting evidence of being AI-related.
    Returns boolean is_ai, confidence score, matched keywords, and primary focus area.
    """
    combined_text = f"{name} {description} {' '.join(tags)}".lower()
    matches = []
    
    # Explicit word-boundary checks
    if re.search(r'\bai\b', combined_text):
        matches.append("ai")
    for kw in AI_KEYWORDS:
        if kw in combined_text and kw not in matches:
            matches.append(kw)

    is_ai = len(matches) > 0
    confidence = "HIGH" if len(matches) >= 2 or any(k in ["generative ai", "foundation model", "llm", "large language model"] for k in matches) else ("MEDIUM" if is_ai else "NONE")
    
    # Classify focus area
    focus_area = "General AI"
    if any(k in ["llm", "large language model", "foundation model", "transformer", "text-to-speech", "nlp"] for k in matches):
        focus_area = "NLP & Foundation Models"
    elif any(k in ["computer vision", "diffusion model", "outpainting", "image"] for k in matches):
        focus_area = "Computer Vision & Generative Media"
    elif any(k in ["ai agent", "autonomous agent", "copilot", "assistant"] for k in matches):
        focus_area = "Autonomous Agents & Copilots"
    elif any(k in ["speech", "voice ai", "audio"] for k in matches):
        focus_area = "Speech & Audio AI"
    elif any(k in ["machine learning", "deep learning", "neural network"] for k in matches):
        focus_area = "Machine Learning & Core AI"
    elif is_ai:
        focus_area = "Applied AI & Automation"
    else:
        focus_area = "Non-AI"

    return {
        "is_ai": is_ai,
        "confidence": confidence,
        "matched_keywords": matches,
        "focus_area": focus_area
    }


@dataclass
class AIStartup:
    """Canonical schema for a verified AI startup / company."""
    startup_id: str
    name: str
    description: Optional[str]
    ai_focus_area: str
    ai_evidence: List[str]
    employee_count: Optional[Union[int, str]] = None
    pricing_model: Optional[str] = None
    website: Optional[str] = None
    primary_source_url: str = ""
    provenance_sources: List[str] = field(default_factory=list)
    headquarters: Optional[str] = None
    batch_or_founded: Optional[str] = None
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AIProduct:
    """Canonical schema for a verified AI product / model / space."""
    product_id: str
    name: str
    description: Optional[str]
    product_type: str  # "AI Model / Weights", "AI Application / Space", "AI Agent / SaaS", etc.
    ai_task_category: str  # "text-generation", "image-to-video", "speech-to-speech", etc.
    developer_or_company: str
    developer_startup_id: Optional[str] = None
    pricing_model: Optional[str] = None  # "Open Source", "Freemium", "Usage-Based API", etc.
    original_source_url: str = ""
    provenance_source: str = ""
    license: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
