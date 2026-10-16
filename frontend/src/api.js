// The browser always calls same-origin /api: nginx (Docker Compose) or the Ingress (Kubernetes)
// routes it to the backend, so the UI never needs to know internal hostnames.
const BASE = '/api'

function describeError(status, body) {
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((issue) => {
        const field = issue.loc?.slice(1).join('.')
        const message = issue.msg?.replace(/^Value error, /, '')
        return field ? `${field}: ${message}` : message
      })
      .join('; ')
  }
  return `Request failed (HTTP ${status})`
}

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new Error('Cannot reach the StockPilot API. Is the backend running?')
  }
  if (response.status === 204) return null
  const body = await response.json().catch(() => null)
  if (!response.ok) throw new Error(describeError(response.status, body))
  return body
}

const send = (method, data) => ({ method, body: data === undefined ? undefined : JSON.stringify(data) })

export const api = {
  listProducts(filters) {
    const params = new URLSearchParams()
    for (const [key, value] of Object.entries(filters)) if (value) params.set(key, value)
    const query = params.toString()
    return request(`/products${query ? `?${query}` : ''}`)
  },
  createProduct: (data) => request('/products', send('POST', data)),
  updateProduct: (id, data) => request(`/products/${id}`, send('PUT', data)),
  deleteProduct: (id) => request(`/products/${id}`, send('DELETE')),
  adjustStock: (id, data) => request(`/products/${id}/adjust`, send('POST', data)),
  stats: () => request('/stats'),
  movements: (limit = 15) => request(`/movements?limit=${limit}`),
  info: () => request('/info'),
}
