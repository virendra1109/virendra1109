import React from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/api'
import type { AnalyzeResponse } from '@/types'

interface Props {
  onAnalyzeComplete: (res: AnalyzeResponse) => void
}

export function UploadPanel({ onAnalyzeComplete }: Props) {
  const [file, setFile] = React.useState<File | null>(null)

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file')
      const form = new FormData()
      form.append('file', file)
      const { data } = await api.post<AnalyzeResponse>('/api/analyze', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      return data
    },
    onSuccess: (data) => onAnalyzeComplete(data),
  })

  const onDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const f = e.dataTransfer.files[0]
      if (f.type !== 'audio/wav' && f.type !== 'audio/x-wav') {
        alert('Only WAV files are allowed')
        return
      }
      setFile(f)
    }
  }

  const onPick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    if (f.type !== 'audio/wav' && f.type !== 'audio/x-wav') {
      alert('Only WAV files are allowed')
      return
    }
    setFile(f)
  }

  return (
    <div className="card">
      <h3>Upload WAV</h3>
      <div className="upload" onDragOver={(e) => e.preventDefault()} onDrop={onDrop}>
        {file ? <div>Selected: {file.name}</div> : <div>Drag & drop or click to select</div>}
        <div style={{ marginTop: 12 }}>
          <input type="file" accept="audio/wav" onChange={onPick} />
        </div>
      </div>
      <div style={{ marginTop: 12 }}>
        <button className="button" disabled={!file || mutation.isPending} onClick={() => mutation.mutate()}>
          {mutation.isPending ? <span className="spinner" /> : 'Transcribe and Analyze'}
        </button>
      </div>
    </div>
  )
}
