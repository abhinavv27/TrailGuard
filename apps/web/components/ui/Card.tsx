import { cn } from "@/lib/utils"

interface CardProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
}

export function Card({ children, className, onClick }: CardProps) {
  const Component = onClick ? "button" : "div"
  return (
    <Component
      className={cn("bg-white border border-slate-200 rounded-xl p-6 text-left shadow-[0_1px_2px_rgba(16,24,40,0.05),0_1px_0_rgba(255,255,255,0.7)_inset]", onClick && "cursor-pointer hover:border-slate-300 hover:shadow-[0_4px_14px_-6px_rgba(16,24,40,0.18)] transition-all", className)}
      onClick={onClick}
    >
      {children}
    </Component>
  )
}
