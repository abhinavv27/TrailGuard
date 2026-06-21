"use client"
import { useState } from "react"
import Link from "next/link"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Eye, EyeOff, ArrowLeft, ArrowRight } from "lucide-react"
import { OfficerPeek } from "@/components/landing/OfficerPeek"

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(4, "Password must be at least 4 characters"),
})
type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({ resolver: zodResolver(loginSchema) })

  const onSubmit = async (data: LoginForm) => {
    setError("")
    setLoading(true)
    try {
      const res = await fetch("http://localhost:8000/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: data.email, password: data.password }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Login failed" }))
        throw new Error(err.detail || "Login failed")
      }
      const resData = await res.json()
      sessionStorage.setItem("token", resData.access_token)
      window.location.href = "/dashboard"
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grain bg-metal relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-16 font-display text-slate-700">
      {/* faint etched circuit traces, masked — matches the landing vibe */}
      <div className="pointer-events-none absolute inset-0 bg-traces [mask-image:radial-gradient(ellipse_60%_55%_at_50%_45%,#000_35%,transparent_80%)]" />

      {/* back to home */}
      <Link
        href="/"
        className="absolute left-6 top-6 z-20 inline-flex items-center gap-1.5 text-xs text-slate-500 transition-colors hover:text-slate-900"
      >
        <ArrowLeft className="h-3.5 w-3.5" /> Home
      </Link>

      {/* centred auth card with the officer peeking from behind it */}
      <div className="relative w-full max-w-sm">
        {/* officer — sits behind the card (z-0), only his head peers over the top */}
        <div
          className="pointer-events-none absolute left-1/2 z-0 -translate-x-1/2"
          style={{ bottom: "calc(100% - 104px)" }}
        >
          <OfficerPeek />
        </div>

        {/* the card (opaque metal panel, hides his body) */}
        <div className="panel-raised relative z-10 rounded-2xl p-8">
          {/* brand */}
          <div className="mb-8 text-center">
            <Link href="/" className="inline-flex items-center gap-2">
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-slate-900">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src="/logo.svg" alt="" className="h-7 w-7" />
              </span>
              <span className="text-base font-semibold text-slate-900">TrailGuard</span>
            </Link>
            <h1 className="mt-5 font-display text-2xl font-bold tracking-tight text-slate-900">
              Log into your account
            </h1>
            <p className="mt-2 text-sm text-slate-500">
              New to TrailGuard?{" "}
              <Link href="/" className="font-medium text-blue-600 underline-offset-4 hover:underline">
                Request access
              </Link>
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2.5 text-sm text-red-600">
                {error}
              </div>
            )}

            <div>
              <label className="mb-1.5 block font-mono text-[11px] font-medium uppercase tracking-[0.12em] text-slate-500" htmlFor="email">
                Enter work email
              </label>
              <input
                id="email"
                type="email"
                {...register("email")}
                className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500/40"
                placeholder="analyst@trailguard.ai"
              />
              {errors.email && <p className="mt-1.5 text-xs text-red-600">{errors.email.message}</p>}
            </div>

            <div>
              <label className="mb-1.5 block font-mono text-[11px] font-medium uppercase tracking-[0.12em] text-slate-500" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  {...register("password")}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 pr-10 text-sm text-slate-900 placeholder-slate-400 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500/40"
                  placeholder="Enter password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 transition-colors hover:text-slate-600"
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-xs text-red-600">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-metal-blue group inline-flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold text-white transition-all disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Login"}
              {!loading && <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />}
            </button>
          </form>

          <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
            <div className="font-mono text-[10px] uppercase tracking-[0.15em] text-slate-500">Demo credentials</div>
            <div className="mt-1.5 font-mono text-xs text-slate-700">analyst@trailguard.ai · demo1234</div>
          </div>
        </div>
      </div>
    </div>
  )
}
