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
      className={cn("bg-navy-800 border border-navy-600 rounded-xl p-6 text-left", onClick && "cursor-pointer hover:border-navy-500 transition-colors", className)}
      onClick={onClick}
    >
      {children}
    </Component>
  )
}
