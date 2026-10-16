import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import ActivityFeed from './components/ActivityFeed'
import AdjustStockModal from './components/AdjustStockModal'
import ConfirmDeleteModal from './components/ConfirmDeleteModal'
import Icon from './components/Icon'
import ProductFormModal from './components/ProductFormModal'
import ProductTable from './components/ProductTable'
import Sidebar from './components/Sidebar'
import StatCards from './components/StatCards'

// Set at image build time to the Git commit SHA (see frontend/Dockerfile).
const UI_VERSION = import.meta.env.VITE_APP_VERSION || 'dev'

const EMPTY_STATS = {
  total_products: 0,
  total_units: 0,
  low_stock: 0,
  out_of_stock: 0,
  inventory_value: 0,
}

export default function App() {
  const [products, setProducts] = useState([])
  const [stats, setStats] = useState(EMPTY_STATS)
  const [movements, setMovements] = useState([])
  const [apiVersion, setApiVersion] = useState(null)
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({ q: '', category: '', status: '' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dialog, setDialog] = useState(null) // { type: 'product' | 'adjust' | 'delete', product? }
  const [toast, setToast] = useState('')

  const refresh = useCallback(async () => {
    try {
      const [productList, summary, feed] = await Promise.all([
        api.listProducts(filters),
        api.stats(),
        api.movements(),
      ])
      setProducts(productList)
      setStats(summary)
      setMovements(feed)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    refresh()
  }, [refresh])

  useEffect(() => {
    api
      .info()
      .then((info) => setApiVersion(info.version))
      .catch(() => setApiVersion(null))
  }, [])

  // Debounce the search box so the API isn't queried on every keystroke.
  useEffect(() => {
    const timer = setTimeout(() => {
      const q = search.trim()
      setFilters((current) => (current.q === q ? current : { ...current, q }))
    }, 250)
    return () => clearTimeout(timer)
  }, [search])

  useEffect(() => {
    if (!toast) return undefined
    const timer = setTimeout(() => setToast(''), 3000)
    return () => clearTimeout(timer)
  }, [toast])

  const updateFilters = (changes) => setFilters((current) => ({ ...current, ...changes }))
  const closeDialog = useCallback(() => setDialog(null), [])

  const finish = async (message) => {
    setDialog(null)
    setToast(message)
    await refresh()
  }

  const saveProduct = async (data) => {
    if (dialog.product) {
      await api.updateProduct(dialog.product.id, data)
      await finish(`Saved ${data.name}`)
    } else {
      await api.createProduct(data)
      await finish(`Added ${data.name}`)
    }
  }

  const adjustStock = async (data) => {
    const updated = await api.adjustStock(dialog.product.id, data)
    await finish(`${updated.name}: ${updated.quantity} units on hand`)
  }

  const deleteProduct = async () => {
    await api.deleteProduct(dialog.product.id)
    await finish(`Deleted ${dialog.product.name}`)
  }

  return (
    <div className="app">
      <Sidebar uiVersion={UI_VERSION} apiVersion={apiVersion} online={!error} />

      <main className="main" id="overview">
        <header className="topbar">
          <div>
            <p className="eyebrow">Inventory overview</p>
            <h1>Inventory at a glance</h1>
          </div>
          <div className="topbar-actions">
            <label className="search">
              <Icon name="search" />
              <input
                type="search"
                placeholder="Search name or SKU"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                aria-label="Search products"
              />
            </label>
            <button
              type="button"
              className="btn primary"
              onClick={() => setDialog({ type: 'product' })}
            >
              <Icon name="plus" />
              Add product
            </button>
          </div>
        </header>

        {error && (
          <div className="alert" role="alert">
            <Icon name="alert" />
            <span>{error}</span>
            <button type="button" className="btn small" onClick={refresh}>
              Retry
            </button>
          </div>
        )}

        <StatCards stats={stats} onSelectStatus={(status) => updateFilters({ status })} />

        <div className="content-grid">
          <ProductTable
            products={products}
            loading={loading}
            filters={filters}
            onFiltersChange={updateFilters}
            onAdjust={(product) => setDialog({ type: 'adjust', product })}
            onEdit={(product) => setDialog({ type: 'product', product })}
            onDelete={(product) => setDialog({ type: 'delete', product })}
          />
          <ActivityFeed movements={movements} />
        </div>
      </main>

      {dialog?.type === 'product' && (
        <ProductFormModal product={dialog.product} onClose={closeDialog} onSave={saveProduct} />
      )}
      {dialog?.type === 'adjust' && (
        <AdjustStockModal product={dialog.product} onClose={closeDialog} onSave={adjustStock} />
      )}
      {dialog?.type === 'delete' && (
        <ConfirmDeleteModal
          product={dialog.product}
          onClose={closeDialog}
          onConfirm={deleteProduct}
        />
      )}
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </div>
  )
}
