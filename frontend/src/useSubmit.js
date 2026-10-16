import { useState } from 'react'

// Tracks the busy/error state of a dialog action. On success the dialog is closed by its
// parent (and unmounted), so state is only reset when the action fails.
export default function useSubmit(action) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const run = async (...args) => {
    setBusy(true)
    setError('')
    try {
      await action(...args)
    } catch (err) {
      setError(err.message)
      setBusy(false)
    }
  }

  return { busy, error, run }
}
