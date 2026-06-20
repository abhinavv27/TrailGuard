"use client"

import { useState } from "react"
import { Eye, EyeOff } from "lucide-react"
import { AppShell } from "@/components/layout/AppShell"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const res = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Login failed" }))
        throw new Error(err.detail || "Login failed")
      }
      const data = await res.json()
      sessionStorage.setItem("token", data.access_token)
      window.location.href = "/dashboard"
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-navy-900 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <img src="/logo.svg" alt="TrailGuard AI" className="w-12 h-12 mx-auto mb-3" />
          <h1 className="text-2xl font-bold text-slate-100">TrailGuard AI</h1>
          <p className="text-sm text-slate-500 mt-1">Financial Crime Investigation Platform</p>
          <span className="inline-block mt-3 bg-amber-500/10 text-amber-400 text-[10px] font-semibold px-2 py-1 rounded border border-amber-500/20 uppercase tracking-wider">
            Synthetic Demo Environment
          </span>
        </div>

        <form onSubmit={handleSubmit} className="bg-navy-800 border border-navy-600 rounded-xl p-6 space-y-4">
          {error && (
            <div className="bg-red-900/30 border border-red-500/30 text-red-400 text-sm rounded-lg px-4 py-2">
              {error}
            </div>
          )}

          <div>
            <label className="label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input w-full"
              placeholder="analyst@trailguard.ai"
              required
            />
          </div>

          <div>
            <label className="label" htmlFor="password">Password</label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input w-full pr-10"
                placeholder="Enter password"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <p className="text-xs text-slate-500 text-center mt-4">
            Demo credentials: analyst@trailguard.ai / demo1234
          </p>
        </form>
      </div>
    </div>
  )
}
