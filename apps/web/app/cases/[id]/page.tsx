"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"
import { ErrorState } from "@/components/ui/ErrorState"
import { AppShell } from "@/components/layout/AppShell"
import {
  Briefcase,
  Clock,
  AlertTriangle,
  Users,
  FileText,
  Plus,
  Send,
  Loader2,
  Sparkles,
  ArrowLeft,
} from "lucide-react"
import { toast } from "sonner"

export default function CaseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const caseId = params.id as string
  const queryClient = useQueryClient()
  const [noteContent, setNoteContent] = useState("")
  const [generatingReport, setGeneratingReport] = useState(false)

  const { data: caseData, isLoading, error, refetch } = useQuery({
    queryKey: ["case", caseId],
    queryFn: () => api.cases.get(caseId),
  })

  const addNoteMutation = useMutation({
    mutationFn: (content: string) => api.cases.addNote(caseId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["case", caseId] })
      setNoteContent("")
      toast.success("Note added")
    },
    onError: (err: any) => toast.error(err.message),
  })

  const handleGenerateReport = async () => {
    setGeneratingReport(true)
    try {
      await api.cases.generateReport(caseId)
      toast.success("Report generated")
      router.push(`/reports/${caseId}`)
    } catch {
      toast.error("Failed to generate report")
    } finally {
      setGeneratingReport(false)
    }
  }

  const handleStatusChange = async (status: string) => {
    try {
      await api.cases.update(caseId, { status })
      queryClient.invalidateQueries({ queryKey: ["case", caseId] })
      toast.success(`Case status updated to ${status}`)
    } catch {
      toast.error("Failed to update status")
    }
  }

  if (error) {
    return (
      <AppShell>
        <ErrorState title="Failed to load case" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  return (
    <AppShell>
      <button
        onClick={() => router.push("/cases")}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-4 transition-colors"
      >
        <ArrowLeft size={16} />
        Back to Cases
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          {isLoading ? (
            <Skeleton className="h-8 w-64 mb-2" />
          ) : (
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-slate-900">
                {caseData?.title || `Case ${caseId?.slice(0, 8)}`}
              </h1>
              <Badge
                variant={
                  caseData?.status === "open"
                    ? "critical"
                    : caseData?.status === "under_review"
                    ? "high"
                    : "low"
                }
              >
                {caseData?.status || "OPEN"}
              </Badge>
            </div>
          )}
          <p className="text-sm text-slate-500 font-mono">{caseId}</p>
        </div>
        <div className="flex gap-2">
          {caseData?.status !== "closed" && (
            <>
              {caseData?.status !== "under_review" && (
                <Button variant="secondary" onClick={() => handleStatusChange("under_review")}>
                  Mark Under Review
                </Button>
              )}
              <Button variant="secondary" onClick={() => handleStatusChange("closed")}>
                Close Case
              </Button>
            </>
          )}
          <Button onClick={handleGenerateReport} disabled={generatingReport}>
            {generatingReport ? (
              <Loader2 size={16} className="mr-2 animate-spin" />
            ) : (
              <FileText size={16} className="mr-2" />
            )}
            Generate Report
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-6">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h3 className="text-sm font-medium text-slate-700 mb-3">Evidence Timeline</h3>
              {caseData?.evidence?.length > 0 ? (
                <div className="space-y-3">
                  {caseData.evidence.map((ev: any, idx: number) => (
                    <div key={idx} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className="w-2 h-2 rounded-full bg-blue-600 mt-1.5" />
                        {idx < caseData.evidence.length - 1 && (
                          <div className="w-px h-full bg-slate-200" />
                        )}
                      </div>
                      <div className="flex-1 pb-3">
                        <p className="text-sm text-slate-800">{ev.title || ev.type || "Evidence"}</p>
                        <p className="text-xs text-slate-500">{ev.description || ev.content}</p>
                        <p className="text-[10px] text-slate-500 mt-1">
                          {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : ""}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No evidence collected yet</p>
              )}
            </Card>

            <Card>
              <h3 className="text-sm font-medium text-slate-700 mb-3">Analyst Notes</h3>
              <div className="space-y-3 mb-4">
                {caseData?.notes?.length > 0 ? (
                  caseData.notes.map((note: any, idx: number) => (
                    <div key={idx} className="bg-slate-100/50 rounded-lg p-3">
                      <p className="text-sm text-slate-800">{note.content}</p>
                      <p className="text-xs text-slate-500 mt-1">
                        {note.author || "Analyst"} — {note.created_at ? new Date(note.created_at).toLocaleString() : ""}
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-500">No notes yet</p>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  placeholder="Add an observation..."
                  className="input flex-1"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && noteContent.trim()) {
                      addNoteMutation.mutate(noteContent)
                    }
                  }}
                />
                <Button
                  size="sm"
                  disabled={!noteContent.trim() || addNoteMutation.isPending}
                  onClick={() => addNoteMutation.mutate(noteContent)}
                >
                  <Send size={14} />
                </Button>
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <h3 className="text-sm font-medium text-slate-700 mb-3">Details</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Alerts</span>
                  <span className="text-slate-800">{caseData?.alert_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Accounts</span>
                  <span className="text-slate-800">{caseData?.account_count || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Total Volume</span>
                  <span className="text-slate-800">
                    ${(caseData?.total_volume || 0).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Created</span>
                  <span className="text-slate-800">
                    {caseData?.created_at ? new Date(caseData.created_at).toLocaleDateString() : "N/A"}
                  </span>
                </div>
              </div>
            </Card>

            {caseData?.linked_accounts?.length > 0 && (
              <Card>
                <h3 className="text-sm font-medium text-slate-700 mb-3">Linked Accounts</h3>
                <div className="space-y-2">
                  {caseData.linked_accounts.map((acc: any, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-slate-100/50 rounded-lg px-3 py-2 cursor-pointer hover:bg-slate-100 transition-colors"
                      onClick={() => router.push(`/accounts/${acc.id}`)}
                    >
                      <span className="text-sm text-slate-800 font-mono text-xs">
                        {acc.id?.slice(0, 16)}...
                      </span>
                      <Badge variant={acc.risk?.toLowerCase() || "medium"}>
                        {acc.risk || "UNKNOWN"}
                      </Badge>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            <Card>
              <h3 className="text-sm font-medium text-slate-700 mb-3">AI Summary</h3>
              <div className="bg-slate-100/50 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={14} className="text-amber-400" />
                  <span className="text-xs text-amber-400 font-medium">AI Analysis</span>
                </div>
                <p className="text-sm text-slate-500">
                  {caseData?.ai_summary || "AI summary will appear after report generation."}
                </p>
              </div>
            </Card>
          </div>
        </div>
      )}
    </AppShell>
  )
}
