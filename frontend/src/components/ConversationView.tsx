import React from 'react'
import type { TranscriptEntry } from '@/types'

function sentimentEmoji(s?: string) {
  const m: Record<string, string> = { Positive: '😊', Neutral: '😐', Negative: '😡' }
  if (!s) return ''
  const key = s.charAt(0).toUpperCase() + s.slice(1).toLowerCase()
  return m[key] || ''
}

export function ConversationView({ transcript }: { transcript: TranscriptEntry[] }) {
  return (
    <div className="card">
      <h3>Call Conversation</h3>
      <div className="chat">
        {transcript.map((t, idx) => (
          <div key={idx} className={`bubble ${t.speaker === 'Agent' ? 'agent' : 'customer'}`} title={`Sentiment: ${t.sentiment ?? ''}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div>{t.speaker === 'Agent' ? '🤖' : '👤'}</div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>{t.start_time} - {t.end_time}</div>
            </div>
            <div style={{ marginTop: 6 }}>{t.text} {sentimentEmoji(t.sentiment)}</div>
            {t.quick_replies && t.quick_replies.length > 0 && (
              <div style={{ marginTop: 6, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {t.quick_replies.map((q, qidx) => (
                  <button key={qidx} className="badge neutral" style={{ border: '1px solid #e5e7eb' }}>{q}</button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
