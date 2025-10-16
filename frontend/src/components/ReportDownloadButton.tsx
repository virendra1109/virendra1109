import React from 'react'

export function ReportDownloadButton({ pdfBase64 }: { pdfBase64?: string | null }) {
  if (!pdfBase64) return null

  const onClick = () => {
    const link = document.createElement('a')
    link.href = pdfBase64
    link.download = 'CallCentreReport.pdf'
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  return (
    <button className="button" onClick={onClick}>Download Report</button>
  )
}
