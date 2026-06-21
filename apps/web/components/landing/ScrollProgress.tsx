"use client"

import { motion, useScroll, useSpring } from "motion/react"

/** Thin sky progress bar pinned to the top, tracking page scroll. */
export function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, { stiffness: 120, damping: 30, mass: 0.3 })
  return (
    <motion.div
      style={{ scaleX }}
      className="fixed inset-x-0 top-0 z-[70] h-0.5 origin-left bg-sky-400"
      aria-hidden
    />
  )
}
