"use client"

import { useState } from "react"
import Link from "next/link"
import {
  ArrowRight,
  Search,
  FileText,
  Lock,
  Eye,
  GitBranch,
  Activity,
  Check,
  ChevronDown,
  ArrowUpRight,
} from "lucide-react"
import { motion } from "motion/react"
import { TransactionTicker } from "@/components/landing/TransactionTicker"
import { Reveal } from "@/components/landing/Reveal"
import { SmoothScroll } from "@/components/landing/SmoothScroll"
import { ScrollProgress } from "@/components/landing/ScrollProgress"
import { NumberTicker } from "@/components/landing/NumberTicker"
import { StepTrail } from "@/components/landing/StepTrail"
import { TiltCard } from "@/components/landing/TiltCard"

const HERO_CONTAINER = {
  hidden: {},
  show: { transition: { staggerChildren: 0.09, delayChildren: 0.05 } },
}
const HERO_ITEM = {
  hidden: { opacity: 0, y: 22, filter: "blur(6px)" },
  show: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] as const } },
}

const NAV = [
  { label: "Platform", href: "#platform" },
  { label: "How it works", href: "#how" },
  { label: "Detection", href: "#detection" },
  { label: "Security", href: "#security" },
]

const DETECTORS = [
  "MULE NETWORKS",
  "LAYERING CHAINS",
  "CIRCULAR FLOWS",
  "STRUCTURING",
  "RAPID PASS-THROUGH",
  "VELOCITY SPIKES",
  "STATISTICAL ANOMALY",
  "COUNTERPARTY FAN-OUT",
]

const STATS: { num?: number; text?: string; suffix?: string; label: string }[] = [
  { num: 7, label: "detection engines, blended" },
  { text: "0–100", label: "explainable risk score" },
  { num: 100, suffix: "%", label: "alerts trace to evidence" },
  { num: 1, suffix: " click", label: "alert → investigation case" },
]

const FAQ = [
  {
    q: "How is the risk score explainable?",
    a: "Every score is a blend of seven detectors, and every alert links the exact transactions, reason codes, and graph evidence behind it. Investigators see why an account is suspicious, not just a number.",
  },
  {
    q: "What patterns does TrailGuard detect?",
    a: "Mule fan-in/fan-out funnels, multi-hop layering chains, circular flows, near-threshold structuring, rapid pass-through, velocity spikes, and statistical anomalies across the whole dataset.",
  },
  {
    q: "Is this using real bank data?",
    a: "No. TrailGuard runs on synthetic data for demonstration and research. Human review is always required before any action is taken on an alert.",
  },
  {
    q: "Can it run on our own infrastructure?",
    a: "Yes. The stack is a FastAPI backend with SQLite or PostgreSQL and a Next.js frontend — self-hostable end to end, no external calls required for detection.",
  },
]

export default function Landing() {
  return (
    <main className="grain bg-metal relative min-h-screen overflow-x-hidden font-display text-slate-700 antialiased">
      <SmoothScroll />
      <ScrollProgress />
      <Nav />
      <Hero />
      <Marquee />
      <Stats />
      <HowItWorks />
      <Features />
      <Security />
      <Faq />
      <Footer />
    </main>
  )
}

