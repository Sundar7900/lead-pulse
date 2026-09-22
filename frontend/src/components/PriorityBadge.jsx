import React from 'react'

export default function PriorityBadge({ priority }) {
  const p = (priority || 'low').toLowerCase()
  
  const config = {
    high: { className: 'badge-high', label: 'High Priority', dotColor: '#ef4444' },
    medium: { className: 'badge-medium', label: 'Medium Priority', dotColor: '#f59e0b' },
    low: { className: 'badge-low', label: 'Low Priority', dotColor: '#64748b' }
  }

  const { className, label, dotColor } = config[p] || config.low

  return (
    <span className={`badge ${className} d-inline-flex align-items-center gap-1`} style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
      <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: dotColor }}></span>
      {label}
    </span>
  )
}
