import React from 'react'

export type InfoStatus = 'good' | 'neutral' | 'bad'

interface Props {
  title?: string
  content: React.ReactNode
  status?: InfoStatus
}

const statusClass: Record<InfoStatus, string> = {
  good: 'badge good',
  neutral: 'badge neutral',
  bad: 'badge bad',
}

export function InfoCard({ title, content, status = 'neutral' }: Props) {
  return (
    <div className="card">
      {title ? <h3>{title}</h3> : null}
      <div>{content}</div>
      <div style={{ marginTop: 8 }}>
        <span className={statusClass[status]}>{status}</span>
      </div>
    </div>
  )
}
