import React from 'react'

export default function EmptyState({ title = 'No items found', message = 'No data available to display.', action, icon }) {
  return (
    <div className="empty-state py-5 text-center">
      <div className="mb-3 text-muted" style={{ opacity: 0.6 }}>
        {icon || (
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        )}
      </div>
      <h5 className="fw-semibold mb-2">{title}</h5>
      <p className="text-muted small mx-auto mb-3" style={{ maxWidth: '400px' }}>{message}</p>
      {action && <div>{action}</div>}
    </div>
  )
}
