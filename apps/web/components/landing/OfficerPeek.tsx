"use client"

import { useEffect } from "react"
import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  useReducedMotion,
} from "motion/react"

/**
 * Peek-a-boo security officer. An upper-body vector figure meant to sit
 * BEHIND a centred auth card: only his head peers over the top edge. He
 * pops up to peek, ducks back down on a loop, blinks, and tilts in 3D to
 * follow the cursor — as if checking who's trying to log in.
 * Reduced-motion safe (stays peeking, still).
 */

const NAVY = "#20406e"
const NAVY_D = "#162d4f"
const SKIN = "#f4c9a6"
const SKIN_D = "#e3b48f"
const HAIR = "#3a2a1c"
const TIE = "#2e74b5"
const TIE_D = "#225c93"
const STROKE = "#2a2a2a"
const MASK = "#d2e7f8"
const MASK_D = "#a9cbe6"

export function OfficerPeek() {
  const reduced = useReducedMotion()

  // cursor-driven 3D "looking" tilt (tracks the whole viewport)
  const px = useMotionValue(0)
  const py = useMotionValue(0)
  const sx = useSpring(px, { stiffness: 80, damping: 15 })
  const sy = useSpring(py, { stiffness: 80, damping: 15 })
  const rotateY = useTransform(sx, [-0.5, 0.5], [-20, 20])
  const rotateX = useTransform(sy, [-0.5, 0.5], [14, -10])

  useEffect(() => {
    if (reduced) return
    const onMove = (e: MouseEvent) => {
      px.set(e.clientX / window.innerWidth - 0.5)
      py.set(e.clientY / window.innerHeight - 0.5)
    }
    window.addEventListener("mousemove", onMove)
    return () => window.removeEventListener("mousemove", onMove)
  }, [reduced, px, py])

  return (
    <motion.div
      style={{ rotateX, rotateY, transformPerspective: 1000, transformStyle: "preserve-3d" }}
      className="origin-bottom"
    >
      {/* peek-a-boo loop: rise → hold → duck behind card → pop back */}
      <motion.div
        animate={reduced ? undefined : { y: [0, 0, 46, 46, 0, 0], rotate: [-2, 2, 1, -1, -2, -2] }}
        transition={{
          duration: 7,
          times: [0, 0.42, 0.54, 0.66, 0.8, 1],
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="origin-bottom"
      >
        <svg width={260} height={250} viewBox="0 0 260 250" className="h-auto w-[230px] overflow-visible">
          {/* ── shoulders / shirt (mostly hidden behind the card) ── */}
          <path d="M76 198 Q130 168 184 198 L192 250 L68 250 Z" fill="#fff" stroke={STROKE} strokeWidth={2.5} />
          <path d="M130 198 L104 180 L130 178 Z" fill="#fff" stroke={NAVY} strokeWidth={3} />
          <path d="M130 198 L156 180 L130 178 Z" fill="#fff" stroke={NAVY} strokeWidth={3} />
          <rect x={70} y={190} width={26} height={11} rx={4} transform="rotate(-12 83 195)" fill={NAVY} />
          <rect x={164} y={190} width={26} height={11} rx={4} transform="rotate(12 177 195)" fill={NAVY} />
          <path d="M122 196 L130 208 L138 196 L130 190 Z" fill={TIE} stroke={TIE_D} strokeWidth={1.5} />

          {/* ── neck ── */}
          <rect x={117} y={150} width={26} height={26} fill={SKIN} stroke={SKIN_D} strokeWidth={1.5} />

          {/* ── hair tufts (behind face) ── */}
          <ellipse cx={90} cy={84} rx={13} ry={20} fill={HAIR} />
          <ellipse cx={170} cy={84} rx={13} ry={20} fill={HAIR} />

          {/* ── face ── */}
          <ellipse cx={130} cy={98} rx={42} ry={48} fill={SKIN} stroke={SKIN_D} strokeWidth={1.5} />
          <ellipse cx={87} cy={104} rx={8} ry={12} fill={SKIN} stroke={SKIN_D} strokeWidth={1.5} />
          <ellipse cx={173} cy={104} rx={8} ry={12} fill={SKIN} stroke={SKIN_D} strokeWidth={1.5} />

          {/* ── eyebrows ── */}
          <path d="M104 84 Q114 79 124 84" stroke={HAIR} strokeWidth={3.5} fill="none" strokeLinecap="round" />
          <path d="M136 84 Q146 79 156 84" stroke={HAIR} strokeWidth={3.5} fill="none" strokeLinecap="round" />

          {/* ── eyes (blink) ── */}
          <motion.g
            style={{ transformBox: "fill-box", transformOrigin: "center" }}
            animate={reduced ? undefined : { scaleY: [1, 1, 0.1, 1, 1] }}
            transition={{ duration: 3.6, times: [0, 0.9, 0.94, 0.98, 1], repeat: Infinity, ease: "easeInOut" }}
          >
            <ellipse cx={114} cy={98} rx={8} ry={10} fill="#fff" stroke={SKIN_D} strokeWidth={1} />
            <ellipse cx={146} cy={98} rx={8} ry={10} fill="#fff" stroke={SKIN_D} strokeWidth={1} />
            <circle cx={115} cy={99} r={4.2} fill="#5b3a1e" />
            <circle cx={147} cy={99} r={4.2} fill="#5b3a1e" />
            <circle cx={116.5} cy={97} r={1.3} fill="#fff" />
            <circle cx={148.5} cy={97} r={1.3} fill="#fff" />
          </motion.g>

          {/* ── mask ── */}
          <path d="M100 110 Q130 104 160 110 L156 134 Q130 154 104 134 Z" fill={MASK} stroke={MASK_D} strokeWidth={2} />
          <path d="M106 120 H154 M107 128 H153" stroke={MASK_D} strokeWidth={1.3} fill="none" />
          <path d="M100 112 Q88 110 85 104" stroke={MASK_D} strokeWidth={2} fill="none" />
          <path d="M160 112 Q172 110 175 104" stroke={MASK_D} strokeWidth={2} fill="none" />

          {/* ── cap ── */}
          <path d="M76 62 Q82 16 130 12 Q178 16 184 62 Z" fill={NAVY} stroke={NAVY_D} strokeWidth={2} />
          <rect x={84} y={46} width={92} height={9} rx={2} fill={NAVY_D} />
          <ellipse cx={130} cy={66} rx={60} ry={11} fill="#111" />
          <circle cx={130} cy={36} r={6} fill="#d6a93b" stroke="#9c7820" strokeWidth={1.5} />
        </svg>
      </motion.div>
    </motion.div>
  )
}
