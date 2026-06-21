import { cn } from "@/lib/utils"

interface BadgeProps {
  children: React.ReactNode
  variant?: "low" | "medium" | "high" | "critical" | "default"
  className?: string
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  const variants = {
    low: "bg-green-100 text-green-700 border border-green-200",
    medium: "bg-amber-100 text-amber-700 border border-amber-200",
    high: "bg-orange-100 text-orange-700 border border-orange-200",
    critical: "bg-red-100 text-red-700 border border-red-200",
    default: "bg-slate-100 text-slate-600 border border-slate-200",
  }

  return (
    <span className={cn("px-2 py-0.5 rounded text-xs font-medium", variants[variant], className)}>
      {children}
    </span>
  )
}
