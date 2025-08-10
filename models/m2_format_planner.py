"""Wrapper for Model‑2 (Format & Plan Designer)."""
from __future__ import annotations

import os, json, asyncio
from typing import Dict, Any
from pathlib import Path
import openai

MODEL_M2 = os.getenv("MODEL_M2", "gpt-4o-mini")
openai.api_key = os.getenv("OPENAI_API_KEY", "")

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "m2.txt"

def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are Model-2 (Format & Plan Designer). Return JSON with keys 'OutputSchema',"
            " 'CodePlan', and 'coding_prompt'."
        )

async def run_m2(m1_out: Dict[str, Any], timeout_sec: int = 12) -> Dict[str, Any]:
    def _call():
        resp = openai.ChatCompletion.create(
            model=MODEL_M2,
            messages=[
                {"role": "system", "content": _load_system_prompt()},
                {"role": "user", "content": json.dumps(m1_out, ensure_ascii=False)},
            ],
            temperature=0.1,
        )
        return resp.choices[0].message["content"]

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _call)

    try:
        return json.loads(text)
    except Exception:
        # Minimal fallback
        return {
            "OutputSchema": {"container": {"type": "array", "order": ["result"]}, "fields": {"result": {"type": "string"}}},
            "CodePlan": {"allowed_libs": ["requests", "pandas"], "net_allowlist": [], "execution": "single script"},
            "coding_prompt": "Write a Python script that prints a JSON array with one string, summarizing the input.",
        }
