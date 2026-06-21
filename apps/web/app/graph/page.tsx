"use client"

import { useState, useCallback, useRef, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { api } from "@/lib/api"
import { Card } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { ErrorState } from "@/components/ui/ErrorState"
import { AppShell } from "@/components/layout/AppShell"
import {
  Share2,
  Target,
  Crosshair,
  ToggleLeft,
  ToggleRight,
  Info,
  Layers,
  Clock,
  X,
} from "lucide-react"
import { toast } from "sonner"
import dynamic from "next/dynamic"

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false })

interface GraphNode {
  id: string
  label?: string
  type?: string
  risk?: string
  value?: number
}

interface GraphLink {
  source: string
  target: string
  value?: number
  type?: string
  timestamp?: string
}

interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

function getNodeColor(node: GraphNode): string {
  if (node.risk === "critical") return "#dc2626"
  if (node.risk === "high") return "#ea580c"
  if (node.risk === "medium") return "#d97706"
  if (node.type === "account") return "#2563eb"
  if (node.type === "transaction") return "#60a5fa"
  return "#94a3b8"
}

function getLinkColor(link: GraphLink, muleMode: boolean): string {
  if (muleMode) {
    if (link.type === "suspicious") return "#dc2626"
    return "#dbe1e8" // Faded out
  }
  if (link.type === "suspicious") return "#ef4444"
  if (link.type === "high_value") return "#ea580c"
  return "#94a3b8"
}

