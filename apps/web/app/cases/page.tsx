"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { TableSkeleton } from "@/components/ui/Skeleton"
import { AppShell } from "@/components/layout/AppShell"
import { Briefcase, ArrowRight } from "lucide-react"

export default function CasesPage() {
  const router = useRouter()

  const { data: cases, isLoading, error, refetch } = useQuery({
    queryKey: ["cases"],
    queryFn: () => api.cases.list(),
  })

  if (error) {
    return (
      <AppShell>
        <ErrorState title="Failed to load cases" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Investigation Cases</h1>
        <p className="text-sm text-slate-500 mt-1">Manage financial crime investigations</p>
      </div>

      {isLoading ? (
        <TableSkeleton rows={5} />
      ) : cases && cases.length > 0 ? (
        <div className="space-y-3">
          {cases.map((c: any) => (
            <Card
              key={c.id}
              className="hover:border-slate-300 transition-colors cursor-pointer"
              onClick={() => router.push(`/cases/${c.id}`)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-sm font-medium text-slate-800">{c.title || `Case ${c.id.slice(0, 8)}`}</h3>
                    <Badge variant={c.status === "open" ? "high" : c.status === "under_review" ? "medium" : "low"}>
                      {c.status || "OPEN"}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span>Alerts: {c.alert_count || 0}</span>
                    <span>Accounts: {c.account_count || 0}</span>
                    <span>Created: {c.created_at ? new Date(c.created_at).toLocaleDateString() : "N/A"}</span>
                  </div>
                </div>
                <ArrowRight size={16} className="text-slate-500 mt-2" />
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Briefcase size={40} />}
          title="No cases"
          description="Open an investigation from the Alert Center to create a case"
        />
      )}
    </AppShell>
  )
}
