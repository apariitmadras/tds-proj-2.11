from __future__ import annotations

import os, json, asyncio
from typing import Dict, Any
from pathlib import Path
import openai

MODEL_M1 = os.getenv("MODEL_M1", "gpt-4o-mini")
openai.api_key = os.getenv("OPENAI_API_KEY", "")

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "m1.txt"

def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are Model-1 (Prompt Engineer). Return JSON with keys 'rewritten_prompt' "
            "and 'task_fingerprint'."
        )

async def run_m1(user_text: str, timeout_sec: int = 10) -> Dict[str, Any]:
    def _call():
        resp = openai.ChatCompletion.create(
            model=MODEL_M1,
            messages=[
                {"role": "system", "content": _load_system_prompt()},
                {"role": "user", "content": user_text},
            ],
            temperature=0.1,
        )
        return resp.choices[0].message["content"]

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _call)

    # Parse assistant JSON reply
    try:
        return json.loads(text)
    except Exception:
        return {"rewritten_prompt": user_text, "task_fingerprint": {"task_type": "PlainStats", "sources": [], "time_budget_sec": timeout_sec}}
