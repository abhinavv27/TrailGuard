"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams } from "next/navigation"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Skeleton } from "@/components/ui/Skeleton"
import { ErrorState } from "@/components/ui/ErrorState"
import { Table } from "@/components/ui/Table"
import { AppShell } from "@/components/layout/AppShell"
import {
  Shield,
  TrendingUp,
  TrendingDown,
  Users,
  Clock,
  Share2,
  AlertTriangle,
  FileText,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react"

export default function AccountPage() {
  const params = useParams()
  const accountId = params.id as string

  const { data: account, isLoading: accountLoading, error: accountError, refetch } = useQuery({
    queryKey: ["account", accountId],
    queryFn: () => api.accounts.get(accountId),
  })

  const { data: transactions } = useQuery({
    queryKey: ["account-transactions", accountId],
    queryFn: () => api.accounts.transactions(accountId),
    enabled: !!accountId,
  })

  if (accountError) {
    return (
      <AppShell>
        <ErrorState title="Failed to load account" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  const patterns = account?.patterns || []
  const metrics = account?.metrics || {}

  return (
    <AppShell>
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold text-slate-100">Account Intelligence Profile</h1>
          {accountLoading ? (
            <Skeleton className="h-6 w-20" />
          ) : (
            account?.risk_score !== undefined && (
              <Badge
                variant={
                  account.risk_score > 0.7
                    ? "critical"
                    : account.risk_score > 0.5
                    ? "high"
                    : account.risk_score > 0.3
                    ? "medium"
                    : "low"
                }
              >
                Risk: {Math.round(account.risk_score * 100)}%
              </Badge>
            )
          )}
        </div>
        <p className="text-sm text-slate-500 font-mono">{accountId}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {accountLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <Skeleton className="h-4 w-20 mb-2" />
              <Skeleton className="h-7 w-16" />
            </Card>
          ))
        ) : (
          <>
            <Card>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">Incoming Value</p>
                  <p className="text-2xl font-bold text-green-400 mt-1">
                    ${(metrics.incoming_value || 0).toLocaleString()}
                  </p>
                </div>
                <ArrowDownRight className="text-green-400" size={20} />
              </div>
            </Card>
            <Card>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">Outgoing Value</p>
                  <p className="text-2xl font-bold text-red-400 mt-1">
                    ${(metrics.outgoing_value || 0).toLocaleString()}
                  </p>
                </div>
                <ArrowUpRight className="text-red-400" size={20} />
              </div>
            </Card>
            <Card>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">Unique Counterparties</p>
                  <p className="text-2xl font-bold text-slate-100 mt-1">{metrics.unique_counterparties || 0}</p>
                </div>
                <Users className="text-blue-400" size={20} />
              </div>
            </Card>
            <Card>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-400">Avg Holding Time</p>
                  <p className="text-2xl font-bold text-slate-100 mt-1">
                    {metrics.avg_holding_time ? `${Math.round(metrics.avg_holding_time / 3600)}h` : "N/A"}
                  </p>
                </div>
                <Clock className="text-purple-400" size={20} />
              </div>
            </Card>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card className="lg:col-span-1">
          <h3 className="text-sm font-medium text-slate-300 mb-3">Graph Metrics</h3>
          <div className="space-y-3">
            {accountLoading ? (
              Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-8 w-full" />)
            ) : (
              <>
                {[
                  { label: "Degree Centrality", value: metrics.degree_centrality, color: "text-cyan-400" },
                  { label: "Betweenness", value: metrics.betweenness, color: "text-blue-400" },
                  { label: "PageRank", value: metrics.page_rank, color: "text-purple-400" },
                  { label: "Clustering Coeff", value: metrics.clustering_coefficient, color: "text-green-400" },
                ].map((m) => (
                  <div key={m.label} className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">{m.label}</span>
                    <span className={`text-sm font-medium ${m.color}`}>
                      {m.value !== undefined ? m.value.toFixed(4) : "N/A"}
                    </span>
                  </div>
                ))}
              </>
            )}
          </div>
        </Card>

        <Card className="lg:col-span-2">
          <h3 className="text-sm font-medium text-slate-300 mb-3">Detected Patterns</h3>
          {accountLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : patterns.length > 0 ? (
            <div className="space-y-2">
              {patterns.map((pattern: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between bg-navy-700/50 rounded-lg px-4 py-3">
                  <div className="flex items-center gap-2">
                    <AlertTriangle size={14} className="text-amber-400" />
                    <span className="text-sm text-slate-200">{pattern.name || pattern.type}</span>
                  </div>
                  <Badge variant={pattern.severity?.toLowerCase() || "medium"}>
                    {pattern.severity || "DETECTED"}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No suspicious patterns detected</p>
          )}
        </Card>
      </div>

      <Card className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-slate-300">Linked Transactions</h3>
          <Button variant="ghost" size="sm">
            <Share2 size={14} className="mr-1" /> View in Graph
          </Button>
        </div>
        {transactions && transactions.length > 0 ? (
          <Table
            columns={[
              { key: "id", header: "TX ID", render: (t: any) => <span className="font-mono text-xs text-slate-300">{t.id?.slice(0, 16)}...</span> },
              { key: "source", header: "Source", render: (t: any) => <span className="text-xs text-slate-400">{t.source_account?.slice(0, 12)}...</span> },
              { key: "destination", header: "Destination", render: (t: any) => <span className="text-xs text-slate-400">{t.destination_account?.slice(0, 12)}...</span> },
              { key: "amount", header: "Amount", render: (t: any) => <span className="text-sm font-medium text-slate-200">${(t.amount || 0).toLocaleString()}</span> },
              { key: "timestamp", header: "Date", render: (t: any) => <span className="text-xs text-slate-500">{t.timestamp ? new Date(t.timestamp).toLocaleDateString() : "-"}</span> },
            ]}
            data={transactions}
            keyExtractor={(t: any) => t.id}
          />
        ) : (
          <p className="text-sm text-slate-500">No transactions found</p>
        )}
      </Card>

      <Card>
        <h3 className="text-sm font-medium text-slate-300 mb-3">Evidence</h3>
        {account?.evidence?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {account.evidence.map((ev: any, idx: number) => (
              <div key={idx} className="bg-navy-700/50 rounded-lg p-3 border border-navy-600">
                <div className="flex items-center gap-2 mb-2">
                  <FileText size={14} className="text-cyan-400" />
                  <span className="text-xs font-medium text-slate-200">{ev.title || ev.type || "Evidence"}</span>
                </div>
                <p className="text-xs text-slate-500">{ev.description || ev.content || "No description"}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No evidence collected</p>
        )}
      </Card>
    </AppShell>
  )
}
