from __future__ import annotations

import asyncio
import base64
import io
import json
from typing import List, Tuple, Union, Dict, Any

from .utils import decode_json_first, to_base64_data_uri

# The following imports assume the existing project modules are importable.
# If their paths differ, adjust PYTHONPATH or relative imports accordingly.
try:
    from src.adapters.azure_speech import AzureSpeechHelper  # type: ignore
    from src.adapters.azure_openai import (  # type: ignore
        AzureOpenAIHelper,
        AsyncAzureOpenAIHelper,
        AzureOpenAI_mini,
        AsyncAzureOpenANano,
        AsyncAzureOpenAI_mini,
    )
    from src.prompts import (  # type: ignore
        diarize_prompt,
        compliance_prompt,
        kpi_prompt,
        golden_journey_prompt,
        call_path_prompt,
        report_prompt,
    )
except Exception:  # pragma: no cover - placeholder if modules are absent in this workspace
    AzureSpeechHelper = None  # type: ignore
    AzureOpenAIHelper = None  # type: ignore
    AsyncAzureOpenAIHelper = None  # type: ignore
    AzureOpenAI_mini = None  # type: ignore
    AsyncAzureOpenANano = None  # type: ignore
    AsyncAzureOpenAI_mini = None  # type: ignore
    diarize_prompt = ""
    compliance_prompt = ""
    kpi_prompt = "{csat_score}"
    golden_journey_prompt = ""
    call_path_prompt = "{start_time}"
    report_prompt = ""


# Instantiate clients (reuse singletons similarly to Streamlit version)
openaiclient = AzureOpenAIHelper() if AzureOpenAIHelper else None
openaiclientmini = AzureOpenAI_mini() if AzureOpenAI_mini else None
asyncopenaiclient = AsyncAzureOpenAIHelper() if AsyncAzureOpenAIHelper else None
asyncopenaiclientnano = AsyncAzureOpenANano() if AsyncAzureOpenANano else None
asyncopenaiclientmini = AsyncAzureOpenAI_mini() if AsyncAzureOpenAI_mini else None
speechclient = AzureSpeechHelper() if AzureSpeechHelper else None


# Reimplemented helpers (copied logic simplified and made side-effect free)
def speech_transcription_to_text(transcript: List[Dict[str, Any]]) -> str:
    texts = [entry.get("text", "") for entry in transcript]
    return " ".join(texts)


def transcriptor(wav_file: str):
    if speechclient and hasattr(speechclient, "recognize_from_file_parallel"):
        return speechclient.recognize_from_file_parallel(wav_file=wav_file)
    # Fallback stub transcript to keep end-to-end flow working without Azure
    return [
        {
            "speaker": "Agent",
            "start_time": "00:00:00",
            "end_time": "00:00:05",
            "text": "Hello, thanks for calling. How can I help you today?",
            "sentiment": "Neutral",
            "quick_replies": ["Billing", "Technical Support", "Sales"],
        },
        {
            "speaker": "Customer",
            "start_time": "00:00:05",
            "end_time": "00:00:12",
            "text": "Hi, I have a question about my latest bill.",
            "sentiment": "Neutral",
        },
        {
            "speaker": "Agent",
            "start_time": "00:00:12",
            "end_time": "00:00:20",
            "text": "Sure, I'd be happy to look into that for you.",
            "sentiment": "Positive",
        },
        {
            "speaker": "Customer",
            "start_time": "00:00:20",
            "end_time": "00:00:35",
            "text": "Thanks. It seems higher than usual and I'm not sure why.",
            "sentiment": "Neutral",
        },
    ]


def diarize_response(transcript: List[Dict[str, Any]]):
    text_paragraph = speech_transcription_to_text(transcript)
    if openaiclientmini and hasattr(openaiclientmini, "get_response"):
        message = [
            {"role": "system", "content": diarize_prompt},
            {"role": "user", "content": text_paragraph},
        ]
        diarize = openaiclientmini.get_response(message)
        return diarize
    # Fallback: echo structured transcript back as diarize JSON
    diarize_obj = {"transcript": []}
    for entry in transcript:
        diarize_obj["transcript"].append(
            {
                "speaker": entry.get("speaker", "Unknown"),
                "start_time": entry.get("start_time", "0:00"),
                "end_time": entry.get("end_time", "0:00"),
                "text": entry.get("text", ""),
                "sentiment": (entry.get("sentiment") or "Neutral"),
                "quick_replies": entry.get("quick_replies"),
            }
        )
    return json.dumps(diarize_obj)


