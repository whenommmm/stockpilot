import {
  CATEGORIES,
  formatMoney,
  formatNumber,
  formatPrice,
  STATUS_LABELS,
  titleCase,
} from '../format'
import Icon from './Icon'

const STATUS_FILTERS = [
  ['', 'All'],
  ['IN_STOCK', 'In stock'],
  ['LOW_STOCK', 'Low'],
  ['OUT_OF_STOCK', 'Out'],
]

function StockLevel({ product }) {
  // Scale the bar so the reorder marker sits at one third of the track.
  const scale = Math.max(product.reorder_level * 3, product.quantity, 1)
  return (
    <div className="stock-level">
      <span>{formatNumber(product.quantity)}</span>
      <div className="meter" title={`Reorder level: ${product.reorder_level}`}>
        <i
          className={product.status.toLowerCase()}
          style={{ width: `${(product.quantity / scale) * 100}%` }}
        />
        <b style={{ left: `${(product.reorder_level / scale) * 100}%` }} />
      </div>
    </div>
  )
}

export default function ProductTable({
  products,
  loading,
  filters,
  onFiltersChange,
  onAdjust,
  onEdit,
  onDelete,
}) {
  let body
  if (loading) {
    body = <div className="empty">Loading products…</div>
  } else if (products.length === 0) {
    body = <div className="empty">No products match these filters.</div>
  } else {
    body = (
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Category</th>
              <th className="num">Stock</th>
              <th className="num">Unit price</th>
              <th className="num">Value</th>
              <th>Status</th>
              <th>
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>
                  <div className="product-cell">
                    <strong>{product.name}</strong>
                    <span>
                      <code>{product.sku}</code>
                      {product.supplier && ` · ${product.supplier}`}
                    </span>
                  </div>
                </td>
                <td>{titleCase(product.category)}</td>
                <td className="num">
                  <StockLevel product={product} />
                </td>
                <td className="num">{formatPrice(product.unit_price)}</td>
                <td className="num">{formatMoney(product.quantity * product.unit_price)}</td>
                <td>
                  <span className={`badge ${product.status.toLowerCase()}`}>
                    {STATUS_LABELS[product.status]}
                  </span>
                </td>
                <td>
                  <div className="row-actions">
                    <button type="button" className="btn small" onClick={() => onAdjust(product)}>
                      <Icon name="arrows" size={15} />
                      Adjust
                    </button>
                    <button
                      type="button"
                      className="icon-btn"
                      onClick={() => onEdit(product)}
                      aria-label={`Edit ${product.name}`}
                    >
                      <Icon name="edit" size={16} />
                    </button>
                    <button
                      type="button"
                      className="icon-btn danger"
                      onClick={() => onDelete(product)}
                      aria-label={`Delete ${product.name}`}
                    >
                      <Icon name="trash" size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <section className="panel" id="products" aria-labelledby="products-title">
      <header className="panel-head">
        <div>
          <h2 id="products-title">Products</h2>
          <p className="muted">{loading ? 'Loading…' : `${products.length} shown`}</p>
        </div>
        <div className="filters">
          <select
            aria-label="Filter by category"
            value={filters.category}
            onChange={(event) => onFiltersChange({ category: event.target.value })}
          >
            <option value="">All categories</option>
            {CATEGORIES.map((category) => (
              <option key={category} value={category}>
                {titleCase(category)}
              </option>
            ))}
          </select>
          <div className="segmented" role="group" aria-label="Filter by stock status">
            {STATUS_FILTERS.map(([value, label]) => (
              <button
                key={label}
                type="button"
                className={filters.status === value ? 'active' : undefined}
                aria-pressed={filters.status === value}
                onClick={() => onFiltersChange({ status: value })}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </header>
      {body}
    </section>
  )
}
