"use client"

import { ArrowRight, AlertTriangle } from "lucide-react"

/**
 * Live transaction tape. A vertical stream of transfers scrolling upward;
 * flagged rows flare red. Pure CSS animation (duplicated rows for a seamless
 * loop), respects prefers-reduced-motion. Decorative — a monitoring-terminal
 * feel for the hero.
 */

type Tx = { t: string; from: string; to: string; amt: string; flag: boolean }

const FEED: Tx[] = [
  { t: "09:14:02", from: "ACC-201", to: "ACC-088", amt: "4,120", flag: false },
  { t: "09:14:08", from: "VICTIM-03", to: "MULE-AX7", amt: "9,800", flag: true },
  { t: "09:14:15", from: "ACC-044", to: "ACC-119", amt: "60", flag: false },
  { t: "09:14:21", from: "VICTIM-07", to: "MULE-AX7", amt: "8,950", flag: true },
  { t: "09:14:33", from: "ACC-077", to: "ACC-005", amt: "1,540", flag: false },
  { t: "09:14:40", from: "MULE-AX7", to: "EXIT-02", amt: "9,200", flag: true },
  { t: "09:14:52", from: "ACC-160", to: "ACC-012", amt: "320", flag: false },
  { t: "09:15:01", from: "LAYER-A", to: "LAYER-B", amt: "19,577", flag: true },
  { t: "09:15:09", from: "ACC-033", to: "ACC-201", amt: "880", flag: false },
  { t: "09:15:18", from: "LAYER-B", to: "LAYER-C", amt: "16,162", flag: true },
  { t: "09:15:26", from: "ACC-118", to: "ACC-090", amt: "240", flag: false },
  { t: "09:15:35", from: "CYCLE-A", to: "CYCLE-B", amt: "10,864", flag: true },
  { t: "09:15:44", from: "ACC-052", to: "ACC-147", amt: "2,300", flag: false },
  { t: "09:15:52", from: "STRUCT-01", to: "STRUCT-RX", amt: "9,900", flag: true },
  { t: "09:16:03", from: "ACC-014", to: "ACC-200", amt: "510", flag: false },
  { t: "09:16:11", from: "VICTIM-11", to: "MULE-AX7", amt: "7,400", flag: true },
]

function Row({ tx }: { tx: Tx }) {
  return (
    <div
      className={`flex items-center gap-3 border-b border-white/[0.05] px-4 py-3 font-mono text-[12px] ${
        tx.flag ? "bg-red-500/[0.06]" : ""
      }`}
    >
      <span className="w-16 shrink-0 text-slate-600">{tx.t}</span>
      <span className={`w-20 shrink-0 truncate ${tx.flag ? "text-red-300" : "text-slate-300"}`}>{tx.from}</span>
      <ArrowRight className={`h-3 w-3 shrink-0 ${tx.flag ? "text-red-400/70" : "text-slate-600"}`} />
      <span className={`w-20 shrink-0 truncate ${tx.flag ? "text-red-300" : "text-slate-300"}`}>{tx.to}</span>
      <span className={`ml-auto shrink-0 tabular-nums ${tx.flag ? "text-red-300" : "text-slate-400"}`}>${tx.amt}</span>
      <span className="w-5 shrink-0">
        {tx.flag && <AlertTriangle className="h-3.5 w-3.5 text-red-400" />}
      </span>
    </div>
  )
}

export function TransactionTicker() {
  const rows = [...FEED, ...FEED]
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-ink-900/80 shadow-2xl shadow-black/50 backdrop-blur">
      {/* header */}
      <div className="flex items-center justify-between border-b border-white/[0.07] bg-white/[0.02] px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 animate-pulse-glow rounded-full bg-sky-400" />
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-slate-400">Live transaction feed</span>
        </div>
        <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-slate-600">stream · synthetic</span>
      </div>

      {/* scrolling tape */}
      <div className="relative h-[440px] lg:h-[520px]">
        <div className="animate-ticker will-change-transform motion-reduce:animate-none">
          {rows.map((tx, i) => (
            <Row key={i} tx={tx} />
          ))}
        </div>
        {/* top & bottom fade masks */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-ink-900 to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-ink-900 to-transparent" />
      </div>

      {/* footer legend */}
      <div className="flex items-center gap-4 border-t border-white/[0.07] bg-white/[0.02] px-4 py-2.5 font-mono text-[10px] text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-slate-500" /> normal
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-red-400" /> flagged
        </span>
        <span className="ml-auto text-slate-600">7 detectors live</span>
      </div>
    </div>
  )
}