def calculate_csat_score(data: Union[str, Dict[str, Any]]) -> float:
    if isinstance(data, str):
        data = decode_json_first(data)
    sentiment_weights = {
        "very satisfied": 5,
        "satisfied": 4,
        "neutral": 3,
        "dissatisfied": 2,
        "very dissatisfied": 1,
    }
    total_weight = 0
    count = 0
    for utt in data.get("transcript", []):
        if utt.get("speaker") != "Customer":
            continue
        sentiment = utt.get("sentiment")
        if not sentiment:
            continue
        weight = sentiment_weights.get(str(sentiment).lower())
        if weight is None:
            continue
        total_weight += weight
        count += 1
    if count == 0:
        return 0.0
    csat_percentage = (total_weight / (count * 5)) * 100
    return round(csat_percentage, 2)


async def compliance_async(diarize: str) -> str:
    if asyncopenaiclientnano and hasattr(asyncopenaiclientnano, "get_response"):
        message = [
            {"role": "system", "content": compliance_prompt},
            {"role": "user", "content": diarize},
        ]
        return await asyncopenaiclientnano.get_response(message)
    # Fallback stub
    return json.dumps({"personal advice": "No", "pressure selling": "No", "reason": "Standard support conversation."})


async def kpi_async(diarize: str) -> str:
    if asyncopenaiclientmini and hasattr(asyncopenaiclientmini, "get_response"):
        message = [
            {"role": "system", "content": kpi_prompt.format(csat_score=calculate_csat_score(diarize))},
            {"role": "user", "content": diarize},
        ]
        return await asyncopenaiclientmini.get_response(message)
    # Fallback stub
    topics = ["billing", "charges", "assistance", "account"]
    return json.dumps({
        "summary": "Customer queried higher-than-usual bill; agent investigated and clarified charges.",
        "agenda": "Understand bill discrepancy and provide resolution.",
        "sentiment": "Positive",
        "topics": topics,
        "category": "Billing",
        "escalation": "No",
        "escalation_reason": "",
    })


async def golden_journey_async(diarize: str) -> str:
    if asyncopenaiclientnano and hasattr(asyncopenaiclientnano, "get_response"):
        message = [
            {"role": "system", "content": golden_journey_prompt},
            {"role": "user", "content": diarize},
        ]
        return await asyncopenaiclientnano.get_response(message)
    # Fallback stub
    return json.dumps({"golden journey": "Yes", "reason": "Greeting and closure present; proactive assistance provided."})


async def call_path_async(diarize: str, transcript: List[Dict[str, Any]]) -> str:
    if asyncopenaiclientmini and hasattr(asyncopenaiclientmini, "get_response"):
        start_time = [entry.get("start_time") for entry in transcript]
        message = [
            {"role": "system", "content": call_path_prompt.format(start_time=start_time)},
            {"role": "user", "content": diarize},
        ]
        return await asyncopenaiclientmini.get_response(message)
    # Fallback stub (list of dicts encoded as JSON)
    call_list = [
        {"Timestamp": "00:00:00", "Speaker": "Agent", "Stage": "Greeting"},
        {"Timestamp": "00:00:05", "Speaker": "Customer", "Stage": "Issue Stated"},
        {"Timestamp": "00:00:12", "Speaker": "Agent", "Stage": "Assistance Offered"},
        {"Timestamp": "00:00:20", "Speaker": "Customer", "Stage": "Clarification"},
        {"Timestamp": "00:00:35", "Speaker": "Agent", "Stage": "Closure"},
    ]
    return json.dumps(call_list)


async def process_transcript(transcript: List[Dict[str, Any]], diarize: str):
    call_path_res, golden_journey_res, kpi_res, compliance_res = await asyncio.gather(
        call_path_async(diarize, transcript),
        golden_journey_async(diarize),
        kpi_async(diarize),
        compliance_async(diarize),
    )
    return call_path_res, golden_journey_res, kpi_res, compliance_res


