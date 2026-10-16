import { shortVersion } from '../format'
import Icon from './Icon'

const LINKS = [
  { href: '#overview', label: 'Overview', icon: 'grid' },
  { href: '#products', label: 'Products', icon: 'box' },
  { href: '#activity', label: 'Stock activity', icon: 'activity' },
]

export default function Sidebar({ uiVersion, apiVersion, online }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          <Icon name="box" size={20} />
        </span>
        <div>
          <strong>StockPilot</strong>
          <small>Inventory control</small>
        </div>
      </div>

      <nav aria-label="Sections">
        {LINKS.map((link, index) => (
          <a key={link.href} href={link.href} className={index === 0 ? 'active' : undefined}>
            <Icon name={link.icon} />
            {link.label}
          </a>
        ))}
      </nav>

      <div className="sidebar-footer">
        <span className={`connection ${online ? 'online' : 'offline'}`}>
          {online ? 'API connected' : 'API unreachable'}
        </span>
        <dl className="build-info">
          <div>
            <dt>UI build</dt>
            <dd>{shortVersion(uiVersion)}</dd>
          </div>
          <div>
            <dt>API build</dt>
            <dd>{shortVersion(apiVersion)}</dd>
          </div>
        </dl>
      </div>
    </aside>
  )
}
