"use client"

import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { CardSkeleton, TableSkeleton } from "@/components/ui/Skeleton"
import { ErrorState } from "@/components/ui/ErrorState"
import { Button } from "@/components/ui/Button"
import { AppShell } from "@/components/layout/AppShell"
import {
  Activity,
  Database,
  AlertTriangle,
  Briefcase,
  TrendingUp,
  Play,
  ArrowRight,
} from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

const riskColors: Record<string, string> = {
  low: "#4ade80",
  medium: "#fbbf24",
  high: "#fb923c",
  critical: "#f87171",
}

export default function DashboardPage() {
  const router = useRouter()

  const { data: summary, isLoading, error, refetch } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: () => api.dashboard.summary(),
  })

  const handleDemoScenario = async () => {
    try {
      await api.demo.injectScenario({ scenario_type: "rapid_mule_network" })
      toast.success("Demo scenario injected successfully")
      refetch()
    } catch {
      toast.error("Failed to inject demo scenario")
    }
  }

  if (error) {
    return (
      <AppShell>
        <ErrorState
          title="Failed to load dashboard"
          message="Could not connect to the backend API. Make sure the server is running."
          onRetry={() => refetch()}
        />
      </AppShell>
    )
  }

  const stats = [
    {
      label: "Total Transactions",
      value: summary?.total_transactions ?? 0,
      icon: Activity,
      color: "text-cyan-400",
    },
    {
      label: "Total Datasets",
      value: summary?.total_datasets ?? 0,
      icon: Database,
      color: "text-blue-400",
    },
    {
      label: "Flagged Accounts",
      value: summary?.flagged_accounts ?? 0,
      icon: AlertTriangle,
      color: "text-amber-400",
    },
    {
      label: "Active Cases",
      value: summary?.active_cases ?? 0,
      icon: Briefcase,
      color: "text-green-400",
    },
  ]

  const riskData = summary?.risk_distribution
    ? Object.entries(summary.risk_distribution).map(([name, value]) => ({ name, value }))
    : []

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Command Center</h1>
          <p className="text-sm text-slate-500 mt-1">Financial crime intelligence overview</p>
        </div>
        <Button onClick={handleDemoScenario}>
          <Play size={16} className="mr-2" />
          Run Demo Scenario
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
          : stats.map((stat) => {
              const Icon = stat.icon
              return (
                <Card key={stat.label}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-slate-400">{stat.label}</p>
                      <p className="text-3xl font-bold text-slate-100 mt-1">{stat.value.toLocaleString()}</p>
                    </div>
                    <Icon className={stat.color} size={24} />
                  </div>
                </Card>
              )
            })
        }
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card className="lg:col-span-1">
          <h3 className="text-sm font-medium text-slate-300 mb-4">Risk Distribution</h3>
          {isLoading ? (
            <CardSkeleton />
          ) : riskData.length > 0 ? (
            <div className="flex items-center gap-4">
              <ResponsiveContainer width={140} height={140}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={35}
                    outerRadius={60}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {riskData.map((entry) => (
                      <Cell key={entry.name} fill={riskColors[entry.name] || "#64748b"} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "#151b2e",
                      border: "1px solid #1c2440",
                      borderRadius: "8px",
                      color: "#e2e8f0",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2">
                {riskData.map((entry: any) => (
                  <div key={entry.name} className="flex items-center gap-2 text-xs">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: riskColors[entry.name] || "#64748b" }}
                    />
                    <span className="text-slate-400 capitalize">{entry.name}</span>
                    <span className="text-slate-200 font-medium">{entry.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-500">No risk data available</p>
          )}
        </Card>

        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-slate-300">Latest Alerts</h3>
            <Button variant="ghost" size="sm" onClick={() => router.push("/alerts")}>
              View All <ArrowRight size={14} className="ml-1" />
            </Button>
          </div>
          {isLoading ? (
            <TableSkeleton rows={4} />
          ) : summary?.latest_alerts?.length > 0 ? (
            <div className="space-y-2">
              {summary.latest_alerts.slice(0, 5).map((alert: any) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between bg-navy-700/50 rounded-lg px-4 py-3 cursor-pointer hover:bg-navy-700 transition-colors"
                  onClick={() => router.push(`/alerts`)}
                >
                  <div>
                    <p className="text-sm text-slate-200 font-medium">{alert.title || alert.event_type || alert.alert_type || "Alert"}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{alert.entity_id || alert.account_id}</p>
                  </div>
                  <Badge variant={alert.severity?.toLowerCase() || "medium"}>
                    {alert.severity || "UNKNOWN"}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No alerts detected</p>
          )}
        </Card>
      </div>

      <Card>
        <h3 className="text-sm font-medium text-slate-300 mb-4">High-Risk Network Clusters</h3>
        {isLoading ? (
          <TableSkeleton rows={3} />
        ) : (
          <p className="text-sm text-slate-500">Run analysis on a dataset to identify high-risk clusters</p>
        )}
      </Card>
    </AppShell>
  )
}