/* ───────────────────────── Nav ───────────────────────── */
function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-slate-900/10 bg-white/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <LogoMark />
          <span className="text-[15px] font-semibold tracking-tight text-slate-900">TrailGuard</span>
        </Link>
        <nav className="hidden items-center gap-8 md:flex">
          {NAV.map((n) => (
            <a key={n.label} href={n.href} className="text-sm text-slate-500 transition-colors hover:text-slate-900">
              {n.label}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Link href="/login" className="hidden text-sm font-medium text-slate-600 transition-colors hover:text-slate-900 sm:block">
            Sign in
          </Link>
          <Link
            href="/login"
            className="btn-metal-blue group inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-semibold text-white transition-all"
          >
            Get started
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      </div>
    </header>
  )
}

function LogoMark() {
  return (
    <span className="grid h-9 w-9 place-items-center rounded-lg bg-slate-900 shadow-sm">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/logo.svg" alt="TrailGuard" className="h-7 w-7" />
    </span>
  )
}

/* ───────────────────────── Hero ───────────────────────── */
function Hero() {
  return (
    <section className="relative isolate overflow-hidden px-6 pb-24 pt-32 lg:pt-40">
      {/* faint etched circuit traces, masked to fade out (no grid) */}
      <div className="absolute inset-0 -z-10 bg-traces [mask-image:radial-gradient(ellipse_75%_55%_at_50%_28%,#000_38%,transparent_82%)]" />

      {/* centered hero copy — staggered load reveal */}
      <motion.div
        variants={HERO_CONTAINER}
        initial="hidden"
        animate="show"
        className="mx-auto flex max-w-3xl flex-col items-center text-center"
      >
        <motion.div
          variants={HERO_ITEM}
          className="panel-flat mb-7 inline-flex items-center gap-2 rounded-full px-3 py-1.5"
        >
          <span className="h-1.5 w-1.5 animate-pulse-glow rounded-full bg-blue-500" />
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-slate-500">
            Explainable financial-crime intelligence
          </span>
        </motion.div>
        <motion.h1
          variants={HERO_ITEM}
          className="font-display text-5xl font-extrabold leading-[0.98] tracking-tight text-slate-900 sm:text-6xl lg:text-7xl"
        >
          Follow the money.
          <br />
          <span className="text-blue-600">Surface the truth.</span>
        </motion.h1>
        <motion.p variants={HERO_ITEM} className="mt-7 max-w-xl text-lg leading-relaxed text-slate-600">
          TrailGuard detects mule networks, traces money trails across accounts, and turns raw alerts
          into evidence-backed investigation cases — every score explained, every flow on the graph.
        </motion.p>
        <motion.div variants={HERO_ITEM} className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/login"
            className="btn-metal-blue group inline-flex items-center gap-2 rounded-full px-7 py-3.5 text-base font-bold text-white transition-all hover:-translate-y-0.5"
          >
            Get started
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <a
            href="#how"
            className="panel-flat inline-flex items-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold text-slate-700 transition-all hover:-translate-y-0.5"
          >
            See how it works
          </a>
        </motion.div>
        <motion.p variants={HERO_ITEM} className="mt-8 font-mono text-[11px] uppercase tracking-[0.15em] text-slate-400">
          Synthetic data · Human review always required
        </motion.p>
      </motion.div>

      {/* metallic hero device on a circuit board */}
      <HeroBoard />
    </section>
  )
}

/* a small metallic chip / module card (decorative) */
function ChipCard({ className = "", label }: { className?: string; label: string }) {
  return (
    <div className={`panel-raised rounded-2xl p-3 ${className}`}>
      <div className="screen-inset mb-3 flex h-8 items-center gap-1.5 rounded-md px-2">
        <span className="h-1.5 w-1.5 rounded-full bg-blue-400/80" />
        <span className="h-1 w-8 rounded-full bg-white/15" />
      </div>
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-slate-500">{label}</span>
        <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
      </div>
      <div className="mt-3 flex gap-1">
        {Array.from({ length: 7 }).map((_, i) => (
          <span key={i} className="h-1 w-2.5 rounded-sm bg-slate-300" />
        ))}
      </div>
    </div>
  )
}

function HeroBoard() {
  return (
    <div className="relative mx-auto mt-20 max-w-5xl">
      {/* circuit traces wiring the device to the chips (desktop) */}
      <svg
        className="pointer-events-none absolute inset-0 -z-0 hidden h-full w-full lg:block"
        viewBox="0 0 1000 560"
        fill="none"
        preserveAspectRatio="xMidYMid meet"
        aria-hidden
      >
        <g stroke="rgba(40,70,120,0.18)" strokeWidth="1.6">
          <path d="M250 150 H140 V300" />
          <path d="M250 250 H90" />
          <path d="M250 430 H150 V470" />
          <path d="M750 150 H880 V320" />
          <path d="M750 250 H920" />
          <path d="M750 420 H860 V300" />
        </g>
        {/* solder pads */}
        {[
          [140, 300], [90, 250], [150, 470], [880, 320], [920, 250], [860, 300],
        ].map(([x, y], i) => (
          <rect key={i} x={x - 3} y={y - 3} width="6" height="6" rx="1" fill="rgba(40,70,120,0.3)" />
        ))}
        {/* a couple of live blue nodes */}
        <rect x="247" y="247" width="6" height="6" rx="1" fill="#2563eb" />
        <rect x="747" y="247" width="6" height="6" rx="1" fill="#2563eb" />
      </svg>

      {/* flanking chip modules (wide screens) */}
      <ChipCard label="USER DATA" className="absolute -left-4 top-10 hidden w-44 xl:block" />
      <ChipCard label="DEPENDENCY DATA" className="absolute -left-10 bottom-8 hidden w-44 xl:block" />
      <ChipCard label="SYSTEM LOG" className="absolute -right-6 top-44 hidden w-44 xl:block" />

      {/* central device */}
      <div className="relative z-10 mx-auto max-w-2xl">
        <Reveal>
          <div className="panel-raised rounded-[1.7rem] p-3">
            <div className="flex items-center justify-between px-2.5 pb-2.5 pt-1">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500" />
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-slate-500">
                  TrailGuard · detection engine
                </span>
              </div>
              <div className="flex gap-1.5">
                {Array.from({ length: 4 }).map((_, i) => (
                  <span key={i} className="screw h-2 w-2 rounded-full" />
                ))}
              </div>
            </div>
            <TransactionTicker />
          </div>
        </Reveal>
      </div>
    </div>
  )
}

/* ───────────────────────── Marquee ───────────────────────── */
function Marquee() {
  const items = [...DETECTORS, ...DETECTORS]
  return (
    <section className="relative border-y border-slate-900/10 bg-white/45 py-5">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-[#e7ebef] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-[#e7ebef] to-transparent" />
      <div className="flex w-max animate-marquee items-center gap-10">
        {items.map((d, i) => (
          <div key={i} className="flex items-center gap-10">
            <span className="font-mono text-xs uppercase tracking-[0.2em] text-slate-500">{d}</span>
            <span className="h-1 w-1 rounded-full bg-blue-500/70" />
          </div>
        ))}
      </div>
    </section>
  )
}

/* ───────────────────────── Stats ───────────────────────── */
function Stats() {
  return (
    <section id="platform" className="mx-auto max-w-7xl px-6 py-24">
      <div className="grid grid-cols-2 gap-5 lg:grid-cols-4">
        {STATS.map((s, i) => (
          <Reveal key={i} delay={i * 80} className="panel-raised rounded-2xl p-8">
            <div className="font-display text-4xl font-bold text-slate-900 lg:text-5xl">
              {s.num !== undefined ? (
                <NumberTicker value={s.num} suffix={s.suffix} />
              ) : (
                s.text
              )}
            </div>
            <div className="mt-3 text-sm text-slate-500">{s.label}</div>
          </Reveal>
        ))}
      </div>
    </section>
  )
}

/* ───────────────────────── How it works ───────────────────────── */
const STEPS = [
  {
    n: "01",
    icon: Activity,
    title: "Ingest transactions",
    body: "Upload a transaction dataset. TrailGuard builds the full account graph and anchors every time window to the data's own clock.",
  },
  {
    n: "02",
    icon: Search,
    title: "Detect patterns",
    body: "Seven engines run across the whole dataset and graph — mule funnels, layering, cycles, structuring, velocity, anomaly — blended into one explainable score.",
  },
  {
    n: "03",
    icon: FileText,
    title: "Investigate & report",
    body: "Open a critical alert into a case, trace the money backward and forward on the graph, and export an evidence-backed report draft.",
  },
]

function HowItWorks() {
  return (
    <section id="how" className="relative mx-auto max-w-7xl px-6 py-24">
      <SectionLabel index="002" text="How it works" />
      <Reveal>
        <h2 className="mt-5 max-w-2xl font-display text-4xl font-bold tracking-tight text-slate-900 lg:text-5xl">
          From raw transactions to a courtroom-ready trail.
        </h2>
      </Reveal>
      <div className="mt-14 px-10">
        <StepTrail />
      </div>
      <div className="mt-6 grid gap-6 md:grid-cols-3">
        {STEPS.map((s, i) => (
          <Reveal key={s.n} delay={i * 100} className="panel-raised group relative rounded-2xl p-7">
            <div className="flex items-center justify-between">
              <span className="grid h-11 w-11 place-items-center rounded-xl border border-blue-600/20 bg-blue-600/10 text-blue-600">
                <s.icon className="h-5 w-5" />
              </span>
              <span className="font-mono text-sm text-slate-400">{s.n}</span>
            </div>
            <h3 className="mt-6 text-xl font-semibold text-slate-900">{s.title}</h3>
            <p className="mt-3 text-sm leading-relaxed text-slate-600">{s.body}</p>
            {i < STEPS.length - 1 && (
              <ArrowRight className="absolute -right-3 top-1/2 hidden h-5 w-5 -translate-y-1/2 text-slate-300 md:block" />
            )}
          </Reveal>
        ))}
      </div>
    </section>
  )
}

/* ───────────────────────── Features ───────────────────────── */
function Features() {
  return (
    <section id="detection" className="mx-auto max-w-7xl space-y-28 px-6 py-24">
      <FeatureRow
        label="Hybrid risk scoring"
        title="One score. Seven reasons."
        body="TrailGuard blends anomaly detection, fraud rules, graph intelligence, and transaction velocity into a single 0–100 score — and shows the reason codes and linked transactions behind every point."
        bullets={["Funnel-aware mule detection", "Dataset-wide isolation forest", "Reason codes on every alert"]}
        mockup={<AlertMockup />}
        flip={false}
      />
      <FeatureRow
        label="Money trail graph"
        title="Trace it backward to the source, forward to the cash-out."
        body="Every account is a node, every transfer an edge. Walk the trail upstream to victims and downstream to exit accounts, with mule funnels highlighted in red."
        bullets={["Source & destination tracing", "Mule money-trail mode", "Circular-flow detection"]}
        mockup={<GraphMockup />}
        flip={true}
      />
      <FeatureRow
        label="Investigation workspace"
        title="Turn an alert into evidence."
        body="Convert any critical alert into a case with one click. Add notes, build an evidence timeline, and generate a human-reviewable investigation report draft."
        bullets={["One-click case creation", "Evidence timeline", "Exportable report draft"]}
        mockup={<CaseMockup />}
        flip={false}
      />
    </section>
  )
}

function FeatureRow({
  label,
  title,
  body,
  bullets,
  mockup,
  flip,
}: {
  label: string
  title: string
  body: string
  bullets: string[]
  mockup: React.ReactNode
  flip: boolean
}) {
  return (
    <div className="grid items-center gap-12 lg:grid-cols-2">
      <Reveal className={flip ? "lg:order-2" : ""}>
        <span className="font-mono text-xs uppercase tracking-[0.2em] text-blue-600">{label}</span>
        <h3 className="mt-4 font-display text-3xl font-bold tracking-tight text-slate-900 lg:text-4xl">{title}</h3>
        <p className="mt-5 max-w-lg leading-relaxed text-slate-600">{body}</p>
        <ul className="mt-7 space-y-3">
          {bullets.map((b) => (
            <li key={b} className="flex items-center gap-3 text-sm text-slate-700">
              <span className="grid h-5 w-5 place-items-center rounded-full bg-blue-600/15 text-blue-600">
                <Check className="h-3 w-3" />
              </span>
              {b}
            </li>
          ))}
        </ul>
      </Reveal>
      <Reveal delay={120} className={flip ? "lg:order-1" : ""}>
        <TiltCard className="relative [transform-style:preserve-3d]">
          {mockup}
        </TiltCard>
      </Reveal>
    </div>
  )
}

/* framed product mockups (markup, not screenshots) */
function MockFrame({ children, title }: { children: React.ReactNode; title: string }) {
  return (
    <div className="panel-raised rounded-[1.4rem] p-2.5">
      {/* metal bezel header with mounting screws */}
      <div className="flex items-center justify-between px-2.5 pb-2.5 pt-1">
        <span className="font-mono text-[11px] tracking-wide text-slate-500">{title}</span>
        <div className="flex gap-1.5">
          {Array.from({ length: 3 }).map((_, i) => (
            <span key={i} className="screw h-2 w-2 rounded-full" />
          ))}
        </div>
      </div>
      {/* recessed dark screen */}
      <div className="screen-inset rounded-2xl p-5">{children}</div>
    </div>
  )
}

function AlertMockup() {
  const rows = [
    { id: "MULE-AX7", sev: "CRITICAL", score: 63, color: "text-red-400 bg-red-500/10 border-red-500/20" },
    { id: "CYCLE-A", sev: "CRITICAL", score: 66, color: "text-red-400 bg-red-500/10 border-red-500/20" },
    { id: "LAYER-D", sev: "HIGH", score: 59, color: "text-amber-400 bg-amber-500/10 border-amber-500/20" },
  ]
  return (
    <MockFrame title="trailguard / alerts">
      <div className="space-y-3">
        {rows.map((r) => (
          <div key={r.id} className="rounded-lg border border-white/[0.06] bg-white/[0.02] p-3.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm text-white">{r.id}</span>
                <span className={`rounded border px-1.5 py-0.5 font-mono text-[10px] ${r.color}`}>{r.sev}</span>
              </div>
              <span className="font-mono text-xs text-slate-400">{r.score}/100</span>
            </div>
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              {["INCOMING_DIVERSITY", "RAPID_FORWARDING", "MULTI_HOP_LAYERING"].map((c) => (
                <span key={c} className="rounded bg-white/[0.04] px-1.5 py-0.5 font-mono text-[9px] text-slate-400">
                  {c}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </MockFrame>
  )
}

function GraphMockup() {
  return (
    <MockFrame title="trailguard / money-trail">
      <div className="relative h-56 w-full overflow-hidden rounded-lg bg-ink-950 bg-dots">
        <svg className="absolute inset-0 h-full w-full" viewBox="0 0 360 220" fill="none">
          {[
            ["60,40", "180,110"],
            ["50,110", "180,110"],
            ["70,180", "180,110"],
            ["180,110", "300,60"],
            ["180,110", "300,160"],
          ].map(([a, b], i) => {
            const [x1, y1] = a.split(",")
            const [x2, y2] = b.split(",")
            return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(248,113,113,0.35)" strokeWidth="1.4" />
          })}
        </svg>
        {[
          { x: "12%", y: "16%", c: "bg-sky-400" },
          { x: "10%", y: "48%", c: "bg-sky-400" },
          { x: "16%", y: "80%", c: "bg-sky-400" },
          { x: "82%", y: "25%", c: "bg-sky-300" },
          { x: "82%", y: "72%", c: "bg-sky-300" },
        ].map((n, i) => (
          <span key={i} className={`absolute h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full ${n.c}`} style={{ left: n.x, top: n.y }} />
        ))}
        <span className="absolute left-1/2 top-1/2 grid h-8 w-8 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full bg-red-500/20 ring-2 ring-red-400/60">
          <span className="h-3 w-3 animate-pulse-glow rounded-full bg-red-400" />
        </span>
        <span className="absolute bottom-3 left-3 rounded bg-ink-900/80 px-2 py-1 font-mono text-[9px] text-slate-400">
          14 senders → 1 mule → 6 exits
        </span>
      </div>
    </MockFrame>
  )
}

function CaseMockup() {
  return (
    <MockFrame title="trailguard / case TG-9F2A">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-white">Case from alert: MULE-AX7</span>
          <span className="rounded bg-red-500/10 px-2 py-0.5 font-mono text-[10px] text-red-400">OPEN</span>
        </div>
        <div className="space-y-2.5 border-l border-white/[0.08] pl-4">
          {["Created from CRITICAL alert", "12 incoming senders linked", "88% forwarded in 16 min", "Connected to circular cluster"].map(
            (e, i) => (
              <div key={i} className="relative text-xs text-slate-400">
                <span className="absolute -left-[21px] top-1 h-1.5 w-1.5 rounded-full bg-sky-400" />
                {e}
              </div>
            )
          )}
        </div>
        <div className="rounded-lg border border-sky-400/20 bg-sky-400/[0.04] p-3">
          <div className="font-mono text-[10px] uppercase tracking-wider text-sky-400">Evidence report</div>
          <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
            Risk 63/100 — Critical. Fan-in funnel with rapid pass-through across 6 downstream accounts.
          </p>
        </div>
      </div>
    </MockFrame>
  )
}

/* ───────────────────────── Security ───────────────────────── */
const SEC = [
  { icon: Eye, title: "Explainable by default", body: "No black-box scores. Every alert carries reason codes, linked transactions, and graph evidence." },
  { icon: Lock, title: "Self-hostable", body: "FastAPI + SQLite/Postgres + Next.js. Detection runs entirely on your own infrastructure." },
  { icon: GitBranch, title: "Auditable trail", body: "Analysis runs, risk assessments, and case notes are all persisted for review and audit." },
]

function Security() {
  return (
    <section id="security" className="relative overflow-hidden border-y border-slate-900/10 bg-white/45 py-24">
      <div className="absolute inset-0 -z-10 bg-traces opacity-70 [mask-image:radial-gradient(ellipse_80%_70%_at_50%_50%,#000_30%,transparent_85%)]" />
      <div className="mx-auto max-w-7xl px-6">
        <SectionLabel index="003" text="Security-first" />
        <Reveal>
          <h2 className="mt-5 max-w-2xl font-display text-4xl font-bold tracking-tight text-slate-900 lg:text-5xl">
            Built for evidence, not just alerts.
          </h2>
        </Reveal>
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {SEC.map((s, i) => (
            <Reveal key={s.title} delay={i * 90} className="panel-raised rounded-2xl p-7">
              <span className="grid h-11 w-11 place-items-center rounded-xl border border-blue-600/20 bg-blue-600/10 text-blue-600">
                <s.icon className="h-5 w-5" />
              </span>
              <h3 className="mt-5 text-lg font-semibold text-slate-900">{s.title}</h3>
              <p className="mt-2.5 text-sm leading-relaxed text-slate-600">{s.body}</p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}

/* ───────────────────────── FAQ ───────────────────────── */
function Faq() {
  const [open, setOpen] = useState<number | null>(0)
  return (
    <section className="mx-auto max-w-3xl px-6 py-24">
      <SectionLabel index="004" text="FAQ" />
      <Reveal>
        <h2 className="mt-5 font-display text-4xl font-bold tracking-tight text-slate-900">Questions, answered.</h2>
      </Reveal>
      <div className="mt-12 divide-y divide-slate-900/10 border-y border-slate-900/10">
        {FAQ.map((f, i) => (
          <div key={i}>
            <button
              onClick={() => setOpen(open === i ? null : i)}
              className="flex w-full items-center justify-between gap-4 py-5 text-left"
            >
              <span className="text-base font-medium text-slate-900">{f.q}</span>
              <ChevronDown className={`h-5 w-5 shrink-0 text-slate-400 transition-transform ${open === i ? "rotate-180 text-blue-600" : ""}`} />
            </button>
            <div className={`grid transition-all duration-300 ${open === i ? "grid-rows-[1fr] pb-5" : "grid-rows-[0fr]"}`}>
              <div className="overflow-hidden">
                <p className="text-sm leading-relaxed text-slate-600">{f.a}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

/* ───────────────────────── Footer ───────────────────────── */
function Footer() {
  return (
    <footer className="border-t border-slate-900/10 bg-white/55">
      <div className="mx-auto max-w-7xl px-6 py-14">
        <div className="flex flex-col justify-between gap-10 md:flex-row">
          <div className="max-w-xs">
            <div className="flex items-center gap-2.5">
              <LogoMark />
              <span className="text-[15px] font-semibold text-slate-900">TrailGuard</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-slate-500">
              Explainable financial-crime investigation. Follow the money. Surface the truth.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-12 sm:grid-cols-3">
            <FooterCol title="Platform" links={["Detection", "Money trail", "Cases", "Reports"]} />
            <FooterCol title="Company" links={["About", "Security", "Privacy", "Terms"]} />
            <FooterCol title="Resources" links={["Docs", "Demo flow", "Changelog", "Contact"]} />
          </div>
        </div>
        <div className="mt-12 flex flex-col items-start justify-between gap-3 border-t border-slate-900/10 pt-6 sm:flex-row sm:items-center">
          <span className="font-mono text-[11px] text-slate-400">© 2026 TrailGuard · Synthetic demo · Human review required</span>
          <Link href="/login" className="group inline-flex items-center gap-1 text-xs text-slate-500 hover:text-blue-600">
            Open workspace <ArrowUpRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </Link>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({ title, links }: { title: string; links: string[] }) {
  return (
    <div>
      <div className="font-mono text-[11px] uppercase tracking-[0.15em] text-slate-500">{title}</div>
      <ul className="mt-4 space-y-2.5">
        {links.map((l) => (
          <li key={l}>
            <a href="#" className="text-sm text-slate-500 transition-colors hover:text-slate-900">
              {l}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}

/* ───────────────────────── shared ───────────────────────── */
function SectionLabel({ index, text }: { index: string; text: string }) {
  return (
    <Reveal className="flex items-center gap-3">
      <span className="font-mono text-xs text-blue-600">{index}</span>
      <span className="h-px w-8 bg-slate-900/20" />
      <span className="font-mono text-xs uppercase tracking-[0.2em] text-slate-500">{text}</span>
    </Reveal>
  )
}
