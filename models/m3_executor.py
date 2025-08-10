"""Wrapper for Model‑3 (Executor: Codegen)."""
from __future__ import annotations

import os, re, json, asyncio
from typing import Dict, Any
from pathlib import Path
import openai

MODEL_M3 = os.getenv("MODEL_M3", "gpt-4o-mini")
openai.api_key = os.getenv("OPENAI_API_KEY", "")

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "m3.txt"

CODE_FENCE = re.compile(r"```(?:python)?\n([\s\S]*?)```", re.IGNORECASE)

def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are Model-3 (Executor). Return one Python script inside a single fenced code block."
        )

async def run_m3(m2_out: Dict[str, Any], timeout_sec: int = 100) -> str:
    payload = {
        "OutputSchema": m2_out.get("OutputSchema", {}),
        "CodePlan": m2_out.get("CodePlan", {}),
        "coding_prompt": m2_out.get("coding_prompt", ""),
    }

    def _call():
        resp = openai.ChatCompletion.create(
            model=MODEL_M3,
            messages=[
                {"role": "system", "content": _load_system_prompt()},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=0.1,
        )
        return resp.choices[0].message["content"]

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _call)

    m = CODE_FENCE.search(text)
    code = m.group(1) if m else text
    return code
