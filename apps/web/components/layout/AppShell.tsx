"use client"

import { Sidebar } from "./Sidebar"
import { Navbar } from "./Navbar"
import { AuthProvider } from "@/hooks/useAuth"

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className="grain bg-metal flex h-screen text-slate-700">
        <Sidebar />
        <div className="ml-60 flex flex-1 flex-col">
          <Navbar />
          <main className="relative flex-1 overflow-y-auto p-6">
            <div className="relative">{children}</div>
          </main>
        </div>
      </div>
    </AuthProvider>
  )
}
