import React from 'react'
import { Link } from 'react-router-dom'
import ScoreBadge from './ScoreBadge'

const ConversationCard = ({ conversation }) => {
  const { id, title, created_at, messages, analysis, has_analysis } = conversation

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Link to={`/conversation/${id}`} className="block">
      <div className="card hover:shadow-xl cursor-pointer">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 truncate">
              {title || `Conversation #${id}`}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {formatDate(created_at)}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              {messages?.length || 0} messages
            </p>
          </div>

          <div className="flex flex-col items-start sm:items-end gap-2">
            {has_analysis ? (
              <>
                <ScoreBadge
                  score={analysis.overall_score}
                  label="Overall"
                  size="lg"
                />
                <div className="flex gap-2 flex-wrap">
                  <span
                    className={`badge text-xs ${
                      analysis.sentiment === 'positive'
                        ? 'bg-green-100 text-green-800'
                        : analysis.sentiment === 'negative'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {analysis.sentiment}
                  </span>
                  {analysis.resolution && (
                    <span className="badge bg-blue-100 text-blue-800 text-xs">
                      Resolved
                    </span>
                  )}
                  {analysis.escalation_needed && (
                    <span className="badge bg-orange-100 text-orange-800 text-xs">
                      Escalation
                    </span>
                  )}
                </div>
              </>
            ) : (
              <span className="badge bg-yellow-100 text-yellow-800 text-xs">
                Not Analyzed
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}

export default ConversationCard