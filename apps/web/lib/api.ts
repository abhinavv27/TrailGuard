const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== 'undefined' ? sessionStorage.getItem('token') : null
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
    ...options,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || 'API Error')
  }
  return res.json()
}

async function unwrapItems<T>(response: any): Promise<T[]> {
  return response.items || response || []
}

export const api = {
  auth: {
    login: (data: { email: string; password: string }) =>
      fetchAPI<{ access_token: string; token_type: string }>('/api/v1/auth/login', {
        method: 'POST', body: JSON.stringify(data),
      }),
    me: () => fetchAPI<{ id: string; email: string; display_name: string; role: string }>('/api/v1/auth/me'),
  },
  dashboard: {
    summary: () => fetchAPI<any>('/api/v1/dashboard/summary'),
  },
  datasets: {
    upload: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const token = sessionStorage.getItem('token')
      return fetch(`${API_BASE}/api/v1/datasets/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      }).then(r => r.json())
    },
    list: async () => {
      const res = await fetchAPI<any>('/api/v1/datasets')
      return unwrapItems<any>(res)
    },
    get: (id: string) => fetchAPI<any>(`/api/v1/datasets/${id}`),
    analyze: (id: string) => fetchAPI<any>(`/api/v1/datasets/${id}/analyze`, { method: 'POST' }),
  },
  alerts: {
    list: async (params?: string) => {
      const res = await fetchAPI<any>(`/api/v1/alerts?${params || ''}`)
      return unwrapItems<any>(res)
    },
    get: (id: string) => fetchAPI<any>(`/api/v1/alerts/${id}`),
    createCase: (id: string) => fetchAPI<any>(`/api/v1/alerts/${id}/create-case`, { method: 'POST' }),
  },
  accounts: {
    get: (id: string) => fetchAPI<any>(`/api/v1/accounts/${id}`),
    transactions: async (id: string) => {
      const res = await fetchAPI<any>(`/api/v1/accounts/${id}/transactions`)
      return res.transactions || res || []
    },
    risk: (id: string) => fetchAPI<any>(`/api/v1/accounts/${id}/risk`),
    graph: (id: string) => fetchAPI<any>(`/api/v1/accounts/${id}/graph`),
  },
  graph: {
    explore: (params: any) => fetchAPI<any>('/api/v1/graph/explore', { method: 'POST', body: JSON.stringify(params) }),
    traceSource: (data: any) => fetchAPI<any>('/api/v1/graph/trace-source', { method: 'POST', body: JSON.stringify(data) }),
    traceDestination: (data: any) => fetchAPI<any>('/api/v1/graph/trace-destination', { method: 'POST', body: JSON.stringify(data) }),
  },
  cases: {
    list: async () => {
      const res = await fetchAPI<any>('/api/v1/cases')
      return unwrapItems<any>(res)
    },
    create: (data: any) => fetchAPI<any>('/api/v1/cases', { method: 'POST', body: JSON.stringify(data) }),
    get: (id: string) => fetchAPI<any>(`/api/v1/cases/${id}`),
    update: (id: string, data: any) => fetchAPI<any>(`/api/v1/cases/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    addNote: (id: string, content: string) => fetchAPI<any>(`/api/v1/cases/${id}/notes`, { method: 'POST', body: JSON.stringify({ content }) }),
    generateReport: (id: string) => fetchAPI<any>(`/api/v1/cases/${id}/generate-report`, { method: 'POST' }),
    getReport: (id: string) => fetchAPI<any>(`/api/v1/cases/${id}/report`),
  },
  demo: {
    injectScenario: (data: any) => fetchAPI<any>('/api/v1/demo/inject-scenario', { method: 'POST', body: JSON.stringify(data) }),
  },
}
