"use client"

import { useAuth } from "@/hooks/useAuth"
import { LogOut, User } from "lucide-react"
import { Badge } from "@/components/ui/Badge"

export function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="h-14 bg-navy-800 border-b border-navy-600 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-400">Financial Crime Investigation Platform</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <User size={16} className="text-slate-400" />
          <span className="text-sm text-slate-200">{user?.display_name || "Analyst"}</span>
        </div>
        <Badge variant="default">{user?.role || "Analyst"}</Badge>
        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-red-400 transition-colors"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </header>
  )
}