export default function GraphPage() {
  const [exploreParams, setExploreParams] = useState<any>({ depth: 2, max_nodes: 50 })
  const [showLegend, setShowLegend] = useState(true)
  const [muleMode, setMuleMode] = useState(false)
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [timeWindow, setTimeWindow] = useState(90)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const graphRef = useRef<any>(null)

  const { data: graphData, isLoading, error, refetch } = useQuery<GraphData>({
    queryKey: ["graph-explore", exploreParams],
    queryFn: () => api.graph.explore(exploreParams),
  })

  const handleTraceSource = async (accountId?: string) => {
    const id = accountId || selectedNode?.id
    if (!id) { toast.error("Select an account first"); return }
    try {
      const data = await api.graph.traceSource({ account_id: id, depth: 3 })
      setExploreParams({ ...exploreParams, ...data })
      toast.success("Source trace complete")
    } catch { toast.error("Trace failed") }
  }

  const handleTraceDestination = async (accountId?: string) => {
    const id = accountId || selectedNode?.id
    if (!id) { toast.error("Select an account first"); return }
    try {
      const data = await api.graph.traceDestination({ account_id: id, depth: 3 })
      setExploreParams({ ...exploreParams, ...data })
      toast.success("Destination trace complete")
    } catch { toast.error("Trace failed") }
  }

  useEffect(() => {
    refetch()
  }, [exploreParams])

  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const updateSize = () => {
      const rect = el.getBoundingClientRect()
      setDimensions({ width: rect.width, height: rect.height })
    }
    updateSize()
    const observer = new ResizeObserver(updateSize)
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (graphRef.current && graphData?.nodes?.length) {
      graphRef.current.zoomToFit(400)
    }
  }, [graphData])

  if (error) {
    return (
      <AppShell>
        <ErrorState title="Failed to load graph" onRetry={() => refetch()} />
      </AppShell>
    )
  }

  return (
    <AppShell>
      <div className="flex h-[calc(100vh-7rem)] -mx-6 -mb-6">
        <div className="flex-1 relative bg-slate-100" ref={containerRef}>
          {isLoading ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-slate-500 flex flex-col items-center gap-2">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
                <span className="text-sm">Loading graph...</span>
              </div>
            </div>
          ) : graphData && graphData.nodes?.length > 0 ? (
            <div className="absolute inset-0">
              <ForceGraph2D
                ref={graphRef}
                graphData={{ 
                  nodes: JSON.parse(JSON.stringify(graphData.nodes)), 
                  links: JSON.parse(JSON.stringify(graphData.links)) 
                }}
                nodeColor={(node: any) => getNodeColor(node)}
                linkColor={(link: any) => getLinkColor(link, muleMode)}
                nodeLabel={(node: any) => node.label || node.id}
                linkLabel={(link: any) => `$${link.value?.toLocaleString() || ""}`}
                onNodeClick={(node: any) => setSelectedNode(node)}
                width={dimensions.width}
                height={dimensions.height}
                linkDirectionalParticles={2}
                linkDirectionalParticleSpeed={0.005}
                nodeRelSize={6}
                backgroundColor="#eef1f5"
              />
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center p-8">
                <Share2 size={48} className="text-slate-500 mx-auto mb-4" />
                <p className="text-slate-500 text-sm">No graph data available</p>
                <p className="text-xs text-slate-500 mt-1">Analyze datasets or inject demo data to populate the graph</p>
                <Button className="mt-4" size="sm" onClick={() => refetch()}>
                  Explore Graph
                </Button>
              </div>
            </div>
          )}

          <div className="absolute top-4 left-4 z-10 flex gap-2">
            <button
              onClick={() => setShowLegend(!showLegend)}
              className="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1.5"
            >
              <Layers size={14} />
              {showLegend ? "Hide" : "Show"} Legend
            </button>
            <button
              onClick={() => setMuleMode(!muleMode)}
              className={`rounded-lg px-3 py-1.5 text-xs flex items-center gap-1.5 border transition-colors ${
                muleMode
                  ? "bg-red-900/30 border-red-500/30 text-red-400"
                  : "bg-white border-slate-200 text-slate-500 hover:text-slate-800"
              }`}
            >
              {muleMode ? <ToggleRight size={14} /> : <ToggleLeft size={14} />}
              Mule Money Trail
            </button>
          </div>

          {showLegend && (
            <div className="absolute top-4 right-4 z-10 bg-white border border-slate-200 rounded-xl p-4 w-48">
              <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Legend</h4>
              <div className="space-y-2">
                {[
                  { color: "#2563eb", label: "Account" },
                  { color: "#60a5fa", label: "Transaction" },
                  { color: "#dc2626", label: "High Risk" },
                  { color: "#ea580c", label: "Medium Risk" },
                  { color: "#d97706", label: "Low Risk" },
                  { color: "#94a3b8", label: "Normal Flow" },
                  { color: "#ef4444", label: "Suspicious Flow" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2 text-xs">
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-slate-500">{item.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 bg-white border border-slate-200 rounded-lg px-4 py-2 flex items-center gap-3">
            <Clock size={14} className="text-slate-500" />
            <input
              type="range"
              min={1}
              max={365}
              value={timeWindow}
              onChange={(e) => setTimeWindow(Number(e.target.value))}
              className="w-32 accent-blue-600"
            />
            <span className="text-xs text-slate-500 w-16">{timeWindow} days</span>
          </div>
        </div>

        <aside className="w-72 bg-white border-l border-slate-200 p-4 overflow-y-auto flex-shrink-0">
          <h3 className="text-sm font-medium text-slate-700 mb-4">Graph Controls</h3>

          {selectedNode && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-medium text-slate-500 uppercase">Selected Account</h4>
                <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-slate-700">
                  <X size={14} />
                </button>
              </div>
              <div className="bg-slate-100 rounded-lg p-3 mb-3">
                <p className="text-sm font-medium text-slate-800">{selectedNode.label || selectedNode.id}</p>
                <p className="text-xs text-slate-500">{selectedNode.id}</p>
                {selectedNode.risk && <Badge variant={selectedNode.risk.toLowerCase()} className="mt-2">{selectedNode.risk}</Badge>}
                {selectedNode.value && (
                  <p className="text-xs text-slate-500 mt-1">
                    Volume: ${Number(selectedNode.value).toLocaleString()}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Button size="sm" variant="secondary" className="w-full" onClick={() => handleTraceSource(selectedNode.id)}>
                  <Target size={14} className="mr-1.5" /> Trace Source
                </Button>
                <Button size="sm" variant="secondary" className="w-full" onClick={() => handleTraceDestination(selectedNode.id)}>
                  <Crosshair size={14} className="mr-1.5" /> Trace Destination
                </Button>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="label">Max Nodes</label>
              <input
                type="number"
                value={exploreParams.max_nodes || 50}
                onChange={(e) => setExploreParams({ ...exploreParams, max_nodes: Number(e.target.value) })}
                className="input w-full"
                min={10}
                max={200}
              />
            </div>
            <div>
              <label className="label">Trace Depth</label>
              <input
                type="number"
                value={exploreParams.depth || 2}
                onChange={(e) => setExploreParams({ ...exploreParams, depth: Number(e.target.value) })}
                className="input w-full"
                min={1}
                max={6}
              />
            </div>
            <Button className="w-full" onClick={() => refetch()}>
              <Share2 size={16} className="mr-1.5" /> Update Graph
            </Button>
          </div>

          {graphData && graphData.nodes?.length > 0 && (
            <div className="mt-6 pt-4 border-t border-slate-200">
              <h4 className="text-xs font-medium text-slate-500 uppercase mb-2">Stats</h4>
              <div className="space-y-1 text-xs text-slate-500">
                <p>Nodes: {graphData.nodes.length}</p>
                <p>Edges: {graphData.links.length}</p>
                <p>Suspicious flows: {graphData.links.filter((l: any) => l.type === "suspicious").length}</p>
              </div>
            </div>
          )}
        </aside>
      </div>
    </AppShell>
  )
}
