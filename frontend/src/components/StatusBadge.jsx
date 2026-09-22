import React from 'react'

export default function StatusBadge({ status }) {
  const st = (status || 'new').toLowerCase().replace(' ', '_')

  const statusMap = {
    new: { label: 'New', className: 'badge-new' },
    contacted: { label: 'Contacted', className: 'badge-contacted' },
    interested: { label: 'Interested', className: 'badge-interested' },
    demo_scheduled: { label: 'Demo Scheduled', className: 'badge-demo-scheduled' },
    negotiation: { label: 'Negotiation', className: 'badge-negotiation' },
    converted: { label: 'Converted', className: 'badge-converted' },
    lost: { label: 'Lost', className: 'badge-lost' }
  }

  const item = statusMap[st] || { label: status || 'Unknown', className: 'badge-new' }

  return (
    <span 
      className={`badge ${item.className}`} 
      style={{ 
        fontWeight: 600, 
        padding: '0.4rem 0.65rem',
        borderRadius: '6px',
        fontSize: '0.78rem'
      }}
    >
      {item.label}
    </span>
  )
}
