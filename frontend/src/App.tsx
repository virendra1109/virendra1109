import React, { useMemo, useState } from 'react'
import { UploadPanel } from '@/components/UploadPanel'
import { ConversationView } from '@/components/ConversationView'
import { InfoCard } from '@/components/InfoCard'
import { CallPathGraph } from '@/components/CallPathGraph'
import { WordCloud } from '@/components/WordCloud'
import { SentimentChart } from '@/components/SentimentChart'
import { ReportDownloadButton } from '@/components/ReportDownloadButton'
import type { AnalyzeResponse, TranscriptEntry } from '@/types'
import Lottie from 'lottie-react'
import headerAnim from './lottie.json'

export default function App() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null)

  const transcript: TranscriptEntry[] = useMemo(() => {
    if (!result) return []
    try {
      const obj = JSON.parse(result.diarize)
      if (Array.isArray(obj?.transcript)) return obj.transcript
    } catch {}
    return result.transcription
  }, [result])

  const kpi = result?.kpi
  const compliance = result?.compliance as any
  const golden = result?.golden_journey as any

  return (
    <div>
      <div className="header">
        <h1>📞 Call Centre Analysis</h1>
        <div style={{ maxWidth: 520, margin: '0 auto' }}>
          <Lottie animationData={headerAnim} loop style={{ height: 300 }} />
        </div>
      </div>
      <div className="container">
        <UploadPanel onAnalyzeComplete={setResult} />

        {result && (
          <div className="grid" style={{ marginTop: 16 }}>
            <div>
              <ConversationView transcript={transcript} />
              <div className="grid">
                <InfoCard title="Best Call Journey" content={
                  golden && (typeof golden === 'string' ? golden : (golden['golden journey']?.toLowerCase?.() === 'no' ? (golden.reason || 'Not met') : 'Golden journey condition met.'))
                } status={
                  golden && typeof golden !== 'string' && golden['golden journey']?.toLowerCase?.() === 'no' ? 'bad' : 'good'
                } />
                <InfoCard title="Compliance" content={
                  compliance && typeof compliance !== 'string' ? (
                    <div>
                      <div>{compliance['personal advice']?.toLowerCase?.() === 'yes' ? 'Personal Advice Given' : 'No Personal Advice'}</div>
                      <div>{compliance['pressure selling']?.toLowerCase?.() === 'yes' ? 'Pressure Selling' : 'No Pressure Selling'}</div>
                      {compliance.reason && <div>Reason: {compliance.reason}</div>}
                    </div>
                  ) : '—'
                } status={
                  compliance && typeof compliance !== 'string' && (compliance['personal advice']?.toLowerCase?.() === 'yes' || compliance['pressure selling']?.toLowerCase?.() === 'yes') ? 'bad' : 'good'
                } />
                <CallPathGraph callPath={result.call_path} imageBase64={result.call_path_image_base64} />
              </div>
            </div>
            <div>
              <div className="grid">
                <InfoCard title="🔇 Total Silence" content={result.total_silence} />
                <InfoCard title="⏱️ Total Duration" content={result.total_duration} />
                <InfoCard title="📜 Summary" content={kpi?.summary ?? '—'} />
                <InfoCard title="🎯 Agenda" content={kpi?.agenda ?? '—'} />
                <InfoCard title="😊 Sentiment" content={kpi?.sentiment ?? '—'} status={
                  kpi?.sentiment?.toLowerCase() === 'positive' ? 'good' : kpi?.sentiment?.toLowerCase() === 'negative' ? 'bad' : 'neutral'} />
                <InfoCard title="⭐ CSAT Score" content={(result.csat_score ?? 0) + '%'} status={'good'} />
              </div>
              <WordCloud imageBase64={result.wordcloud_image_base64} />
              <SentimentChart imageBase64={result.sentiment_chart_image_base64} />
              <div style={{ marginTop: 12 }}>
                <ReportDownloadButton pdfBase64={result.report_pdf_base64} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
