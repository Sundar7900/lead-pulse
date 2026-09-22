import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiService } from '../services/api'
import StatsCard from '../components/StatsCard'
import PriorityBadge from '../components/PriorityBadge'
import ScoreBadge from '../components/ScoreBadge'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [statistics, setStatistics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [summaryRes, statsRes] = await Promise.all([
        apiService.getDashboardSummary(),
        apiService.getDashboardStatistics()
      ])

      if (summaryRes.success) setSummary(summaryRes.data)
      if (statsRes.success) setStatistics(statsRes.data)
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError(err.response?.data?.message || err.message || 'Error connecting to backend')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleMarkAlertRead = async (alertId) => {
    try {
      await apiService.markAlertAsRead(alertId)
      // Optimistically update summary alerts
      if (summary) {
        setSummary({
          ...summary,
          highlights: {
            ...summary.highlights,
            recentAlerts: summary.highlights.recentAlerts.filter(a => a.id !== alertId)
          },
          overview: {
            ...summary.overview,
            unreadAlerts: Math.max(0, summary.overview.unreadAlerts - 1)
          }
        })
      }
    } catch (err) {
      alert('Failed to mark alert as read: ' + err.message)
    }
  }

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '₹0'
    return '₹' + Number(val).toLocaleString('en-IN')
  }

  if (loading) {
    return <LoadingSpinner message="Gathering sales intelligence & analytics..." />
  }

  if (error) {
    return (
      <div className="card p-4 text-center my-4 border-danger">
        <h5 className="text-danger">Failed to Load Dashboard</h5>
        <p className="text-muted small">{error}</p>
        <div>
          <button className="btn btn-primary btn-sm px-4" onClick={loadData}>
            Retry Connection
          </button>
        </div>
      </div>
    )
  }

  const overview = summary?.overview || {}
  const financials = summary?.financials || {}
  const breakdowns = statistics?.breakdowns || {}
  const scoreDist = statistics?.scoreDistribution || []
  const highValueLeads = summary?.highlights?.highValueLeads || []
  const recentAlerts = summary?.highlights?.recentAlerts || []

  return (
    <div className="dashboard-view">
      {/* Top Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Sales Intelligence Dashboard</h2>
          <p className="text-muted mb-0">Overview of pipeline health, score distribution, and critical alerts</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/leads" className="btn btn-primary d-inline-flex align-items-center gap-2">
            <span>View All Leads</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </Link>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="row g-3 mb-4">
        <div className="col-md-3 col-sm-6">
          <StatsCard
            title="Total Pipeline Leads"
            value={overview.totalLeads || 0}
            subtitle={`${overview.newLeads || 0} new incoming`}
            color="#4f46e5"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            }
          />
        </div>
        <div className="col-md-3 col-sm-6">
          <StatsCard
            title="High-Value Leads"
            value={overview.highValueLeads || 0}
            subtitle="Score >= 70 threshold"
            color="#ef4444"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
            }
          />
        </div>
        <div className="col-md-3 col-sm-6">
          <StatsCard
            title="Pipeline Volume"
            value={formatCurrency(financials.totalBudget)}
            subtitle={`Avg: ${formatCurrency(financials.avgBudget)}/lead`}
            color="#10b981"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            }
          />
        </div>
        <div className="col-md-3 col-sm-6">
          <StatsCard
            title="Conversion Rate"
            value={`${statistics?.conversionMetrics?.conversionRate || 0}%`}
            subtitle={`${overview.convertedLeads || 0} won | ${overview.lostLeads || 0} lost`}
            color="#0ea5e9"
            icon={
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                <polyline points="17 6 23 6 23 12"></polyline>
              </svg>
            }
          />
        </div>
      </div>

      {/* Visual Distributions & Charts Row */}
      <div className="row g-4 mb-4">
        {/* Priority & Status Breakdown */}
        <div className="col-lg-6">
          <div className="card p-4 h-100">
            <h5 className="fw-bold mb-3 d-flex justify-content-between align-items-center">
              <span>Leads by Priority</span>
              <span className="badge bg-light text-muted fw-normal small">Auto-calculated</span>
            </h5>
            
            {/* Visual multi-segment bar */}
            <div className="distribution-bar mb-3" style={{ height: '14px' }}>
              {(breakdowns.byPriority || []).map((p, idx) => {
                const colors = { high: '#ef4444', medium: '#f59e0b', low: '#94a3b8' }
                return (
                  <div
                    key={idx}
                    className="dist-segment"
                    style={{
                      width: `${p.percentage}%`,
                      backgroundColor: colors[p.priority] || '#cbd5e1'
                    }}
                    title={`${p.priority.toUpperCase()}: ${p.count} (${p.percentage}%)`}
                  ></div>
                )
              })}
            </div>

            <div className="row g-2 mb-4">
              {(breakdowns.byPriority || []).map((p, idx) => (
                <div key={idx} className="col-4">
                  <div className="p-2 border rounded-3 text-center">
                    <div className="small text-muted text-uppercase" style={{ fontSize: '0.7rem' }}>{p.priority}</div>
                    <div className="fw-bold fs-5">{p.count}</div>
                    <div className="text-muted small">{p.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>

            <hr className="my-2" />

            <h6 className="fw-bold mt-3 mb-3">Pipeline Funnel by Status</h6>
            <div className="d-flex flex-column gap-2">
              {(breakdowns.byStatus || []).map((s, idx) => (
                <div key={idx} className="d-flex align-items-center justify-content-between gap-3">
                  <div style={{ width: '130px' }}>
                    <StatusBadge status={s.status} />
                  </div>
                  <div className="flex-grow-1">
                    <div className="progress" style={{ height: '8px', backgroundColor: '#f1f5f9' }}>
                      <div
                        className="progress-bar bg-primary"
                        role="progressbar"
                        style={{ width: `${s.percentage}%` }}
                        aria-valuenow={s.percentage}
                        aria-valuemin="0"
                        aria-valuemax="100"
                      ></div>
                    </div>
                  </div>
                  <div className="text-end" style={{ width: '80px' }}>
                    <span className="fw-semibold small">{s.count}</span>
                    <span className="text-muted small ms-1">({s.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Lead Score Distribution */}
        <div className="col-lg-6">
          <div className="card p-4 h-100">
            <h5 className="fw-bold mb-1">Lead Score Distribution</h5>
            <p className="text-muted small mb-4">Frequency breakdown across score brackets (0 - 100)</p>

            <div className="d-flex flex-column gap-3 mb-4">
              {scoreDist.map((item, idx) => {
                const isHigh = item.range === '80+' || item.range === '60-79'
                const barColor = item.range === '80+' ? '#ef4444' : item.range === '60-79' ? '#f97316' : item.range === '40-59' ? '#f59e0b' : '#94a3b8'
                return (
                  <div key={idx}>
                    <div className="d-flex justify-content-between align-items-center mb-1 small">
                      <span className="fw-semibold text-dark">
                        Score {item.range} {isHigh && <span className="badge bg-danger-subtle text-danger ms-1">High Intent</span>}
                      </span>
                      <span className="text-muted">
                        <strong>{item.count}</strong> leads ({item.percentage}%)
                      </span>
                    </div>
                    <div className="progress" style={{ height: '10px', backgroundColor: '#f1f5f9', borderRadius: '999px' }}>
                      <div
                        className="progress-bar"
                        style={{ width: `${item.percentage}%`, backgroundColor: barColor, borderRadius: '999px' }}
                      ></div>
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Performance by BD Representatives */}
            <h6 className="fw-bold mt-2 mb-2">Top Business Development Reps</h6>
            <div className="row g-2">
              {(breakdowns.byBD || []).slice(0, 4).map((bd, idx) => (
                <div key={idx} className="col-6">
                  <div className="p-2 border rounded-3 d-flex align-items-center justify-content-between">
                    <span className="small text-truncate" style={{ maxWidth: '120px' }}>{bd.name}</span>
                    <span className="badge bg-secondary-subtle text-secondary">{bd.count} leads</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* High-Value Leads & Recent Alerts Row */}
      <div className="row g-4">
        {/* High-Value Leads Table */}
        <div className="col-lg-7">
          <div className="card p-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 className="fw-bold mb-0">High-Value Lead Radar</h5>
                <span className="text-muted small">Top prospective deals scoring highest in buying signals</span>
              </div>
              <Link to="/leads?priority=high" className="btn btn-sm btn-outline-primary">
                View All
              </Link>
            </div>

            {highValueLeads.length === 0 ? (
              <EmptyState title="No High-Value Leads" message="No leads have currently reached the score threshold of 70+." />
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Lead</th>
                      <th>Course</th>
                      <th>Budget</th>
                      <th>Score</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {highValueLeads.map((lead) => (
                      <tr key={lead.id}>
                        <td>
                          <div className="fw-bold text-dark">{lead.name}</div>
                        </td>
                        <td className="small text-muted">{lead.product}</td>
                        <td className="small fw-semibold">{formatCurrency(lead.budget)}</td>
                        <td>
                          <ScoreBadge score={lead.score} />
                        </td>
                        <td>
                          <StatusBadge status={lead.status} />
                        </td>
                        <td>
                          <Link to={`/leads/${lead.id}`} className="btn btn-sm btn-light border py-0 px-2">
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Recent Alerts Feed */}
        <div className="col-lg-5">
          <div className="card p-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 className="fw-bold mb-0">Live Action Alerts</h5>
                <span className="text-muted small">High-value triggers & missed follow-ups</span>
              </div>
              <Link to="/alerts" className="btn btn-sm btn-outline-secondary">
                All Alerts
              </Link>
            </div>

            {recentAlerts.length === 0 ? (
              <EmptyState title="All Caught Up!" message="No unread alerts requiring immediate attention." />
            ) : (
              <div className="alerts-feed">
                {recentAlerts.map((alert) => (
                  <div key={alert.id} className={`alert-item severity-${alert.severity} unread`}>
                    <div className="d-flex justify-content-between align-items-start mb-1">
                      <span className="badge bg-light text-dark border small fw-semibold" style={{ fontSize: '0.7rem' }}>
                        {alert.type.replace(/_/g, ' ')}
                      </span>
                      <button
                        className="btn btn-link btn-sm text-muted p-0 text-decoration-none"
                        onClick={() => handleMarkAlertRead(alert.id)}
                        title="Dismiss alert"
                        style={{ fontSize: '0.75rem' }}
                      >
                        ✓ Mark Read
                      </button>
                    </div>
                    <div className="small fw-semibold text-dark mb-1">{alert.leadName}</div>
                    <div className="text-muted small" style={{ fontSize: '0.78rem' }}>{alert.message}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
