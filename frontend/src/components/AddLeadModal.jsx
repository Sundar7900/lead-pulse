import React, { useState } from 'react'
import { apiService } from '../services/api'

export default function AddLeadModal({ isOpen, onClose, onLeadCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    location: 'Bangalore',
    product: 'Data Science',
    budget: 500000,
    assignedToName: 'Priya Sharma',
    source: 'website',
    status: 'new',
    demoRequested: false,
    pricingRequested: false,
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  if (!isOpen) return null

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const payload = {
        ...formData,
        budget: Number(formData.budget) || 0
      }
      const res = await apiService.createLead(payload)
      if (res.success) {
        onLeadCreated && onLeadCreated(res.data)
        onClose()
      } else {
        setError(res.message || 'Failed to create lead')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to create lead')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', backdropFilter: 'blur(4px)', zIndex: 1050 }}>
      <div className="modal-dialog modal-dialog-centered modal-lg">
        <div className="modal-content border-0 shadow-lg" style={{ borderRadius: '16px', overflow: 'hidden' }}>
          <div className="modal-header bg-light border-0 px-4 py-3">
            <h5 className="modal-title fw-bold">Create New Sales Lead</h5>
            <button type="button" className="btn-close" onClick={onClose} disabled={loading}></button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="modal-body p-4">
              {error && (
                <div className="alert alert-danger py-2 px-3 small mb-3">
                  {error}
                </div>
              )}

              <div className="row g-3">
                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Full Name *</label>
                  <input
                    type="text"
                    name="name"
                    required
                    className="form-control"
                    placeholder="e.g. Arun Kumar"
                    value={formData.name}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Email Address *</label>
                  <input
                    type="email"
                    name="email"
                    required
                    className="form-control"
                    placeholder="e.g. arun@example.com"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Phone Number</label>
                  <input
                    type="tel"
                    name="phone"
                    className="form-control"
                    placeholder="e.g. 9876543210"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Location</label>
                  <select name="location" className="form-select" value={formData.location} onChange={handleChange}>
                    <option value="Bangalore">Bangalore</option>
                    <option value="Chennai">Chennai</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Pune">Pune</option>
                    <option value="Kolkata">Kolkata</option>
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Product / Course *</label>
                  <select name="product" className="form-select" value={formData.product} onChange={handleChange}>
                    <option value="Data Science">Data Science</option>
                    <option value="Full Stack Development">Full Stack Development</option>
                    <option value="Artificial Intelligence">Artificial Intelligence</option>
                    <option value="Machine Learning">Machine Learning</option>
                    <option value="Cloud Computing">Cloud Computing</option>
                    <option value="Cybersecurity">Cybersecurity</option>
                    <option value="DevOps Engineering">DevOps Engineering</option>
                    <option value="Business Analytics">Business Analytics</option>
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Budget (₹) *</label>
                  <input
                    type="number"
                    name="budget"
                    required
                    step="10000"
                    min="50000"
                    className="form-control"
                    value={formData.budget}
                    onChange={handleChange}
                  />
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Assigned BD</label>
                  <select name="assignedToName" className="form-select" value={formData.assignedToName} onChange={handleChange}>
                    <option value="Priya Sharma">Priya Sharma (North)</option>
                    <option value="Rahul Verma">Rahul Verma (South)</option>
                    <option value="Ananya Iyer">Ananya Iyer (West)</option>
                    <option value="Vikram Patel">Vikram Patel (East)</option>
                    <option value="Sneha Reddy">Sneha Reddy (Central)</option>
                  </select>
                </div>

                <div className="col-md-6">
                  <label className="form-label small fw-semibold">Lead Source</label>
                  <select name="source" className="form-select" value={formData.source} onChange={handleChange}>
                    <option value="website">Website</option>
                    <option value="linkedin">LinkedIn</option>
                    <option value="referral">Referral</option>
                    <option value="google_ads">Google Ads</option>
                    <option value="direct">Direct</option>
                    <option value="webinar">Webinar</option>
                  </select>
                </div>

                <div className="col-12 mt-3">
                  <div className="d-flex gap-4 p-3 bg-light rounded-3">
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="demoRequested"
                        name="demoRequested"
                        checked={formData.demoRequested}
                        onChange={handleChange}
                      />
                      <label className="form-check-label small fw-semibold" htmlFor="demoRequested">
                        Demo Requested (+20 pts)
                      </label>
                    </div>
                    <div className="form-check">
                      <input
                        className="form-check-input"
                        type="checkbox"
                        id="pricingRequested"
                        name="pricingRequested"
                        checked={formData.pricingRequested}
                        onChange={handleChange}
                      />
                      <label className="form-check-label small fw-semibold" htmlFor="pricingRequested">
                        Pricing Asked (+15 pts)
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer border-0 px-4 pb-4">
              <button type="button" className="btn btn-light" onClick={onClose} disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary px-4" disabled={loading}>
                {loading ? 'Creating...' : 'Create Lead & Calculate Score'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
