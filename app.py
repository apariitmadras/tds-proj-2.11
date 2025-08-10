import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from orchestrator import run_chain

app = FastAPI(title="Multi-Model Pipeline API")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/")
async def analyze(request: Request, file: Optional[UploadFile] = File(None)):
    try:
        if file is not None:
            user_text = (await file.read()).decode("utf-8", errors="ignore").strip()
        else:
            # raw text body or form field
            body_bytes = await request.body()
            user_text = body_bytes.decode("utf-8", errors="ignore").strip()

        if not user_text:
            raise HTTPException(status_code=400, detail="Question is required and must be a string")

        final_output = await run_chain(user_text)
        # Return exactly what Model-3 printed (could be JSON, array, object, etc.)
        return PlainTextResponse(final_output)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
