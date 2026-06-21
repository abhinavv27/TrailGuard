"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { TableSkeleton } from "@/components/ui/Skeleton"
import { AppShell } from "@/components/layout/AppShell"
import { Bell, Filter, Search, ChevronLeft, ChevronRight, AlertTriangle } from "lucide-react"
import { toast } from "sonner"

const severityOptions = ["all", "critical", "high", "medium", "low"]

export default function AlertsPage() {
  const router = useRouter()
  const [page, setPage] = useState(1)
  const [severityFilter, setSeverityFilter] = useState("all")
  const perPage = 10

  const params = new URLSearchParams()
  if (severityFilter !== "all") params.set("severity", severityFilter)
  params.set("skip", String((page - 1) * perPage))
  params.set("limit", String(perPage))

  const { data: alerts, isLoading, error, refetch } = useQuery({
    queryKey: ["alerts", severityFilter, page],
    queryFn: () => api.alerts.list(params.toString()),
  })

  const handleOpenInvestigation = async (alertId: string) => {
    try {
      const caseData = await api.alerts.createCase(alertId)
      toast.success("Investigation case created")
      router.push(`/cases/${caseData.case_id ?? caseData.id}`)
    } catch {
      toast.error("Failed to create investigation case")
    }
  }

  if (error) {
    return (
      <AppShell>
        <ErrorState title="Failed to load alerts" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Alert Center</h1>
        <p className="text-sm text-slate-500 mt-1">Monitor and investigate suspicious activity</p>
      </div>

      <Card className="mb-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-slate-500" />
            <span className="text-sm text-slate-500">Severity:</span>
          </div>
          <div className="flex gap-2">
            {severityOptions.map((opt) => (
              <button
                key={opt}
                onClick={() => { setSeverityFilter(opt); setPage(1) }}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  severityFilter === opt
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-500 hover:text-slate-800"
                }`}
              >
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {isLoading ? (
        <TableSkeleton rows={5} />
      ) : alerts && alerts.length > 0 ? (
        <>
          <div className="space-y-3 mb-6">
            {alerts.map((alert: any) => (
              <Card key={alert.id} className="hover:border-slate-300 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle
                        size={16}
                        className={
                          alert.severity === "critical"
                            ? "text-red-400"
                            : alert.severity === "high"
                            ? "text-orange-400"
                            : alert.severity === "medium"
                            ? "text-amber-400"
                            : "text-green-400"
                        }
                      />
                      <h3 className="text-sm font-medium text-slate-800">
                        {alert.title || alert.event_type || alert.alert_type || "Suspicious Activity Detected"}
                      </h3>
                      <Badge variant={alert.severity?.toLowerCase()}>
                        {alert.severity || "UNKNOWN"}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span>Entity: {alert.entity_id || alert.account_id || "N/A"}</span>
                      <span>Detector: {alert.detector_type || alert.event_type || "N/A"}</span>
                      {(alert.score !== undefined || alert.risk_score !== undefined) && (
                        <span>Score: {(alert.score ?? alert.risk_score).toFixed(0)}/100</span>
                      )}
                    </div>
                    {alert.reason_codes && alert.reason_codes.length > 0 && (
                      <div className="flex gap-2 mt-2">
                        {alert.reason_codes.map((code: string, idx: number) => (
                          <span
                            key={idx}
                            className="bg-slate-200 text-slate-700 text-[10px] px-2 py-0.5 rounded font-mono"
                          >
                            {code}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      size="sm"
                      onClick={() => router.push(`/accounts/${alert.entity_id || alert.account_id}`)}
                      variant="ghost"
                    >
                      View Account
                    </Button>
                    <Button size="sm" onClick={() => handleOpenInvestigation(alert.id)}>
                      Open Investigation
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          <div className="flex items-center justify-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft size={16} className="mr-1" /> Previous
            </Button>
            <span className="text-sm text-slate-500">Page {page}</span>
            <Button
              variant="ghost"
              size="sm"
              disabled={!alerts || alerts.length < perPage}
              onClick={() => setPage((p) => p + 1)}
            >
              Next <ChevronRight size={16} className="ml-1" />
            </Button>
          </div>
        </>
      ) : (
        <EmptyState
          icon={<Bell size={40} />}
          title="No alerts"
          description="No alerts match your current filters"
        />
      )}
    </AppShell>
  )
}
