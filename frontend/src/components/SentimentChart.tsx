import React from 'react'

export function SentimentChart({ imageBase64 }: { imageBase64?: string | null }) {
  if (!imageBase64) return null
  return (
    <div className="card">
      <h3>Sentiment</h3>
      <img className="responsive" src={imageBase64} alt="Sentiment Chart" />
    </div>
  )
}
