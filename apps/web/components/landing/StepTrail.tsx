"use client"

import { motion } from "motion/react"

/** A horizontal "follow the money" rail: the line draws itself left→right on
 *  view, 3 station dots light up, and a money dot travels the track on a loop. */
export function StepTrail() {
  return (
    <div className="relative hidden h-6 w-full md:block" aria-hidden>
      <svg className="h-6 w-full" viewBox="0 0 1000 24" preserveAspectRatio="none" fill="none">
        {/* base track */}
        <line x1="40" y1="12" x2="960" y2="12" stroke="rgba(20,32,55,0.14)" strokeWidth="2" />
        {/* drawing accent track */}
        <motion.line
          x1="40"
          y1="12"
          x2="960"
          y2="12"
          stroke="rgba(37,99,235,0.6)"
          strokeWidth="2"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true, margin: "0px 0px -15% 0px" }}
          transition={{ duration: 1.3, ease: [0.16, 1, 0.3, 1] }}
        />
        {/* station dots at 0 / 50 / 100% */}
        {[40, 500, 960].map((cx, i) => (
          <motion.circle
            key={cx}
            cx={cx}
            cy="12"
            r="5"
            fill="#2563eb"
            initial={{ scale: 0, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 + i * 0.45, type: "spring", stiffness: 300, damping: 18 }}
          />
        ))}
        {/* travelling money dot */}
        <motion.circle
          cy="12"
          r="3.5"
          fill="#60a5fa"
          initial={{ cx: 40 }}
          animate={{ cx: [40, 960] }}
          transition={{ duration: 2.6, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.6 }}
        />
      </svg>
    </div>
  )
}
