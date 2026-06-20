"use client"

import { Sidebar } from "./Sidebar"
import { Navbar } from "./Navbar"
import { AuthProvider } from "@/hooks/useAuth"

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 ml-60 flex flex-col">
          <Navbar />
          <main className="flex-1 overflow-y-auto p-6">
            {children}
          </main>
        </div>
      </div>
    </AuthProvider>
  )
}
