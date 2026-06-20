import { describe, it, expect } from "vitest"

describe("App smoke test", () => {
  it("should have the correct project name in package.json", async () => {
    const pkg = await import("../package.json")
    expect(pkg.name).toBe("trailguard-web")
  })

  it("should export cn utility correctly", async () => {
    const { cn } = await import("../lib/utils")
    expect(cn("a", "b")).toBe("a b")
    expect(cn("a", false && "b", "c")).toBe("a c")
  })

  it("should have required API client endpoints", async () => {
    const { api } = await import("../lib/api")
    expect(api.auth).toBeDefined()
    expect(api.auth.login).toBeDefined()
    expect(api.dashboard).toBeDefined()
    expect(api.dashboard.summary).toBeDefined()
    expect(api.datasets).toBeDefined()
    expect(api.datasets.list).toBeDefined()
    expect(api.datasets.upload).toBeDefined()
    expect(api.alerts).toBeDefined()
    expect(api.alerts.list).toBeDefined()
    expect(api.accounts).toBeDefined()
    expect(api.accounts.get).toBeDefined()
    expect(api.graph).toBeDefined()
    expect(api.graph.explore).toBeDefined()
    expect(api.cases).toBeDefined()
    expect(api.cases.list).toBeDefined()
    expect(api.demo).toBeDefined()
  })
})
