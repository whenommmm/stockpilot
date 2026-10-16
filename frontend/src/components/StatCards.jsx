import { formatMoney, formatNumber } from '../format'
import Icon from './Icon'

const CARDS = [
  { key: 'total_products', label: 'Products', icon: 'box', format: formatNumber },
  { key: 'total_units', label: 'Units on hand', icon: 'layers', format: formatNumber },
  { key: 'inventory_value', label: 'Inventory value', icon: 'rupee', format: formatMoney },
  {
    key: 'low_stock',
    label: 'Low stock',
    icon: 'alert',
    format: formatNumber,
    tone: 'warn',
    status: 'LOW_STOCK',
    hint: 'At or below reorder level',
  },
  {
    key: 'out_of_stock',
    label: 'Out of stock',
    icon: 'ban',
    format: formatNumber,
    tone: 'danger',
    status: 'OUT_OF_STOCK',
    hint: 'Needs restocking now',
  },
]

function CardBody({ card, value }) {
  return (
    <>
      <span className="stat-icon">
        <Icon name={card.icon} />
      </span>
      <div>
        <p>{card.label}</p>
        <strong>{card.format(value)}</strong>
        {card.hint && <small>{card.hint}</small>}
      </div>
    </>
  )
}

export default function StatCards({ stats, onSelectStatus }) {
  return (
    <section className="stats" aria-label="Inventory summary">
      {CARDS.map((card) => {
        const value = stats[card.key]
        const className = `stat ${card.tone ?? ''} ${card.tone && value > 0 ? 'attention' : ''}`
        // Warning cards double as shortcuts to the matching table filter.
        return card.status ? (
          <button
            key={card.key}
            type="button"
            className={className}
            onClick={() => onSelectStatus(card.status)}
            title={`Show ${card.label.toLowerCase()} products`}
          >
            <CardBody card={card} value={value} />
          </button>
        ) : (
          <article key={card.key} className={className}>
            <CardBody card={card} value={value} />
          </article>
        )
      })}
    </section>
  )
}
