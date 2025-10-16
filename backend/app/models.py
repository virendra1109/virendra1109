from __future__ import annotations

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class TranscriptEntry(BaseModel):
    speaker: str  # "Agent" | "Customer"
    start_time: str  # "0:00" or "HH:MM:SS"
    end_time: str
    text: str
    sentiment: Optional[str] = None  # "Positive"|"Neutral"|"Negative" etc
    quick_replies: Optional[List[str]] = None


class CallPathEntry(BaseModel):
    Timestamp: str
    Speaker: str
    Stage: str


class KPIModel(BaseModel):
    summary: str
    agenda: str
    sentiment: str
    topics: List[str] = Field(default_factory=list)
    category: str
    escalation: str
    escalation_reason: Optional[str] = None


class ComplianceModel(BaseModel):
    personal_advice: str = Field(alias="personal advice")
    pressure_selling: str = Field(alias="pressure selling")
    reason: Optional[str] = None

    model_config = {
        "populate_by_name": True,
    }


class GoldenJourneyModel(BaseModel):
    golden_journey: str = Field(alias="golden journey")
    reason: Optional[str] = None

    model_config = {
        "populate_by_name": True,
    }


class AnalyzeResponse(BaseModel):
    transcription: List[TranscriptEntry]
    diarize: str  # stringified JSON (detailed diarize)
    call_path: Union[List[CallPathEntry], str]
    golden_journey: Union[GoldenJourneyModel, str]
    kpi: KPIModel
    compliance: ComplianceModel
    total_silence: str
    total_duration: str
    csat_score: Optional[float] = None
    wordcloud_image_base64: Optional[str] = None
    sentiment_chart_image_base64: Optional[str] = None
    call_path_image_base64: Optional[str] = None
    report_pdf_base64: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
