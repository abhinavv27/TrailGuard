"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"
import { ErrorState } from "@/components/ui/ErrorState"
import { AppShell } from "@/components/layout/AppShell"
import {
  FileText,
  Download,
  Printer,
  Shield,
  AlertTriangle,
  Users,
  Clock,
  ArrowLeft,
} from "lucide-react"
import { toast } from "sonner"

export default function ReportPage() {
  const params = useParams()
  const router = useRouter()
  const reportId = params.id as string

  const { data: report, isLoading, error, refetch } = useQuery({
    queryKey: ["report", reportId],
    queryFn: () => api.cases.getReport(reportId),
  })

  if (error) {
    return (
      <AppShell>
        <ErrorState title="Failed to load report" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  const handlePrint = () => {
    window.print()
  }

  const handleExportPDF = () => {
    toast.success("PDF export initiated (print to PDF recommended)")
    window.print()
  }

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6 print:hidden">
          <button
            onClick={() => router.push(`/cases/${reportId}`)}
            className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Case
          </button>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={handlePrint}>
              <Printer size={16} className="mr-1.5" /> Print
            </Button>
            <Button onClick={handleExportPDF}>
              <Download size={16} className="mr-1.5" /> Export PDF
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="space-y-6">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : (
          <div className="bg-navy-800 border border-navy-600 rounded-xl p-8 space-y-8">
            <div className="text-center border-b border-navy-600 pb-6">
              <img src="/logo.svg" alt="TrailGuard AI" className="w-10 h-10 mx-auto mb-3" />
              <h1 className="text-2xl font-bold text-slate-100">Investigation Report</h1>
              <p className="text-sm text-slate-500 mt-1">TrailGuard AI — Financial Crime Investigation Platform</p>
              {report?.created_at && (
                <p className="text-xs text-slate-500 mt-2">
                  Generated: {new Date(report.created_at).toLocaleString()}
                </p>
              )}
            </div>

            <section>
              <h2 className="text-lg font-semibold text-slate-100 mb-4">Case Metadata</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">Case ID</span>
                  <p className="text-slate-200 font-mono text-xs mt-1">{report?.case_id || reportId}</p>
                </div>
                <div>
                  <span className="text-slate-400">Title</span>
                  <p className="text-slate-200 mt-1">{report?.title || "Investigation Report"}</p>
                </div>
                <div>
                  <span className="text-slate-400">Status</span>
                  <Badge variant={report?.status === "closed" ? "low" : report?.status === "under_review" ? "high" : "critical"}>
                    {report?.status || "OPEN"}
                  </Badge>
                </div>
                <div>
                  <span className="text-slate-400">Created</span>
                  <p className="text-slate-200 mt-1">
                    {report?.created_at ? new Date(report.created_at).toLocaleDateString() : "N/A"}
                  </p>
                </div>
              </div>
            </section>

            <section className="border-t border-navy-600 pt-6">
              <div className="flex items-center gap-2 mb-4">
                <Shield size={18} className="text-cyan-400" />
                <h2 className="text-lg font-semibold text-slate-100">Risk Assessment</h2>
              </div>
              <div className="flex items-center gap-4 mb-4">
                <span className="text-sm text-slate-400">Risk Score:</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 h-2 bg-navy-600 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-red-400"
                      style={{ width: `${Math.min(100, (report?.risk_score || 0) * 100)}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-slate-200">
                    {Math.round((report?.risk_score || 0) * 100)}%
                  </span>
                </div>
              </div>
              {report?.reason_codes?.length > 0 && (
                <div>
                  <span className="text-sm text-slate-400">Reason Codes:</span>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {report.reason_codes.map((code: string, idx: number) => (
                      <span
                        key={idx}
                        className="bg-navy-600 text-slate-300 text-xs px-2 py-1 rounded font-mono"
                      >
                        {code}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </section>

            <section className="border-t border-navy-600 pt-6">
              <div className="flex items-center gap-2 mb-4">
                <Users size={18} className="text-blue-400" />
                <h2 className="text-lg font-semibold text-slate-100">Involved Accounts</h2>
              </div>
              {report?.accounts?.length > 0 ? (
                <div className="space-y-2">
                  {report.accounts.map((acc: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between bg-navy-700/50 rounded-lg px-4 py-3">
                      <span className="text-sm font-mono text-slate-200">{acc.id}</span>
                      <Badge variant={acc.risk?.toLowerCase() || "medium"}>{acc.risk || "UNKNOWN"}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No accounts listed</p>
              )}
            </section>

            <section className="border-t border-navy-600 pt-6">
              <div className="flex items-center gap-2 mb-4">
                <Clock size={18} className="text-purple-400" />
                <h2 className="text-lg font-semibold text-slate-100">Suspicious Transaction Timeline</h2>
              </div>
              {report?.transactions?.length > 0 ? (
                <div className="space-y-3">
                  {report.transactions.map((tx: any, idx: number) => (
                    <div key={idx} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className="w-2 h-2 rounded-full bg-red-400 mt-1.5" />
                        {idx < report.transactions.length - 1 && (
                          <div className="w-px h-full bg-navy-600" />
                        )}
                      </div>
                      <div className="flex-1 pb-3">
                        <p className="text-sm text-slate-200">
                          ${(tx.amount || 0).toLocaleString()} — {tx.source_account} → {tx.destination_account}
                        </p>
                        <p className="text-xs text-slate-500">
                          {tx.timestamp ? new Date(tx.timestamp).toLocaleString() : ""}
                          {tx.type && <span> · {tx.type}</span>}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">No suspicious transactions recorded</p>
              )}
            </section>

            <section className="border-t border-navy-600 pt-6">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle size={18} className="text-amber-400" />
                <h2 className="text-lg font-semibold text-slate-100">Evidence</h2>
              </div>
              {report?.evidence?.length > 0 ? (
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-300">
                  {report.evidence.map((ev: any, idx: number) => (
                    <li key={idx}>{ev.title || ev.type || ev.description || `Evidence ${idx + 1}`}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500">No evidence collected</p>
              )}
            </section>

            {report?.notes?.length > 0 && (
              <section className="border-t border-navy-600 pt-6">
                <h2 className="text-lg font-semibold text-slate-100 mb-4">Analyst Notes</h2>
                <div className="space-y-3">
                  {report.notes.map((note: any, idx: number) => (
                    <div key={idx} className="bg-navy-700/50 rounded-lg p-3">
                      <p className="text-sm text-slate-300 italic">&ldquo;{note.content}&rdquo;</p>
                      <p className="text-xs text-slate-500 mt-1">
                        — {note.author || "Analyst"}, {note.created_at ? new Date(note.created_at).toLocaleDateString() : ""}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            )}

            <div className="border-t border-navy-600 pt-6">
              <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-4 text-center">
                <p className="text-xs text-amber-400 font-medium uppercase tracking-wider">
                  Synthetic Demonstration Only — Human Review Required
                </p>
                <p className="text-xs text-slate-500 mt-2">
                  This report was generated for demonstration purposes. All findings require independent verification
                  by qualified financial crime investigators before any action is taken.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  )
}
