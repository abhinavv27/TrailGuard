import { cn } from "@/lib/utils"

interface CardProps {
  children: React.ReactNode
  className?: string
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn("bg-navy-800 border border-navy-600 rounded-xl p-6", className)}>
      {children}
    </div>
  )
}
