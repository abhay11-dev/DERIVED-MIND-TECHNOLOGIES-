import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from '../api/axios'
import MessageBubble from '../components/MessageBubble'
import ScoreBadge from '../components/ScoreBadge'
import ProgressBar from '../components/ProgressBar'
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js'
import { Radar } from 'react-chartjs-2'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const ConversationDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [conversation, setConversation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchConversation()
  }, [id])

  const fetchConversation = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/conversations/${id}/`)
      setConversation(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load conversation')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true)
      await axios.post(`/conversations/${id}/analyze/`)
      await fetchConversation()
    } catch (err) {
      setError('Failed to analyze conversation')
      console.error(err)
    } finally {
      setAnalyzing(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !conversation) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || 'Conversation not found'}</p>
        <button
          onClick={() => navigate('/')}
          className="btn-primary mt-4"
        >
          Back to Dashboard
        </button>
      </div>
    )
  }

  const { title, created_at, messages, analysis, has_analysis } = conversation

  const radarData = analysis ? {
    labels: ['Clarity', 'Relevance', 'Accuracy', 'Completeness', 'Empathy'],
    datasets: [
      {
        label: 'Scores',
        data: [
          analysis.clarity_score,
          analysis.relevance_score,
          analysis.accuracy_score,
          analysis.completeness_score,
          analysis.empathy_score,
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
      },
    ],
  } : null

  const radarOptions = {
    scales: {
      r: {
        min: 0,
        max: 100,
        ticks: {
          stepSize: 20,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="text-primary-600 hover:text-primary-700 mb-4 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </button>
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {title || `Conversation #${id}`}
            </h1>
            <p className="text-gray-600 mt-2">
              {new Date(created_at).toLocaleString()}
            </p>
          </div>
          {!has_analysis && (
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="btn-primary whitespace-nowrap"
            >
              {analyzing ? 'Analyzing...' : 'Analyze Conversation'}
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Messages Section */}
        <div className="lg:col-span-2">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Messages ({messages.length})
            </h2>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
              {messages.map((message) => (
                <MessageBubble key={message.id} message={message} />
              ))}
            </div>
          </div>
        </div>

        {/* Analysis Section */}
        <div className="space-y-6">
          {has_analysis && analysis ? (
            <>
              {/* Overall Score */}
              <div className="card text-center">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Overall Score
                </h3>
                <ScoreBadge
                  score={analysis.overall_score}
                  label=""
                  size="lg"
                />
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex justify-center gap-2 flex-wrap">
                    <span
                      className={`badge ${
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
                      <span className="badge bg-blue-100 text-blue-800">
                        Resolved
                      </span>
                    )}
                    {analysis.escalation_needed && (
                      <span className="badge bg-orange-100 text-orange-800">
                        Needs Escalation
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Radar Chart */}
              <div className="card">

             <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Score Breakdown
                </h3>
                <div className="h-64">
                  <Radar data={radarData} options={radarOptions} />
                </div>
              </div>

              {/* Detailed Scores */}
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Detailed Metrics
                </h3>
                <div className="space-y-4">
                  <ProgressBar
                    value={analysis.clarity_score}
                    label="Clarity"
                  />
                  <ProgressBar
                    value={analysis.relevance_score}
                    label="Relevance"
                  />
                  <ProgressBar
                    value={analysis.accuracy_score}
                    label="Accuracy"
                  />
                  <ProgressBar
                    value={analysis.completeness_score}
                    label="Completeness"
                  />
                  <ProgressBar
                    value={analysis.empathy_score}
                    label="Empathy"
                  />
                </div>
              </div>

              {/* Additional Metrics */}
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Additional Insights
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Fallback Count</span>
                    <span className="font-semibold text-gray-900">
                      {analysis.fallback_count}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Avg Response Time</span>
                    <span className="font-semibold text-gray-900">
                      {analysis.avg_response_time_seconds.toFixed(1)}s
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Resolution Status</span>
                    <span className="font-semibold text-gray-900">
                      {analysis.resolution ? 'Resolved' : 'Not Resolved'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Escalation</span>
                    <span className="font-semibold text-gray-900">
                      {analysis.escalation_needed ? 'Needed' : 'Not Needed'}
                    </span>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="card text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No Analysis Yet
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Click "Analyze Conversation" to generate insights
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ConversationDetail