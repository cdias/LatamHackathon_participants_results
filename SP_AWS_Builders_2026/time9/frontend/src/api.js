// Cliente de API. O JWT fica em memória (não em localStorage) para reduzir risco de XSS.
const API_BASE = import.meta.env.VITE_API_BASE || ''

let _token = null
export function setToken(t) { _token = t }
export function getToken() { return _token }

async function req(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (_token) headers['Authorization'] = `Bearer ${_token}`
  const res = await fetch(`${API_BASE}${path}`, {
    method, headers, body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}))
    throw new Error(detail.detail || `Erro ${res.status}`)
  }
  return res.json()
}

export const api = {
  login: (username, password) => req('/api/auth/login', { method: 'POST', body: { username, password } }),
  me: () => req('/api/me'),
  recommendations: () => req('/api/recommendations'),
  targets: (flightId) => req(`/api/flights/${flightId}/targets`),
  generateCopy: (payload) => req('/api/campaigns/generate-copy', { method: 'POST', body: payload }),
  createCampaign: (payload) => req('/api/campaigns', { method: 'POST', body: payload }),
  campaigns: () => req('/api/campaigns'),
  search: (q) => req('/api/search', { method: 'POST', body: { q } }),
}
