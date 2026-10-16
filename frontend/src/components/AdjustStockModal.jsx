import { useState } from 'react'
import { formatNumber } from '../format'
import useSubmit from '../useSubmit'
import Modal from './Modal'

const REASONS = {
  RESTOCK: { label: 'Restock', hint: 'Goods received', sign: 1 },
  SALE: { label: 'Sale', hint: 'Goods sold or shipped', sign: -1 },
  ADJUSTMENT: { label: 'Correction', hint: 'Stock-take, damage, returns', sign: null },
}

export default function AdjustStockModal({ product, onClose, onSave }) {
  const [reason, setReason] = useState('RESTOCK')
  const [direction, setDirection] = useState(-1)
  const [units, setUnits] = useState('1')
  const [note, setNote] = useState('')
  const { busy, error, run } = useSubmit(onSave)

  const amount = Number(units)
  const validAmount = Number.isInteger(amount) && amount >= 1
  const change = (REASONS[reason].sign ?? direction) * (validAmount ? amount : 0)
  const resulting = product.quantity + change
  const canSubmit = validAmount && resulting >= 0 && !busy

  const handleSubmit = (event) => {
    event.preventDefault()
    if (canSubmit) run({ change, reason, note: note.trim() })
  }

  return (
    <Modal eyebrow={product.sku} title={`Adjust stock · ${product.name}`} onClose={onClose}>
      <form className="form" onSubmit={handleSubmit}>
        <fieldset className="reason-picker">
          <legend>Reason</legend>
          {Object.entries(REASONS).map(([key, option]) => (
            <label key={key} className={`reason ${reason === key ? 'selected' : ''}`}>
              <input
                type="radio"
                name="reason"
                value={key}
                checked={reason === key}
                onChange={() => setReason(key)}
              />
              <strong>{option.label}</strong>
              <small>{option.hint}</small>
            </label>
          ))}
        </fieldset>

        {reason === 'ADJUSTMENT' && (
          <div className="segmented wide" role="group" aria-label="Direction">
            <button
              type="button"
              className={direction === 1 ? 'active' : undefined}
              aria-pressed={direction === 1}
              onClick={() => setDirection(1)}
            >
              Add units
            </button>
            <button
              type="button"
              className={direction === -1 ? 'active' : undefined}
              aria-pressed={direction === -1}
              onClick={() => setDirection(-1)}
            >
              Remove units
            </button>
          </div>
        )}

        <div className="form-row">
          <label>
            Units
            <input
              type="number"
              min="1"
              step="1"
              required
              value={units}
              onChange={(event) => setUnits(event.target.value)}
              autoFocus
            />
          </label>
          <label>
            Note
            <input
              value={note}
              maxLength={200}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Order #, invoice…"
            />
          </label>
        </div>

        <div className={`stock-preview ${resulting < 0 ? 'bad' : ''}`} aria-live="polite">
          {resulting < 0 ? (
            <span>Only {formatNumber(product.quantity)} units available</span>
          ) : (
            <>
              <span>On hand {formatNumber(product.quantity)}</span>
              <span aria-hidden="true">→</span>
              <strong>{formatNumber(resulting)} after this change</strong>
            </>
          )}
        </div>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <div className="form-actions">
          <button type="button" className="btn ghost" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn primary" disabled={!canSubmit}>
            {busy ? 'Saving…' : 'Record movement'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
