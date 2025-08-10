import os, json, re, asyncio
from typing import Dict, Any
from pathlib import Path

import openai

# Load prompt
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "m1.txt"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

openai.api_key = os.getenv("OPENAI_API_KEY", "")
MODEL_M1 = os.getenv("MODEL_M1", "gpt-4o-mini")

async def run_m1(user_text: str, timeout_sec: int = 10) -> Dict[str, Any]:
    def _call():
        resp = openai.ChatCompletion.create(
            model=MODEL_M1,
            messages=[
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": user_text}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message["content"]

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _call)

    # Extract first JSON object from response
    m = re.search(r"\{[\s\S]*\}", text)
    data = json.loads(m.group(0)) if m else {"rewritten_prompt": user_text, "task_fingerprint": {}}
    return data