# Simple total silence/duration calculators

def _time_to_seconds_hms(time_str: str) -> int:
    parts = time_str.split(":")
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    return 0


def calculate_silence_and_duration(transcript_list: List[Dict[str, Any]]):
    if not transcript_list:
        return "0 seconds", "0 seconds"
    transcript_list = sorted(
        transcript_list, key=lambda x: _time_to_seconds_hms(str(x.get("start_time", "0:00")))
    )
    call_start = _time_to_seconds_hms(str(transcript_list[0].get("start_time", "0:00")))
    call_end = _time_to_seconds_hms(str(transcript_list[-1].get("end_time", "0:00")))
    total_duration = max(0, call_end - call_start)
    total_silence = 0
    for i in range(1, len(transcript_list)):
        prev_end = _time_to_seconds_hms(str(transcript_list[i - 1].get("end_time", "0:00")))
        current_start = _time_to_seconds_hms(str(transcript_list[i].get("start_time", "0:00")))
        gap = current_start - prev_end
        if gap > 0:
            total_silence += gap
    return f"{total_silence} seconds", f"{total_duration} seconds"


# Media generation (PNG) utilities using matplotlib/wordcloud/graphviz if available

def generate_wordcloud_base64(topics: List[str]) -> Union[str, None]:
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt
        from collections import Counter

        text = " ".join(topics) if topics else ""
        if not text:
            return None
        fig, ax = plt.subplots(figsize=(8, 4))
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        plt.close(fig)
        return to_base64_data_uri(buf.getvalue(), "image/png")
    except Exception:
        return None


def generate_sentiment_chart_base64(diarize: str) -> Union[str, None]:
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        diar = decode_json_first(diarize)
        sentiment_mapping = {
            "Very satisfied": 5,
            "Satisfied": 4,
            "Neutral": 3,
            "Dissatisfied": 2,
            "Very dissatisfied": 1,
        }
        data = []
        for entry in diar.get("transcript", []):
            speaker = entry.get("speaker", "Unknown")
            t_str = entry.get("start_time", "0:00")
            time_seconds = _time_to_seconds_hms(str(t_str))
            sentiment_str = str(entry.get("sentiment", "Neutral")).capitalize()
            sentiment_val = sentiment_mapping.get(sentiment_str, 3)
            data.append({
                "time_seconds": time_seconds,
                "sentiment": sentiment_val,
                "speaker": speaker,
            })
        if not data:
            return None
        df = pd.DataFrame(data)
        fig, ax = plt.subplots(figsize=(4, 2.5))
        for speaker in df["speaker"].unique():
            sub_df = df[df["speaker"] == speaker]
            ax.plot(
                sub_df["time_seconds"],
                sub_df["sentiment"],
                marker="o",
                linewidth=2,
                label=speaker,
            )
        ax.set_title("Sentiment Analysis Over Time", fontsize=8)
        ax.set_xlabel("Time (Seconds)", fontsize=6)
        ax.set_ylabel("Sentiment Score", fontsize=6)
        ax.set_ylim(1, 7)
        ax.grid(True, linestyle="--", linewidth=0.5)
        ax.legend(fontsize=6)
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        return to_base64_data_uri(buf.getvalue(), "image/png")
    except Exception:
        return None


def generate_call_path_image_base64(call_path_json_or_str: Union[str, Dict[str, Any]]) -> Union[str, None]:
    try:
        import graphviz
        if isinstance(call_path_json_or_str, str):
            call_path_json_or_str = json.loads(call_path_json_or_str)
        call_path = call_path_json_or_str
        if isinstance(call_path, dict) and "call path" in call_path:
            call_path = call_path["call path"]
        if not isinstance(call_path, list):
            return None
        dot = graphviz.Digraph(comment="Call Flow", graph_attr={"rankdir": "LR"})
        dot.attr(bgcolor="#FFFFFF")
        dot.attr("node", shape="ellipse", style="filled", fillcolor="#FFFFFF", fontcolor="black", color="black", fontsize="10", width="1.8", height="1.2")
        dot.attr("edge", color="black")
        for i, entry in enumerate(call_path):
            if not isinstance(entry, dict):
                continue
            speaker = entry.get("Speaker", "Unknown")
            timestamp = entry.get("Timestamp", "Unknown")
            stage = entry.get("Stage", "Unknown")
            label = f"{speaker}\n{timestamp}\n{stage}"
            dot.node(str(i), label)
        for i in range(len(call_path) - 1):
            dot.edge(str(i), str(i + 1))
        png_bytes = dot.pipe(format="png")
        return to_base64_data_uri(png_bytes, "image/png")
    except Exception:
        return None


