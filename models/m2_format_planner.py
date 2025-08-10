import os, json, re, asyncio
from typing import Dict, Any
from pathlib import Path
import openai

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "m2.txt"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")

openai.api_key = os.getenv("OPENAI_API_KEY", "")
MODEL_M2 = os.getenv("MODEL_M2", "gpt-4o-mini")

async def run_m2(m1: Dict[str, Any], timeout_sec: int = 12) -> Dict[str, Any]:
    def _call():
        resp = openai.ChatCompletion.create(
            model=MODEL_M2,
            messages=[
                {"role":"system","content": SYSTEM_PROMPT},
                {"role":"user","content": json.dumps(m1, ensure_ascii=False)}
            ],
            temperature=0.2,
        )
        return resp.choices[0].message["content"]

    loop = asyncio.get_event_loop()
    text = await loop.run_in_executor(None, _call)

    m = re.search(r"\{[\s\S]*\}", text)
    data = json.loads(m.group(0)) if m else {"OutputSchema":{},"CodePlan":{},"coding_prompt":""}
    return data
