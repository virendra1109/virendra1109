import React from 'react'
import type { CallPathEntry } from '@/types'

interface Props {
  callPath?: CallPathEntry[] | string
  imageBase64?: string | null
}

export function CallPathGraph({ callPath, imageBase64 }: Props) {
  if (imageBase64) {
    return (
      <div className="card">
        <h3>Call Path</h3>
        <img className="responsive" src={imageBase64} alt="Call Path" />
      </div>
    )
  }
  // fallback render as table if array is provided
  let entries: CallPathEntry[] = []
  if (Array.isArray(callPath)) entries = callPath
  else if (typeof callPath === 'string') {
    try {
      const obj = JSON.parse(callPath)
      entries = Array.isArray(obj) ? obj : (obj['call path'] ?? [])
    } catch {}
  }
  return (
    <div className="card">
      <h3>Call Path</h3>
      <div style={{ overflow: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>Timestamp</th>
              <th style={{ textAlign: 'left' }}>Speaker</th>
              <th style={{ textAlign: 'left' }}>Stage</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e, i) => (
              <tr key={i}>
                <td>{e.Timestamp}</td>
                <td>{e.Speaker}</td>
                <td>{e.Stage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
