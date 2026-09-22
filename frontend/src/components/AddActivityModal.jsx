import React, { useState } from 'react'
import { apiService } from '../services/api'

export default function AddActivityModal({ isOpen, leadId, onClose, onActivityAdded }) {
  const [formData, setFormData] = useState({
    type: 'call',
    subject: 'Follow-up discussion',
    notes: '',
    outcome: 'interested',
    performedByName: 'Priya Sharma'
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const res = await apiService.addLeadActivity(leadId, formData)
      if (res.success) {
        onActivityAdded && onActivityAdded(res.data)
        onClose()
      } else {
        setError(res.message || 'Failed to log activity')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to log activity')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', backdropFilter: 'blur(4px)', zIndex: 1050 }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content border-0 shadow-lg" style={{ borderRadius: '16px', overflow: 'hidden' }}>
          <div className="modal-header bg-light border-0 px-4 py-3">
            <h5 className="modal-title fw-bold">Log New Activity</h5>
            <button type="button" className="btn-close" onClick={onClose} disabled={loading}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body p-4">
              {error && (
                <div className="alert alert-danger py-2 px-3 small mb-3">
                  {error}
                </div>
              )}

              <div className="mb-3">
                <label className="form-label small fw-semibold">Activity Type</label>
                <select name="type" className="form-select" value={formData.type} onChange={handleChange}>
                  <option value="call">Phone Call (+10 pts / multiple calls)</option>
                  <option value="demo">Product Demo (+20 pts)</option>
                  <option value="meeting">Sales Meeting</option>
                  <option value="email">Email</option>
                  <option value="note">Internal Note</option>
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label small fw-semibold">Subject / Title</label>
                <input
                  type="text"
                  name="subject"
                  required
                  className="form-control"
                  placeholder="e.g. Discussed course curriculum & payment plan"
                  value={formData.subject}
                  onChange={handleChange}
                />
              </div>

              <div className="mb-3">
                <label className="form-label small fw-semibold">Outcome</label>
                <select name="outcome" className="form-select" value={formData.outcome} onChange={handleChange}>
                  <option value="interested">Interested - High buying intent</option>
                  <option value="demo_completed">Demo Successfully Completed</option>
                  <option value="callback_requested">Callback Requested</option>
                  <option value="pricing_shared">Pricing Quote Shared</option>
                  <option value="no_answer">No Answer / Left Voicemail</option>
                  <option value="not_interested">Not Interested</option>
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label small fw-semibold">Detailed Notes</label>
                <textarea
                  name="notes"
                  rows="3"
                  className="form-control"
                  placeholder="Key takeaways, questions asked by candidate, objections..."
                  value={formData.notes}
                  onChange={handleChange}
                ></textarea>
              </div>
            </div>

            <div className="modal-footer border-0 px-4 pb-4">
              <button type="button" className="btn btn-light" onClick={onClose} disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary px-4" disabled={loading}>
                {loading ? 'Saving...' : 'Save Activity & Update Recency'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
