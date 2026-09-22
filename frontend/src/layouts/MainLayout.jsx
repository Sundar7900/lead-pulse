import React, { useState, useEffect } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { apiService } from '../services/api'
import './MainLayout.css'

function MainLayout() {
  const [unreadAlerts, setUnreadAlerts] = useState(0)
  const [dbStatus, setDbStatus] = useState({ connected: false, type: 'checking...' })
  const [seeding, setSeeding] = useState(false)

  const fetchStatus = async () => {
    try {
      const res = await apiService.getStatus()
      if (res.success && res.data) {
        setDbStatus(res.data.database)
        setUnreadAlerts(res.data.counts.alerts || 0)
      }
    } catch (e) {
      console.warn('Backend status check failed:', e)
    }
  }

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleSeed = async () => {
    if (window.confirm('Reset database with 75 realistic mock leads, activities, and alerts?')) {
      setSeeding(true)
      try {
        await apiService.post('/api/seed', {})
        window.location.reload()
      } catch (err) {
        alert('Seeding error: ' + (err.message || 'Failed'))
      } finally {
        setSeeding(false)
      }
    }
  }

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand d-flex align-items-center justify-content-between">
          <h2>Lead<span>Pulse</span></h2>
          <span className="badge bg-primary-subtle text-primary" style={{ fontSize: '0.65rem' }}>MVP</span>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '12px' }}>
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            Dashboard
          </NavLink>
          <NavLink to="/leads" className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '12px' }}>
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            Leads
          </NavLink>
          <NavLink to="/alerts" className={({ isActive }) => `sidebar-link d-flex justify-content-between align-items-center ${isActive ? 'active' : ''}`}>
            <div className="d-flex align-items-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '12px' }}>
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              Alerts
            </div>
            {unreadAlerts > 0 && (
              <span className="badge rounded-pill bg-danger text-white px-2 py-1" style={{ fontSize: '0.72rem' }}>
                {unreadAlerts}
              </span>
            )}
          </NavLink>
        </nav>

        {/* System Info Footnote */}
        <div className="p-3 mx-3 mt-auto rounded-3" style={{ background: 'rgba(255,255,255,0.06)', position: 'absolute', bottom: '20px', width: 'calc(260px - 32px)' }}>
          <div className="d-flex align-items-center gap-2 mb-2">
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: dbStatus.connected ? '#10b981' : '#ef4444' }}></span>
            <span className="small text-white-50" style={{ fontSize: '0.75rem' }}>
              DB: <strong className="text-white">{dbStatus.type}</strong>
            </span>
          </div>
          <button 
            className="btn btn-outline-light btn-sm w-100 py-1" 
            style={{ fontSize: '0.72rem' }}
            onClick={handleSeed}
            disabled={seeding}
          >
            {seeding ? 'Seeding...' : '⚡ Reset Mock Data'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {/* Top Navbar */}
        <header className="top-navbar">
          <div className="navbar-title">
            <h5 className="mb-0 fw-bold text-dark">LeadPulse Intelligence</h5>
            <span className="text-muted small">Real-time Lead Scoring & Priority Alert Engine</span>
          </div>
          <div className="d-flex align-items-center gap-3">
            <span className="badge bg-light text-secondary border px-3 py-2">
              🚀 Fast Scoring Rule Engine
            </span>
            <div className="d-flex align-items-center gap-2">
              <div 
                className="rounded-circle d-flex align-items-center justify-content-center bg-primary text-white fw-bold" 
                style={{ width: '36px', height: '36px', fontSize: '0.85rem' }}
              >
                AU
              </div>
              <div>
                <div className="small fw-semibold">Sales Admin</div>
                <div className="text-muted" style={{ fontSize: '0.7rem' }}>admin@leadpulse.com</div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default MainLayout
