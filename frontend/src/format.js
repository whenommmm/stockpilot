export const CATEGORIES = ['ELECTRONICS', 'GROCERY', 'APPAREL', 'HOME', 'OFFICE', 'OTHER']

export const STATUS_LABELS = {
  IN_STOCK: 'In stock',
  LOW_STOCK: 'Low stock',
  OUT_OF_STOCK: 'Out of stock',
}

export const REASON_LABELS = {
  RESTOCK: 'Restock',
  SALE: 'Sale',
  ADJUSTMENT: 'Correction',
}

const money = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})
const price = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 2,
})
const count = new Intl.NumberFormat('en-IN')
const relative = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

export const formatMoney = (value) => money.format(value)
export const formatPrice = (value) => price.format(value)
export const formatNumber = (value) => count.format(value)

export const titleCase = (value) =>
  value.charAt(0) + value.slice(1).toLowerCase().replaceAll('_', ' ')

const UNITS = [
  ['day', 86400],
  ['hour', 3600],
  ['minute', 60],
]

export function timeAgo(isoString) {
  const seconds = Math.round((new Date(isoString).getTime() - Date.now()) / 1000)
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) return relative.format(Math.round(seconds / size), unit)
  }
  return 'just now'
}

// Builds are tagged with the full Git SHA; show the familiar 7-character form.
export const shortVersion = (version) =>
  version && /^[0-9a-f]{40}$/.test(version) ? version.slice(0, 7) : version || '—'
