import React from 'react'

export default function StatsCard({ title, value, subtitle, icon, color = '#4f46e5', trend }) {
  return (
    <div className="stats-card h-100 position-relative overflow-hidden">
      <div className="d-flex justify-content-between align-items-start">
        <div>
          <h6 className="text-muted mb-2 text-uppercase" style={{ fontSize: '0.72rem', letterSpacing: '0.05em' }}>
            {title}
          </h6>
          <h3 className="mb-1 fw-bold" style={{ color: color }}>
            {value}
          </h3>
          {subtitle && (
            <p className="text-muted small mb-0 mt-1" style={{ fontSize: '0.8rem' }}>
              {subtitle}
            </p>
          )}
        </div>
        {icon && (
          <div 
            className="d-flex align-items-center justify-content-center rounded-3 p-2" 
            style={{ 
              backgroundColor: `${color}15`, 
              color: color,
              minWidth: '40px',
              minHeight: '40px'
            }}
          >
            {icon}
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 pt-2 border-top d-flex align-items-center gap-1 small text-muted">
          {trend}
        </div>
      )}
    </div>
  )
}
