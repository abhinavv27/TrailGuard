"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Database,
  Bell,
  Share2,
  Briefcase,
  FileText,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/datasets", label: "Datasets", icon: Database },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/graph", label: "Graph", icon: Share2 },
  { href: "/cases", label: "Cases", icon: Briefcase },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-60 bg-navy-800 border-r border-navy-600 flex flex-col h-screen fixed left-0 top-0">
      <div className="p-5 border-b border-navy-600">
        <Link href="/dashboard" className="flex items-center gap-3">
          <img src="/logo.svg" alt="TrailGuard AI" className="w-8 h-8" />
          <div>
            <h1 className="text-lg font-bold text-slate-100 leading-tight">TrailGuard</h1>
            <p className="text-[10px] text-cyan-400 font-medium tracking-wider uppercase">AI</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href)
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-cyan-600/10 text-cyan-400 border border-cyan-600/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-navy-700"
              )}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-navy-600">
        <span className="inline-block bg-amber-500/10 text-amber-400 text-[10px] font-semibold px-2 py-1 rounded border border-amber-500/20 uppercase tracking-wider">
          Synthetic Demo Environment
        </span>
      </div>
    </aside>
  )
}
