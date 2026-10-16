import useSubmit from '../useSubmit'
import Modal from './Modal'

export default function ConfirmDeleteModal({ product, onClose, onConfirm }) {
  const { busy, error, run } = useSubmit(onConfirm)

  return (
    <Modal eyebrow={product.sku} title={`Delete ${product.name}?`} onClose={onClose}>
      <p className="dialog-text">
        This removes the product and its whole stock history. It cannot be undone.
      </p>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      <div className="form-actions">
        <button type="button" className="btn ghost" onClick={onClose} autoFocus>
          Cancel
        </button>
        <button type="button" className="btn danger" disabled={busy} onClick={() => run()}>
          {busy ? 'Deleting…' : 'Delete product'}
        </button>
      </div>
    </Modal>
  )
}
