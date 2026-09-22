import React from 'react'

export default function ScoreBadge({ score, showLabel = false }) {
  const s = Number(score) || 0
  
  let bg = '#f1f5f9'
  let color = '#475569'
  let label = 'Low'

  if (s >= 70) {
    bg = 'rgba(239, 68, 68, 0.12)'
    color = '#dc2626'
    label = 'Hot Lead'
  } else if (s >= 40) {
    bg = 'rgba(245, 158, 11, 0.12)'
    color = '#d97706'
    label = 'Warm'
  } else {
    bg = 'rgba(100, 116, 139, 0.12)'
    color = '#64748b'
    label = 'Cold'
  }

  return (
    <div className="d-inline-flex align-items-center gap-1">
      <span 
        className="fw-bold px-2 py-1 rounded" 
        style={{ 
          backgroundColor: bg, 
          color: color, 
          fontSize: '0.85rem',
          minWidth: '38px',
          textAlign: 'center'
        }}
      >
        {s}
      </span>
      {showLabel && (
        <span className="small text-muted" style={{ fontSize: '0.75rem' }}>
          ({label})
        </span>
      )}
    </div>
  )
}
