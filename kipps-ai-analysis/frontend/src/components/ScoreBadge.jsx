import React from 'react'

const ScoreBadge = ({ score, label, size = 'md' }) => {
  const getColor = (score) => {
    if (score >= 80) return 'bg-green-100 text-green-800 border-green-200'
    if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-red-100 text-red-800 border-red-200'
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2',
  }

  return (
    <div
      className={`inline-flex flex-col items-center rounded-lg border-2 ${getColor(
        score
      )} ${sizeClasses[size]}`}
    >
      <span className="font-bold text-lg">{score.toFixed(0)}</span>
      {label && <span className="text-xs font-medium">{label}</span>}
    </div>
  )
}

export default ScoreBadge