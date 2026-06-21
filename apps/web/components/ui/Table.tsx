import { cn } from "@/lib/utils"

interface Column<T> {
  key: string
  header: string
  render?: (item: T) => React.ReactNode
  className?: string
}

interface TableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (item: T) => string
  onRowClick?: (item: T) => void
  className?: string
}

export function Table<T>({ columns, data, keyExtractor, onRowClick, className }: TableProps<T>) {
  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200">
            {columns.map((col) => (
              <th key={col.key} className={cn("text-left text-slate-500 font-medium py-3 px-4", col.className)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr
              key={keyExtractor(item)}
              onClick={() => onRowClick?.(item)}
              className={cn(
                "border-b border-slate-100 hover:bg-slate-50 transition-colors",
                onRowClick && "cursor-pointer"
              )}
            >
              {columns.map((col) => (
                <td key={col.key} className={cn("py-3 px-4", col.className)}>
                  {col.render ? col.render(item) : (item as any)[col.key] ?? "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
