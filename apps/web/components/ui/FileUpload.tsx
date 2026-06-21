"use client"

import { useState, useRef, useCallback } from "react"
import { Upload, File, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface FileUploadProps {
  onUpload: (file: File) => void
  accept?: string
  maxSize?: number
  className?: string
}

export function FileUpload({ onUpload, accept = ".csv,.json,.xlsx", maxSize = 50, className }: FileUploadProps) {
  const [dragOver, setDragOver] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) {
      setFile(f)
      onUpload(f)
    }
  }, [onUpload])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      setFile(f)
      onUpload(f)
    }
  }, [onUpload])

  const clear = useCallback(() => {
    setFile(null)
    if (inputRef.current) inputRef.current.value = ""
  }, [])

  return (
    <div className={cn("w-full", className)}>
      {!file ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={cn(
            "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors",
            dragOver
              ? "border-blue-500 bg-blue-50"
              : "border-slate-300 hover:border-slate-400 bg-white"
          )}
        >
          <Upload className="mx-auto mb-3 text-slate-400" size={36} />
          <p className="text-slate-700 font-medium mb-1">Drop file here or click to browse</p>
          <p className="text-xs text-slate-500">Supports {accept} (max {maxSize}MB)</p>
          <input ref={inputRef} type="file" accept={accept} onChange={handleChange} className="hidden" />
        </div>
      ) : (
        <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-4 py-3">
          <div className="flex items-center gap-3">
            <File className="text-blue-600" size={20} />
            <div>
              <p className="text-sm text-slate-800">{file.name}</p>
              <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <button onClick={clear} className="text-slate-400 hover:text-slate-600 transition-colors">
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  )
}
