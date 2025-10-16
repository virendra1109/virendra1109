import React from 'react'

export function WordCloud({ imageBase64 }: { imageBase64?: string | null }) {
  if (!imageBase64) return null
  return (
    <div className="card">
      <h3>Word Cloud</h3>
      <img className="responsive" src={imageBase64} alt="Word Cloud" />
    </div>
  )
}
