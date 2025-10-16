export interface TranscriptEntry {
  speaker: string; // "Agent" | "Customer"
  start_time: string; // "0:00" or "HH:MM:SS"
  end_time: string;
  text: string;
  sentiment?: string; // "Positive"|"Neutral"|"Negative" etc
  quick_replies?: string[];
}

export interface CallPathEntry {
  Timestamp: string;
  Speaker: string;
  Stage: string;
}

export interface AnalyzeResponse {
  transcription: TranscriptEntry[];
  diarize: string;
  call_path: CallPathEntry[] | string;
  golden_journey: { "golden journey": string; reason?: string } | string;
  kpi: {
    summary: string;
    agenda: string;
    sentiment: string;
    topics: string[];
    category: string;
    escalation: string;
    escalation_reason?: string;
  };
  compliance: { "personal advice": string; "pressure selling": string; reason?: string };
  total_silence: string;
  total_duration: string;
  csat_score?: number;
  wordcloud_image_base64?: string;
  sentiment_chart_image_base64?: string;
  call_path_image_base64?: string;
  report_pdf_base64?: string;
}
