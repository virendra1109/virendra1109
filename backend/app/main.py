from __future__ import annotations

import json
import os
from typing import Any, Dict

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models import AnalyzeResponse, ErrorResponse, KPIModel, ComplianceModel, GoldenJourneyModel
from . import pipeline

app = FastAPI(title="Call Centre Analysis API", version="1.0.0")

# CORS
FRONTEND_ORIGINS = os.environ.get("FRONTEND_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze", response_model=AnalyzeResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def analyze(
    file: UploadFile = File(..., description="WAV audio file"),
    call_date: str | None = Form(default=None),
    agent_name: str | None = Form(default=None),
    customer_name: str | None = Form(default=None),
) -> Any:
    try:
        if file.content_type not in ("audio/wav", "audio/x-wav"):
            raise HTTPException(status_code=400, detail="Only WAV files are allowed")

        # Save to a temp path
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as out:
            out.write(await file.read())

        # Pipeline steps (sync + async)
        transcription = pipeline.transcriptor(temp_path)
        diarize = pipeline.diarize_response(transcription)
        call_path_res, golden_journey_res, kpi_res, compliance_res = await pipeline.process_transcript(
            transcript=transcription, diarize=diarize
        )
        total_silence, total_duration = pipeline.calculate_silence_and_duration(transcription)
        csat_score = pipeline.calculate_csat_score(diarize)

        # Parse derived structures needed for image gen
        try:
            kpi_json = json.loads(kpi_res) if isinstance(kpi_res, str) else kpi_res
        except Exception:
            kpi_json = {"topics": []}
        wordcloud_image_base64 = pipeline.generate_wordcloud_base64(kpi_json.get("topics", []))
        sentiment_chart_image_base64 = pipeline.generate_sentiment_chart_base64(diarize)
        call_path_image_base64 = pipeline.generate_call_path_image_base64(call_path_res)

        # PDF report
        report_pdf_base64 = pipeline.generate_report_pdf_base64(
            di=diarize,
            call_path=call_path_res,
            kpi=kpi_res,
            golden_j=golden_journey_res,
            compliance=compliance_res,
            call_dur=total_duration,
        )

        # Build response with exact schema
        response_payload = {
            "transcription": transcription,
            "diarize": diarize,
            "call_path": call_path_res,
            "golden_journey": json.loads(golden_journey_res) if _is_json(golden_journey_res) else golden_journey_res,
            "kpi": json.loads(kpi_res) if _is_json(kpi_res) else kpi_res,
            "compliance": json.loads(compliance_res) if _is_json(compliance_res) else compliance_res,
            "total_silence": total_silence,
            "total_duration": total_duration,
            "csat_score": csat_score,
            "wordcloud_image_base64": wordcloud_image_base64,
            "sentiment_chart_image_base64": sentiment_chart_image_base64,
            "call_path_image_base64": call_path_image_base64,
            "report_pdf_base64": report_pdf_base64,
        }
        return JSONResponse(content=response_payload)
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"error": he.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Unexpected error", "details": {"message": str(e)}})


def _is_json(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        json.loads(value)
        return True
    except Exception:
        return False


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}
