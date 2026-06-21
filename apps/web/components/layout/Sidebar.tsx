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
    <aside className="w-60 bg-white border-r border-slate-200 flex flex-col h-screen fixed left-0 top-0">
      <div className="p-5 border-b border-slate-200">
        <Link href="/dashboard" className="flex items-center gap-3">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-slate-900">
            <img src="/logo.svg" alt="TrailGuard AI" className="w-6 h-6" />
          </span>
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">TrailGuard</h1>
            <p className="text-[10px] text-blue-600 font-semibold tracking-wider uppercase">AI</p>
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
                  ? "bg-blue-50 text-blue-700 border border-blue-200"
                  : "text-slate-500 hover:text-slate-900 hover:bg-slate-100"
              )}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-slate-200">
        <span className="inline-block bg-amber-100 text-amber-700 text-[10px] font-semibold px-2 py-1 rounded border border-amber-200 uppercase tracking-wider">
          Synthetic Demo Environment
        </span>
      </div>
    </aside>
  )
}
