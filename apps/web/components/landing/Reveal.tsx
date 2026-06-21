"use client"

import { useEffect, useRef, type ReactNode } from "react"

/** Scroll-triggered reveal. Adds .is-visible when the element enters view. */
export function Reveal({
  children,
  className = "",
  delay = 0,
  as: Tag = "div",
}: {
  children: ReactNode
  className?: string
  delay?: number
  as?: any
}) {
  const ref = useRef<HTMLElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    // If the element is already in (or scrolled above) the viewport on mount,
    // reveal it immediately — avoids blank reserved space on load / reload-
    // while-scrolled, and IntersectionObserver never fires for content above
    // the current scroll position.
    if (el.getBoundingClientRect().top < window.innerHeight * 0.95) {
      el.classList.add("is-visible")
      return
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            el.classList.add("is-visible")
            io.unobserve(el)
          }
        })
      },
      // fire as soon as the element peeks in from the bottom, not 15% in
      { threshold: 0, rootMargin: "0px 0px -4% 0px" }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [])

  return (
    <Tag ref={ref as any} className={`reveal ${className}`} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </Tag>
  )
}
