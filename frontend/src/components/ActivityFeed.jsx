import { REASON_LABELS, timeAgo } from '../format'

export default function ActivityFeed({ movements }) {
  return (
    <aside className="panel activity" id="activity" aria-labelledby="activity-title">
      <header className="panel-head">
        <div>
          <h2 id="activity-title">Stock activity</h2>
          <p className="muted">Latest movements across all products</p>
        </div>
      </header>
      {movements.length === 0 ? (
        <div className="empty">No stock movements yet.</div>
      ) : (
        <ol className="feed">
          {movements.map((movement) => (
            <li key={movement.id}>
              <span className={`delta ${movement.change > 0 ? 'in' : 'out'}`}>
                {movement.change > 0 ? `+${movement.change}` : movement.change}
              </span>
              <div>
                <strong>{movement.product_name}</strong>
                <span>
                  {REASON_LABELS[movement.reason]}
                  {movement.note && ` · ${movement.note}`}
                </span>
              </div>
              <time dateTime={movement.created_at}>{timeAgo(movement.created_at)}</time>
            </li>
          ))}
        </ol>
      )}
    </aside>
  )
}
