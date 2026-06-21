"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { Table } from "@/components/ui/Table"
import { FileUpload } from "@/components/ui/FileUpload"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { TableSkeleton } from "@/components/ui/Skeleton"
import { AppShell } from "@/components/layout/AppShell"
import { Database, Upload, Play, FileText, AlertCircle, CheckCircle } from "lucide-react"
import { toast } from "sonner"

export default function DatasetsPage() {
  const [uploading, setUploading] = useState(false)
  const queryClient = useQueryClient()

  const { data: datasets, isLoading, error, refetch } = useQuery({
    queryKey: ["datasets"],
    queryFn: () => api.datasets.list(),
  })

  const analyzeMutation = useMutation({
    mutationFn: (id: string) => api.datasets.analyze(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["datasets"] })
      toast.success("Dataset analysis complete")
    },
    onError: (err: any) => toast.error(err.message),
  })

  const handleUpload = async (file: File) => {
    setUploading(true)
    try {
      await api.datasets.upload(file)
      toast.success("Dataset uploaded successfully")
      queryClient.invalidateQueries({ queryKey: ["datasets"] })
    } catch (err: any) {
      toast.error(err.message || "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  if (error) {
    return (
      <AppShell>
        <ErrorState title="Failed to load datasets" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  const columns = [
    {
      key: "filename",
      header: "Filename",
      render: (item: any) => (
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-blue-600" />
          <span className="text-slate-800">{item.filename}</span>
        </div>
      ),
    },
    {
      key: "row_count",
      header: "Records",
      render: (item: any) => (
        <span className="text-slate-700">{(item.row_count ?? item.record_count ?? 0).toLocaleString()}</span>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (item: any) => {
        const variants: Record<string, "low" | "medium" | "high" | "critical" | "default"> = {
          completed: "low",
          processing: "medium",
          failed: "critical",
          uploaded: "default",
        }
        return <Badge variant={variants[item.status] || "default"}>{item.status}</Badge>
      },
    },
    {
      key: "created_at",
      header: "Uploaded",
      render: (item: any) => (
        <span className="text-slate-500 text-xs">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "-"}</span>
      ),
    },
    {
      key: "actions",
      header: "",
      render: (item: any) =>
        item.status === "completed" ? (
          <span className="flex items-center gap-1 text-xs text-green-400">
            <CheckCircle size={12} /> Analyzed
          </span>
        ) : item.status === "uploaded" ? (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => analyzeMutation.mutate(item.id)}
            disabled={analyzeMutation.isPending}
          >
            <Play size={12} className="mr-1" />
            Analyze
          </Button>
        ) : item.status === "processing" ? (
          <span className="text-xs text-amber-400">Processing...</span>
        ) : item.status === "failed" ? (
          <span className="text-xs text-red-400">Failed</span>
        ) : null,
    },
  ]

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Dataset Workspace</h1>
        <p className="text-sm text-slate-500 mt-1">Upload and analyze transaction datasets</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card className="lg:col-span-2">
          <h3 className="text-sm font-medium text-slate-700 mb-3">Upload Dataset</h3>
          <FileUpload onUpload={handleUpload} />
          {uploading && (
            <div className="mt-3 flex items-center gap-2 text-sm text-blue-600">
              <Upload size={16} className="animate-bounce" />
              Uploading and processing...
            </div>
          )}
        </Card>

        <Card>
          <h3 className="text-sm font-medium text-slate-700 mb-3">Supported Schemas</h3>
          <ul className="space-y-2 text-xs text-slate-500">
            <li className="flex items-center gap-2">
              <CheckCircle size={12} className="text-green-400" />
              Transaction ID (required)
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle size={12} className="text-green-400" />
              Source Account (required)
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle size={12} className="text-green-400" />
              Destination Account (required)
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle size={12} className="text-green-400" />
              Amount (required)
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle size={12} className="text-green-400" />
              Timestamp (required)
            </li>
            <li className="flex items-center gap-2">
              <AlertCircle size={12} className="text-amber-400" />
              Transaction Type (optional)
            </li>
          </ul>
        </Card>
      </div>

      <Card>
        <h3 className="text-sm font-medium text-slate-700 mb-4">Datasets</h3>
        {isLoading ? (
          <TableSkeleton />
        ) : datasets && datasets.length > 0 ? (
          <Table columns={columns} data={datasets} keyExtractor={(item: any) => item.id} />
        ) : (
          <EmptyState
            icon={<Database size={40} />}
            title="No datasets uploaded"
            description="Upload a CSV, JSON, or XLSX file to begin analysis"
          />
        )}
      </Card>
    </AppShell>
  )
}