def generate_report_pdf_base64(
    di: str,
    call_path: str,
    kpi: str,
    golden_j: str,
    compliance: str,
    call_dur: str,
) -> Union[str, None]:
    try:
        import re
        import pdfkit
        from datetime import date

        # Prepare HTML via LLM using the original report_prompt and helper client
        if openaiclient and hasattr(openaiclient, "get_response"):
            message = [
                {
                    "role": "system",
                    "content": report_prompt.format(
                        di=di,
                        call_path=call_path,
                        kpi=kpi,
                        gol_j=golden_j,
                        comp=compliance,
                        call_duration=call_dur,
                        call_date=date.today(),
                    ),
                }
            ]
            report = openaiclient.get_response(message, json_mode=True)
            data = json.loads(report)
        else:
            data = {
                "call_date": "",
                "call_dur": call_dur,
                "agent_name": "",
                "customer_name": "",
                "call_category": "",
                "highlight": "",
                "diarize_summary": "",
                "summary": "",
                "agenda": "",
                "sentiment": "",
                "topic_list": [],
                "escalation_status": "",
                "golden_journey": "",
                "call_path_summary": "",
                "compliance_summary": "",
                "overall_summary": "",
            }

        if isinstance(data.get("topic_list"), list):
            data["topic_list"] = ", ".join(data["topic_list"])  # type: ignore

        html_output = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Call Analysis Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; padding: 20px; background-color: #f4f4f4; }}
    h1, h2, h3 {{ color: #333; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    table, th, td {{ border: 1px solid #ddd; }}
    th, td {{ padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
    img {{ display: block; margin: 20px auto; }}
  </style>
</head>
<body>
  <h1>Call Analysis Report</h1>
  <h2>1. Call Overview</h2>
  <p><strong>Call Date:</strong> {data.get('call_date','')}</p>
  <p><strong>Call Duration:</strong> {call_dur}</p>
  <p><strong>Agent:</strong> {data.get('agent_name','')}</p>
  <p><strong>Customer:</strong> {data.get('customer_name','')}</p>
  <p><strong>Call Category:</strong> {data.get('call_category','')}</p>
  <p><strong>Key Highlights:</strong> {data.get('highlight','')}</p>
  <h2>2. Diarized Transcription Analysis</h2>
  <p>{data.get('diarize_summary','')}</p>
  <h2>3. KPI Analysis</h2>
  <p><strong>Summary:</strong> {data.get('summary','')}</p>
  <p><strong>Agenda:</strong> {data.get('agenda','')}</p>
  <p><strong>Sentiment:</strong> {data.get('sentiment','')}</p>
  <p><strong>Topics Discussed:</strong> {data.get('topic_list','')}</p>
  <p><strong>Escalation Status:</strong> {data.get('escalation_status','')}</p>
  <h2>4. Golden Journey Assessment</h2>
  <p>{data.get('golden_journey','')}</p>
  <h2>5. Call Path Breakdown</h2>
  <p>{data.get('call_path_summary','')}</p>
  <h2>6. Compliance Evaluation</h2>
  <p>{data.get('compliance_summary','')}</p>
  <h2>7. Overall Insights and Recommendations</h2>
  <p>{data.get('overall_summary','')}</p>
</body>
</html>
"""
        options = {
            "no-stop-slow-scripts": "",
            "disable-javascript": "",
            "enable-local-file-access": "",
        }
        pdf_bytes = pdfkit.from_string(html_output, False, options=options)
        return to_base64_data_uri(pdf_bytes, "application/pdf")
    except Exception:
        return None
