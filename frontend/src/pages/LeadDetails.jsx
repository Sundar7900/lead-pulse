import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiService } from '../services/api'
import PriorityBadge from '../components/PriorityBadge'
import ScoreBadge from '../components/ScoreBadge'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import AddActivityModal from '../components/AddActivityModal'

export default function LeadDetails() {
  const { id } = useParams()
  const [lead, setLead] = useState(null)
  const [activities, setActivities] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isActivityModalOpen, setIsActivityModalOpen] = useState(false)
  const [recalculating, setRecalculating] = useState(false)
  const [statusUpdating, setStatusUpdating] = useState(false)
  const [feedbackMsg, setFeedbackMsg] = useState(null)

  const loadLeadAndActivities = async () => {
    try {
      setLoading(true)
      setError(null)
      const [leadRes, activitiesRes] = await Promise.all([
        apiService.getLead(id),
        apiService.getLeadActivities(id)
      ])

      if (leadRes.success && leadRes.data) {
        setLead(leadRes.data)
      } else {
        setError('Lead not found')
      }

      if (activitiesRes.success && activitiesRes.data) {
        setActivities(activitiesRes.data)
      }
    } catch (err) {
      console.error('Failed to load lead details:', err)
      setError(err.response?.data?.message || err.message || 'Error loading lead')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadLeadAndActivities()
  }, [id])

  const handleRecalculateScore = async () => {
    setRecalculating(true)
    setFeedbackMsg(null)
    try {
      const res = await apiService.calculateLeadScore(id)
      if (res.success && res.data) {
        setLead(prev => ({
          ...prev,
          leadScore: res.data.leadScore,
          priority: res.data.priority,
          scoreBreakdown: res.data.scoreBreakdown
        }))
        setFeedbackMsg({ type: 'success', text: `Score recalculated: ${res.data.leadScore} pts (${res.data.priority.toUpperCase()} priority)` })
      }
    } catch (err) {
      setFeedbackMsg({ type: 'danger', text: 'Recalculation failed: ' + err.message })
    } finally {
      setRecalculating(false)
    }
  }

  const handleStatusChange = async (newStatus) => {
    setStatusUpdating(true)
    try {
      const res = await apiService.updateLead(id, { status: newStatus })
      if (res.success && res.data) {
        setLead(res.data)
        setFeedbackMsg({ type: 'success', text: `Lead status updated to ${newStatus}` })
      }
    } catch (err) {
      setFeedbackMsg({ type: 'danger', text: 'Status update failed: ' + err.message })
    } finally {
      setStatusUpdating(false)
    }
  }

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '₹0'
    return '₹' + Number(val).toLocaleString('en-IN')
  }

  const formatDate = (val) => {
    if (!val) return 'N/A'
    try {
      const d = new Date(val)
      return d.toLocaleString('en-IN', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
    } catch {
      return String(val)
    }
  }

  if (loading) {
    return <LoadingSpinner message="Loading candidate profile & score breakdown..." />
  }

  if (error || !lead) {
    return (
      <div className="card p-5 text-center my-4 border-0 shadow-sm">
        <h4 className="text-danger fw-bold">Lead Profile Not Found</h4>
        <p className="text-muted">{error || 'Unable to locate lead with this ID'}</p>
        <div>
          <Link to="/leads" className="btn btn-primary btn-sm px-4">
            ← Back to Leads
          </Link>
        </div>
      </div>
    )
  }

  const breakdown = lead.scoreBreakdown || {}

  return (
    <div className="lead-details-view">
      {/* Breadcrumb & Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <nav aria-label="breadcrumb">
            <ol className="breadcrumb mb-1">
              <li className="breadcrumb-item">
                <Link to="/leads" className="text-decoration-none">Leads</Link>
              </li>
              <li className="breadcrumb-item active text-dark fw-semibold" aria-current="page">
                {lead.name}
              </li>
            </ol>
          </nav>
          <div className="d-flex align-items-center gap-3">
            <h2 className="fw-bold mb-0">{lead.name}</h2>
            <PriorityBadge priority={lead.priority} />
            <StatusBadge status={lead.status} />
          </div>
        </div>

        <div className="d-flex align-items-center gap-2">
          <button
            className="btn btn-outline-primary d-inline-flex align-items-center gap-2"
            onClick={() => setIsActivityModalOpen(true)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span>+ Log Activity</span>
          </button>

          <button
            className="btn btn-primary d-inline-flex align-items-center gap-2"
            onClick={handleRecalculateScore}
            disabled={recalculating}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={recalculating ? 'spinner-border spinner-border-sm' : ''}>
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            <span>{recalculating ? 'Calculating...' : 'Recalculate Score'}</span>
          </button>
        </div>
      </div>

      {feedbackMsg && (
        <div className={`alert alert-${feedbackMsg.type} alert-dismissible fade show py-2 px-3 small mb-4`} role="alert">
          {feedbackMsg.text}
          <button type="button" className="btn-close py-2" onClick={() => setFeedbackMsg(null)}></button>
        </div>
      )}

      <div className="row g-4">
        {/* Left Column: Lead Info & Activity Timeline */}
        <div className="col-lg-8">
          {/* Lead Information Card */}
          <div className="card p-4 shadow-sm border-0 mb-4" style={{ borderRadius: '14px' }}>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="fw-bold mb-0">Lead Profile Information</h5>
              <div className="d-flex align-items-center gap-2">
                <span className="small text-muted">Change Stage:</span>
                <select
                  className="form-select form-select-sm"
                  style={{ width: '160px' }}
                  value={lead.status}
                  disabled={statusUpdating}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  <option value="new">New</option>
                  <option value="contacted">Contacted</option>
                  <option value="interested">Interested</option>
                  <option value="demo_scheduled">Demo Scheduled</option>
                  <option value="negotiation">Negotiation</option>
                  <option value="converted">Converted</option>
                  <option value="lost">Lost</option>
                </select>
              </div>
            </div>

            <div className="row g-3">
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Email Address</label>
                <div className="fw-semibold text-dark">{lead.email || 'N/A'}</div>
              </div>
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Phone Number</label>
                <div className="fw-semibold text-dark">{lead.phone || 'N/A'}</div>
              </div>
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Location</label>
                <div className="fw-semibold text-dark">{lead.location || 'N/A'}</div>
              </div>

              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Interested Product</label>
                <div className="fw-semibold text-dark">{lead.product}</div>
              </div>
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Budget Allocation</label>
                <div className="fw-bold text-success fs-6">{formatCurrency(lead.budget)}</div>
              </div>
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Assigned BD</label>
                <div className="fw-semibold text-dark">{lead.assignedToName || 'Unassigned'}</div>
              </div>

              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Lead Source</label>
                <div className="text-dark small text-capitalize">{lead.source || 'Website'}</div>
              </div>
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Created At</label>
                <div className="text-dark small">{formatDate(lead.createdAt)}</div>
              </div>
              <div className="col-md-4 col-sm-6">
                <label className="text-muted small mb-1">Next Follow-up</label>
                <div className="text-dark small">{lead.nextFollowUpAt ? formatDate(lead.nextFollowUpAt) : 'None scheduled'}</div>
              </div>
            </div>
          </div>

          {/* Activity Timeline Card */}
          <div className="card p-4 shadow-sm border-0" style={{ borderRadius: '14px' }}>
            <div className="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h5 className="fw-bold mb-0">Activity History & Timeline</h5>
                <p className="text-muted small mb-0">Chronological interaction logs for this lead</p>
              </div>
              <button
                className="btn btn-sm btn-outline-secondary"
                onClick={() => setIsActivityModalOpen(true)}
              >
                + Log New Interaction
              </button>
            </div>

            {activities.length === 0 ? (
              <EmptyState
                title="No Activities Logged Yet"
                message="Add phone calls, demo schedules, or notes to build engagement and boost the lead's score."
                action={
                  <button className="btn btn-sm btn-primary" onClick={() => setIsActivityModalOpen(true)}>
                    Log First Activity
                  </button>
                }
              />
            ) : (
              <div className="activity-timeline ps-3">
                {activities.map((act) => {
                  const actId = act._id || act.id
                  return (
                    <div key={actId} className="activity-item">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <span className="badge bg-light text-dark border text-uppercase" style={{ fontSize: '0.7rem' }}>
                          {act.type}
                        </span>
                        <span className="text-muted small" style={{ fontSize: '0.75rem' }}>
                          {formatDate(act.performedAt)}
                        </span>
                      </div>
                      <h6 className="fw-bold text-dark mb-1">{act.subject}</h6>
                      {act.notes && (
                        <p className="text-muted small mb-2" style={{ whiteSpace: 'pre-line' }}>
                          {act.notes}
                        </p>
                      )}
                      <div className="d-flex gap-2 align-items-center small text-muted">
                        <span>By: <strong>{act.performedByName || 'Sales Rep'}</strong></span>
                        {act.outcome && (
                          <>
                            <span>•</span>
                            <span className="badge bg-secondary-subtle text-secondary">{act.outcome}</span>
                          </>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Scoring Engine Breakdown Card */}
        <div className="col-lg-4">
          <div className="card p-4 shadow-sm border-0 mb-4" style={{ borderRadius: '14px' }}>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="fw-bold mb-0">Lead Score Engine</h5>
              <span className="badge bg-light text-dark border small">Rule-based</span>
            </div>

            <div className="text-center py-4 bg-light rounded-3 mb-4">
              <div className="score-display fw-bold" style={{ color: lead.leadScore >= 70 ? '#ef4444' : lead.leadScore >= 40 ? '#f59e0b' : '#64748b' }}>
                {lead.leadScore || 0}
              </div>
              <div className="mt-1">
                <PriorityBadge priority={lead.priority} />
              </div>
              <p className="text-muted small mt-2 mb-0">
                {lead.leadScore >= 70
                  ? 'High buying signals! Priority outreach recommended.'
                  : lead.leadScore >= 40
                  ? 'Moderate interest. Schedule product demo.'
                  : 'Low engagement. Continue nurturing campaign.'}
              </p>
            </div>

            <h6 className="fw-bold mb-3">Factor Score Breakdown</h6>
            <div className="factor-breakdown">
              <div className="factor-row">
                <span className="small text-muted">Budget Factor</span>
                <span className="small fw-bold text-dark">
                  +{breakdown.budgetFactor || 0} pts
                </span>
              </div>
              <div className="factor-row">
                <span className="small text-muted">Call Count Engagement</span>
                <span className="small fw-bold text-dark">
                  +{breakdown.callFactor || 0} pts
                </span>
              </div>
              <div className="factor-row">
                <span className="small text-muted">Product Demo Requested</span>
                <span className="small fw-bold text-dark">
                  +{breakdown.demoFactor || (lead.demoRequested ? 20 : 0)} pts
                </span>
              </div>
              <div className="factor-row">
                <span className="small text-muted">Pricing Plan Asked</span>
                <span className="small fw-bold text-dark">
                  +{breakdown.pricingFactor || (lead.pricingRequested ? 15 : 0)} pts
                </span>
              </div>
              <div className="factor-row">
                <span className="small text-muted">Down Payment Paid</span>
                <span className="small fw-bold text-dark">
                  +{breakdown.dpPaidFactor || (lead.dpPaid ? 25 : 0)} pts
                </span>
              </div>
              <div className="factor-row">
                <span className="small text-muted">Recent Activity (within 7d)</span>
                <span className="small fw-bold text-dark">
                  +{breakdown.recencyFactor || 0} pts
                </span>
              </div>
              <div className="factor-row pt-2 fw-bold">
                <span className="text-dark">Total Score</span>
                <span className="text-primary">{lead.leadScore || 0} / 100</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-top">
              <button
                className="btn btn-outline-primary btn-sm w-100"
                onClick={handleRecalculateScore}
                disabled={recalculating}
              >
                {recalculating ? 'Evaluating rules...' : '⚡ Re-evaluate Score Rules'}
              </button>
            </div>
          </div>

          {/* Quick Guidance Box */}
          <div className="card p-3 shadow-sm border-0 bg-primary-subtle text-primary-emphasis" style={{ borderRadius: '14px' }}>
            <h6 className="fw-bold mb-1">💡 Scoring Rule Tips</h6>
            <ul className="small ps-3 mb-0" style={{ fontSize: '0.8rem' }}>
              <li>Budget &ge; ₹5,00,000 adds +20 points</li>
              <li>Booking a demo adds +20 points</li>
              <li>Inquiring about pricing adds +15 points</li>
              <li>Logging 3+ calls adds +10 points</li>
              <li>Activity in past 7 days adds +10 points</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Log Activity Modal */}
      <AddActivityModal
        isOpen={isActivityModalOpen}
        leadId={id}
        onClose={() => setIsActivityModalOpen(false)}
        onActivityAdded={() => {
          loadLeadAndActivities()
        }}
      />
    </div>
  )
}
