import type { Metadata } from "next"
import { Inter, Sora, JetBrains_Mono } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"

const inter = Inter({ subsets: ["latin"], variable: "--font-body" })
const sora = Sora({ subsets: ["latin"], variable: "--font-display", weight: ["400", "500", "600", "700", "800"] })
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", weight: ["400", "500", "600"] })

export const metadata: Metadata = {
  title: "TrailGuard — Explainable Financial Crime Intelligence",
  description: "Follow the money. Surface the truth. TrailGuard detects mule networks, traces money trails, and turns alerts into evidence-backed cases.",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${sora.variable} ${jetbrains.variable} ${inter.className} bg-slate-100 text-slate-700`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
