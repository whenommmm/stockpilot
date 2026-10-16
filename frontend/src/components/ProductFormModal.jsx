import { CATEGORIES, titleCase } from '../format'
import useSubmit from '../useSubmit'
import Modal from './Modal'

export default function ProductFormModal({ product, onClose, onSave }) {
  const editing = Boolean(product)
  const { busy, error, run } = useSubmit(onSave)

  const handleSubmit = (event) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const data = {
      name: form.get('name').trim(),
      category: form.get('category'),
      supplier: form.get('supplier').trim(),
      unit_price: Number(form.get('unit_price')),
      reorder_level: Number(form.get('reorder_level')),
    }
    if (!editing) {
      data.sku = form.get('sku').trim().toUpperCase()
      data.quantity = Number(form.get('quantity'))
    }
    run(data)
  }

  return (
    <Modal
      eyebrow={editing ? product.sku : 'New product'}
      title={editing ? `Edit ${product.name}` : 'Add a product'}
      onClose={onClose}
    >
      <form className="form" onSubmit={handleSubmit}>
        {!editing && (
          <div className="form-row">
            <label>
              SKU
              <input
                name="sku"
                required
                minLength={2}
                maxLength={40}
                placeholder="ELEC-1005"
                title="Letters, numbers and dashes"
                autoFocus
              />
            </label>
            <label>
              Opening stock
              <input name="quantity" type="number" min="0" step="1" defaultValue="0" required />
            </label>
          </div>
        )}
        <label>
          Product name
          <input
            name="name"
            required
            maxLength={200}
            defaultValue={product?.name}
            placeholder="e.g. Wireless Mouse"
            autoFocus={editing}
          />
        </label>
        <div className="form-row">
          <label>
            Category
            <select name="category" defaultValue={product?.category ?? 'OTHER'}>
              {CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {titleCase(category)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Supplier
            <input
              name="supplier"
              maxLength={120}
              defaultValue={product?.supplier}
              placeholder="Optional"
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Unit price (₹)
            <input
              name="unit_price"
              type="number"
              min="0"
              step="0.01"
              required
              defaultValue={product?.unit_price ?? 0}
            />
          </label>
          <label>
            Reorder level
            <input
              name="reorder_level"
              type="number"
              min="0"
              step="1"
              required
              defaultValue={product?.reorder_level ?? 10}
            />
          </label>
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
          <button type="submit" className="btn primary" disabled={busy}>
            {busy ? 'Saving…' : editing ? 'Save changes' : 'Add product'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
