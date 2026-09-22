import React, { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { apiService } from '../services/api'
import PriorityBadge from '../components/PriorityBadge'
import ScoreBadge from '../components/ScoreBadge'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import AddLeadModal from '../components/AddLeadModal'

export default function Leads() {
  const [searchParams, setSearchParams] = useSearchParams()
  const initialPriority = searchParams.get('priority') || ''

  const [leads, setLeads] = useState([])
  const [pagination, setPagination] = useState({ page: 1, perPage: 15, total: 0, totalPages: 1 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Filter states
  const [search, setSearch] = useState('')
  const [priority, setPriority] = useState(initialPriority)
  const [status, setStatus] = useState('')
  const [assignedTo, setAssignedTo] = useState('')
  const [product, setProduct] = useState('')
  const [sortBy, setSortBy] = useState('createdAt')
  const [sortOrder, setSortOrder] = useState('desc')

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)

  const fetchLeads = async (page = 1) => {
    try {
      setLoading(true)
      setError(null)
      const params = {
        page,
        per_page: pagination.perPage,
        sortBy,
        sortOrder
      }

      if (search.trim()) params.search = search.trim()
      if (priority) params.priority = priority
      if (status) params.status = status
      if (assignedTo) params.assignedTo = assignedTo
      if (product) params.product = product

      const res = await apiService.getLeads(params)
      if (res.success && res.data) {
        setLeads(res.data.leads || [])
        if (res.data.pagination) {
          setPagination(res.data.pagination)
        }
      }
    } catch (err) {
      console.error('Failed to fetch leads:', err)
      setError(err.response?.data?.message || err.message || 'Error connecting to API')
    } finally {
      setLoading(false)
    }
  }

  // Refetch when filters change
  useEffect(() => {
    fetchLeads(1)
  }, [priority, status, assignedTo, product, sortBy, sortOrder])

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    fetchLeads(1)
  }

  const handleResetFilters = () => {
    setSearch('')
    setPriority('')
    setStatus('')
    setAssignedTo('')
    setProduct('')
    setSearchParams({})
  }

  const handleDeleteLead = async (id, name) => {
    if (window.confirm(`Are you sure you want to delete lead "${name}"?`)) {
      try {
        await apiService.deleteLead(id)
        fetchLeads(pagination.page)
      } catch (err) {
        alert('Failed to delete lead: ' + err.message)
      }
    }
  }

  const formatCurrency = (val) => {
    if (!val && val !== 0) return '₹0'
    return '₹' + Number(val).toLocaleString('en-IN')
  }

  const formatDate = (val) => {
    if (!val) return 'Never'
    try {
      const d = new Date(val)
      return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })
    } catch {
      return String(val).substring(0, 10)
    }
  }

  return (
    <div className="leads-page">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Sales Leads</h2>
          <p className="text-muted mb-0">Manage pipeline candidates, track scoring, and assign reps</p>
        </div>
        <button 
          className="btn btn-primary d-inline-flex align-items-center gap-2 shadow-sm"
          onClick={() => setIsModalOpen(true)}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>+ Add New Lead</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="card p-3 mb-4 border-0 shadow-sm" style={{ borderRadius: '12px' }}>
        <form onSubmit={handleSearchSubmit} className="row g-2 align-items-center">
          <div className="col-lg-3 col-md-6">
            <div className="input-group">
              <span className="input-group-text bg-light border-end-0">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
              </span>
              <input
                type="text"
                className="form-control border-start-0 ps-0"
                placeholder="Search name, email, phone..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
          </div>

          <div className="col-lg-2 col-md-3 col-6">
            <select
              className="form-select"
              value={priority}
              onChange={(e) => {
                setPriority(e.target.value)
                setSearchParams(e.target.value ? { priority: e.target.value } : {})
              }}
            >
              <option value="">All Priorities</option>
              <option value="high">High Priority (70+)</option>
              <option value="medium">Medium Priority (40-69)</option>
              <option value="low">Low Priority (&lt;40)</option>
            </select>
          </div>

          <div className="col-lg-2 col-md-3 col-6">
            <select
              className="form-select"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="">All Stages</option>
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="interested">Interested</option>
              <option value="demo_scheduled">Demo Scheduled</option>
              <option value="negotiation">Negotiation</option>
              <option value="converted">Converted</option>
              <option value="lost">Lost</option>
            </select>
          </div>

          <div className="col-lg-2 col-md-4 col-6">
            <select
              className="form-select"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
            >
              <option value="">All Courses</option>
              <option value="Data Science">Data Science</option>
              <option value="Full Stack Development">Full Stack Development</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Cloud Computing">Cloud Computing</option>
              <option value="Machine Learning">Machine Learning</option>
              <option value="Cybersecurity">Cybersecurity</option>
              <option value="DevOps Engineering">DevOps Engineering</option>
              <option value="Business Analytics">Business Analytics</option>
            </select>
          </div>

          <div className="col-lg-2 col-md-4 col-6">
            <select
              className="form-select"
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
            >
              <option value="">All Sales Reps</option>
              <option value="Priya Sharma">Priya Sharma</option>
              <option value="Rahul Verma">Rahul Verma</option>
              <option value="Ananya Iyer">Ananya Iyer</option>
              <option value="Vikram Patel">Vikram Patel</option>
              <option value="Sneha Reddy">Sneha Reddy</option>
            </select>
          </div>

          <div className="col-lg-1 col-md-4 text-end">
            <button
              type="button"
              className="btn btn-outline-secondary w-100"
              onClick={handleResetFilters}
              title="Reset all filters"
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* Main Leads Table */}
      <div className="card shadow-sm border-0 overflow-hidden" style={{ borderRadius: '12px' }}>
        {loading ? (
          <LoadingSpinner message="Fetching leads..." />
        ) : error ? (
          <div className="p-4 text-center text-danger">
            <p className="mb-2">{error}</p>
            <button className="btn btn-sm btn-outline-primary" onClick={() => fetchLeads(pagination.page)}>
              Retry
            </button>
          </div>
        ) : leads.length === 0 ? (
          <EmptyState
            title="No Leads Found"
            message="No leads matched your search and filter criteria. Try adjusting your query."
            action={
              <button className="btn btn-sm btn-primary" onClick={handleResetFilters}>
                Clear Filters
              </button>
            }
          />
        ) : (
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th style={{ width: '22%' }}>Lead Candidate</th>
                  <th>Product</th>
                  <th>Budget</th>
                  <th>Score</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Assigned BD</th>
                  <th>Last Activity</th>
                  <th className="text-end pe-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead) => {
                  const leadId = lead._id || lead.id
                  return (
                    <tr key={leadId}>
                      <td>
                        <Link to={`/leads/${leadId}`} className="text-decoration-none">
                          <div className="fw-bold text-dark">{lead.name}</div>
                          <div className="text-muted small" style={{ fontSize: '0.75rem' }}>
                            {lead.email} {lead.location ? `• ${lead.location}` : ''}
                          </div>
                        </Link>
                      </td>
                      <td className="small text-muted">{lead.product}</td>
                      <td className="small fw-semibold">{formatCurrency(lead.budget)}</td>
                      <td>
                        <ScoreBadge score={lead.leadScore} />
                      </td>
                      <td>
                        <PriorityBadge priority={lead.priority} />
                      </td>
                      <td>
                        <StatusBadge status={lead.status} />
                      </td>
                      <td>
                        <div className="small fw-medium text-dark">{lead.assignedToName || 'Unassigned'}</div>
                        <div className="text-muted" style={{ fontSize: '0.7rem' }}>
                          Source: {lead.source || 'direct'}
                        </div>
                      </td>
                      <td className="small text-muted">{formatDate(lead.lastActivityAt)}</td>
                      <td className="text-end pe-3">
                        <div className="btn-group btn-group-sm">
                          <Link to={`/leads/${leadId}`} className="btn btn-light border py-1 px-2" title="View details">
                            View
                          </Link>
                          <button
                            type="button"
                            className="btn btn-light border py-1 px-2 text-danger"
                            onClick={() => handleDeleteLead(leadId, lead.name)}
                            title="Delete lead"
                          >
                            ×
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {pagination.total > 0 && (
          <div className="card-footer bg-white border-0 py-3 px-4 d-flex justify-content-between align-items-center">
            <span className="small text-muted">
              Showing <strong>{(pagination.page - 1) * pagination.perPage + 1}</strong> to{' '}
              <strong>{Math.min(pagination.page * pagination.perPage, pagination.total)}</strong> of{' '}
              <strong>{pagination.total}</strong> leads
            </span>

            <div className="d-flex gap-1">
              <button
                className="btn btn-sm btn-outline-secondary"
                disabled={pagination.page <= 1}
                onClick={() => fetchLeads(pagination.page - 1)}
              >
                Previous
              </button>
              <button className="btn btn-sm btn-light border fw-bold px-3">
                {pagination.page} / {pagination.totalPages || 1}
              </button>
              <button
                className="btn btn-sm btn-outline-secondary"
                disabled={pagination.page >= (pagination.totalPages || 1)}
                onClick={() => fetchLeads(pagination.page + 1)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add Lead Modal */}
      <AddLeadModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onLeadCreated={() => {
          fetchLeads(1)
        }}
      />
    </div>
  )
}
