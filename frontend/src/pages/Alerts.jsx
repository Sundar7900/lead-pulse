import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiService } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [summary, setSummary] = useState(null)

  // Filters
  const [alertType, setAlertType] = useState('')
  const [severity, setSeverity] = useState('')
  const [isRead, setIsRead] = useState('false') // Default show unread first
  const [markingAll, setMarkingAll] = useState(false)

  const fetchAlerts = async () => {
    try {
      setLoading(true)
      setError(null)
      const params = {
        page: 1,
        per_page: 50
      }

      if (alertType) params.type = alertType
      if (severity) params.severity = severity
      if (isRead !== '') params.isRead = isRead === 'true'

      const [alertsRes, summaryRes] = await Promise.all([
        apiService.getAlerts(params),
        apiService.get('/api/alerts/summary').catch(() => ({ success: false }))
      ])

      if (alertsRes.success && alertsRes.data) {
        setAlerts(alertsRes.data.alerts || [])
      }

      if (summaryRes && summaryRes.success) {
        setSummary(summaryRes.data)
      }
    } catch (err) {
      console.error('Failed to fetch alerts:', err)
      setError(err.response?.data?.message || err.message || 'Error loading alerts')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [alertType, severity, isRead])

  const handleMarkAsRead = async (alertId) => {
    try {
      await apiService.markAlertAsRead(alertId)
      // Update locally
      setAlerts(prev => prev.map(a => (a._id || a.id) === alertId ? { ...a, isRead: true } : a))
      if (summary) {
        setSummary(prev => ({
          ...prev,
          unread: Math.max(0, (prev?.unread || 1) - 1)
        }))
      }
    } catch (err) {
      alert('Failed to mark alert as read: ' + err.message)
    }
  }

  const handleMarkAllRead = async () => {
    setMarkingAll(true)
    try {
      await apiService.put('/api/alerts/mark-all-read', {})
      fetchAlerts()
    } catch (err) {
      alert('Failed to mark all read: ' + err.message)
    } finally {
      setMarkingAll(false)
    }
  }

  const handleDeleteAlert = async (alertId) => {
    try {
      await apiService.delete(`/api/alerts/${alertId}`)
      setAlerts(prev => prev.filter(a => (a._id || a.id) !== alertId))
    } catch (err) {
      alert('Failed to delete alert: ' + err.message)
    }
  }

  const formatDate = (val) => {
    if (!val) return ''
    try {
      const d = new Date(val)
      return d.toLocaleString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    } catch {
      return String(val)
    }
  }

  return (
    <div className="alerts-page">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Sales Alerts & Notifications</h2>
          <p className="text-muted mb-0">Actionable notifications triggered by scoring events and overdue follow-ups</p>
        </div>
        <div>
          <button
            className="btn btn-outline-secondary d-inline-flex align-items-center gap-2"
            onClick={handleMarkAllRead}
            disabled={markingAll || alerts.length === 0}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            <span>{markingAll ? 'Marking...' : 'Mark All as Read'}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards for Alerts */}
      {summary && (
        <div className="row g-3 mb-4">
          <div className="col-md-4">
            <div className="card p-3 border-0 shadow-sm d-flex flex-row align-items-center gap-3">
              <div className="p-3 bg-danger-subtle text-danger rounded-3 fw-bold fs-4">
                {summary.unread || 0}
              </div>
              <div>
                <div className="small text-muted text-uppercase fw-semibold" style={{ fontSize: '0.72rem' }}>
                  Unread Alerts
                </div>
                <div className="text-dark small">Requiring sales attention</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card p-3 border-0 shadow-sm d-flex flex-row align-items-center gap-3">
              <div className="p-3 bg-warning-subtle text-warning rounded-3 fw-bold fs-4">
                {summary.bySeverity?.high || 0}
              </div>
              <div>
                <div className="small text-muted text-uppercase fw-semibold" style={{ fontSize: '0.72rem' }}>
                  High Severity Triggers
                </div>
                <div className="text-dark small">High-value leads (score &ge; 70)</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card p-3 border-0 shadow-sm d-flex flex-row align-items-center gap-3">
              <div className="p-3 bg-primary-subtle text-primary rounded-3 fw-bold fs-4">
                {summary.byType?.FOLLOW_UP_REQUIRED || 0}
              </div>
              <div>
                <div className="small text-muted text-uppercase fw-semibold" style={{ fontSize: '0.72rem' }}>
                  Overdue Follow-ups
                </div>
                <div className="text-dark small">Missed contact schedules</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters Toolbar */}
      <div className="card p-3 mb-4 border-0 shadow-sm" style={{ borderRadius: '12px' }}>
        <div className="row g-2 align-items-center">
          <div className="col-md-4">
            <select
              className="form-select"
              value={alertType}
              onChange={(e) => setAlertType(e.target.value)}
            >
              <option value="">All Alert Types</option>
              <option value="HIGH_VALUE_LEAD">High-Value Lead Alert</option>
              <option value="FOLLOW_UP_REQUIRED">Follow-up Required</option>
              <option value="LEAD_INACTIVE">Lead Inactive Alert</option>
              <option value="CONVERSION_OPPORTUNITY">Conversion Opportunity</option>
            </select>
          </div>

          <div className="col-md-3">
            <select
              className="form-select"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value="">All Severities</option>
              <option value="high">High Severity</option>
              <option value="medium">Medium Severity</option>
              <option value="low">Low Severity</option>
            </select>
          </div>

          <div className="col-md-3">
            <select
              className="form-select"
              value={isRead}
              onChange={(e) => setIsRead(e.target.value)}
            >
              <option value="false">Unread Only</option>
              <option value="true">Read Only</option>
              <option value="">All (Read & Unread)</option>
            </select>
          </div>

          <div className="col-md-2 text-end">
            <button
              className="btn btn-outline-secondary w-100"
              onClick={() => {
                setAlertType('')
                setSeverity('')
                setIsRead('')
              }}
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Alert Cards Feed */}
      {loading ? (
        <LoadingSpinner message="Fetching live alerts..." />
      ) : error ? (
        <div className="card p-4 text-center text-danger border-0 shadow-sm">
          <p className="mb-2">{error}</p>
          <button className="btn btn-sm btn-outline-primary" onClick={fetchAlerts}>Retry</button>
        </div>
      ) : alerts.length === 0 ? (
        <EmptyState
          title="No Alerts Found"
          message="No notifications match the chosen filters. Try switching to 'All' to view resolved alerts."
          action={
            <button className="btn btn-sm btn-primary" onClick={() => { setAlertType(''); setSeverity(''); setIsRead(''); }}>
              Show All Alerts
            </button>
          }
        />
      ) : (
        <div className="d-flex flex-column gap-2">
          {alerts.map((alert) => {
            const alertId = alert._id || alert.id
            const isUnread = !alert.isRead

            return (
              <div
                key={alertId}
                className={`alert-item severity-${alert.severity} ${isUnread ? 'unread' : 'opacity-75'} d-flex justify-content-between align-items-center gap-3`}
              >
                <div className="d-flex align-items-start gap-3 flex-grow-1">
                  <div className="mt-1">
                    {alert.severity === 'high' ? (
                      <span className="badge bg-danger text-white rounded-pill px-2 py-1" style={{ fontSize: '0.68rem' }}>
                        HIGH
                      </span>
                    ) : alert.severity === 'medium' ? (
                      <span className="badge bg-warning text-dark rounded-pill px-2 py-1" style={{ fontSize: '0.68rem' }}>
                        MED
                      </span>
                    ) : (
                      <span className="badge bg-info text-white rounded-pill px-2 py-1" style={{ fontSize: '0.68rem' }}>
                        INFO
                      </span>
                    )}
                  </div>

                  <div>
                    <div className="d-flex align-items-center gap-2 mb-1">
                      <span className="small text-muted text-uppercase fw-semibold" style={{ fontSize: '0.72rem' }}>
                        {alert.type.replace(/_/g, ' ')}
                      </span>
                      <span className="text-muted small">•</span>
                      <span className="text-muted small" style={{ fontSize: '0.75rem' }}>
                        {formatDate(alert.createdAt)}
                      </span>
                    </div>

                    <div className="d-flex align-items-center gap-2 mb-1">
                      <span className="fw-bold text-dark">{alert.leadName}</span>
                      {isUnread && (
                        <span className="badge bg-danger-subtle text-danger" style={{ fontSize: '0.65rem' }}>
                          NEW
                        </span>
                      )}
                    </div>

                    <p className="mb-0 text-muted small" style={{ fontSize: '0.85rem' }}>
                      {alert.message}
                    </p>
                  </div>
                </div>

                <div className="d-flex align-items-center gap-2 flex-shrink-0">
                  {alert.leadId && (
                    <Link to={`/leads/${alert.leadId}`} className="btn btn-sm btn-light border px-3">
                      Open Lead →
                    </Link>
                  )}

                  {isUnread && (
                    <button
                      className="btn btn-sm btn-outline-secondary"
                      onClick={() => handleMarkAsRead(alertId)}
                      title="Mark as Read"
                    >
                      ✓ Mark Read
                    </button>
                  )}

                  <button
                    className="btn btn-sm btn-light border text-muted px-2"
                    onClick={() => handleDeleteAlert(alertId)}
                    title="Dismiss"
                  >
                    ×
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
