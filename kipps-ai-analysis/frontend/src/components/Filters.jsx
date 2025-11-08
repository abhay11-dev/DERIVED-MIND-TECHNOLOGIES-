import React from 'react'

const Filters = ({ filters, onFilterChange, onReset }) => {
  const sentimentOptions = ['positive', 'neutral', 'negative']

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
      
      <div className="space-y-4">
        {/* Sentiment Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sentiment
          </label>
          <select
            className="input-field"
            value={filters.sentiment || ''}
            onChange={(e) => onFilterChange('sentiment', e.target.value)}
          >
            <option value="">All Sentiments</option>
            {sentimentOptions.map((option) => (
              <option key={option} value={option}>
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Minimum Score Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Minimum Score
          </label>
          <input
            type="number"
            className="input-field"
            placeholder="0-100"
            min="0"
            max="100"
            value={filters.min_score || ''}
            onChange={(e) => onFilterChange('min_score', e.target.value)}
          />
        </div>

        {/* Date From Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date From
          </label>
          <input
            type="date"
            className="input-field"
            value={filters.date_from || ''}
            onChange={(e) => onFilterChange('date_from', e.target.value)}
          />
        </div>

        {/* Date To Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date To
          </label>
          <input
            type="date"
            className="input-field"
            value={filters.date_to || ''}
            onChange={(e) => onFilterChange('date_to', e.target.value)}
          />
        </div>

        {/* Reset Button */}
        <button
          className="btn-secondary w-full"
          onClick={onReset}
        >
          Reset Filters
        </button>
      </div>
    </div>
  )
}

export default Filters