"use client"

import { useEffect, useRef } from "react"
import { useInView, useMotionValue, useSpring } from "motion/react"

/** Count-up number that animates from 0 → value when scrolled into view. */
export function NumberTicker({
  value,
  suffix = "",
  className = "",
}: {
  value: number
  suffix?: string
  className?: string
}) {
  const ref = useRef<HTMLSpanElement>(null)
  const out = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref, { once: true, margin: "0px 0px -12% 0px" })
  const mv = useMotionValue(0)
  const spring = useSpring(mv, { damping: 28, stiffness: 90 })

  useEffect(() => {
    if (inView) mv.set(value)
  }, [inView, value, mv])

  useEffect(() => {
    return spring.on("change", (v) => {
      if (out.current) out.current.textContent = Math.round(v).toLocaleString()
    })
  }, [spring])

  return (
    <span ref={ref} className={className}>
      <span ref={out}>0</span>
      {suffix && <span className="text-sky-400">{suffix}</span>}
    </span>
  )
}
