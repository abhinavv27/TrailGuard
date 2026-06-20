import { cn } from "@/lib/utils"

interface BadgeProps {
  children: React.ReactNode
  variant?: "low" | "medium" | "high" | "critical" | "default"
  className?: string
}

export function Badge({ children, variant = "default", className }: BadgeProps) {
  const variants = {
    low: "bg-green-900/50 text-green-400",
    medium: "bg-amber-900/50 text-amber-400",
    high: "bg-orange-900/50 text-orange-400",
    critical: "bg-red-900/50 text-red-400",
    default: "bg-navy-600 text-slate-300",
  }

  return (
    <span className={cn("px-2 py-0.5 rounded text-xs font-medium", variants[variant], className)}>
      {children}
    </span>
  )
}
