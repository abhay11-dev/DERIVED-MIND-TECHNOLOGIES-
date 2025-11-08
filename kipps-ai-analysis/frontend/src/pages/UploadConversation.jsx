import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from '../api/axios'

const UploadConversation = () => {
  const navigate = useNavigate()
  const [jsonInput, setJsonInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const sampleJSON = {
    title: "Customer Support - Order Issue",
    messages: [
      {
        sender: "user",
        text: "Hello, I have a problem with my recent order",
        timestamp: "2024-01-15T10:00:00Z"
      },
      {
        sender: "agent",
        text: "I understand your concern. I'm here to help. Can you please provide your order number?",
        timestamp: "2024-01-15T10:00:30Z"
      },
      {
        sender: "user",
        text: "My order number is #12345",
        timestamp: "2024-01-15T10:01:00Z"
      },
      {
        sender: "agent",
        text: "Thank you! Let me check that for you. I can see your order was shipped yesterday and should arrive by tomorrow. Is there anything specific you need help with?",
        timestamp: "2024-01-15T10:02:00Z"
      },
      {
        sender: "user",
        text: "Perfect! That's all I needed to know. Thank you!",
        timestamp: "2024-01-15T10:02:30Z"
      },
      {
        sender: "agent",
        text: "You're welcome! Have a great day!",
        timestamp: "2024-01-15T10:03:00Z"
      }
    ]
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const data = JSON.parse(jsonInput)
      const response = await axios.post('/conversations/', data)
      setSuccess(true)
      setTimeout(() => {
        navigate(`/conversation/${response.data.id}`)
      }, 1500)
    } catch (err) {
      if (err.message.includes('JSON')) {
        setError('Invalid JSON format. Please check your input.')
      } else {
        setError(err.response?.data?.detail || 'Failed to upload conversation')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setJsonInput(event.target.result)
      }
      reader.readAsText(file)
    }
  }

  const loadSample = () => {
    setJsonInput(JSON.stringify(sampleJSON, null, 2))
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Upload Conversation</h1>
        <p className="text-gray-600 mt-2">
          Upload a conversation in JSON format for analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Upload Area */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="card">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Conversation JSON
            </label>
            <textarea
              className="input-field font-mono text-sm"
              rows="20"
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              placeholder='{"title": "...", "messages": [...]}'
              required
            />

            <div className="flex flex-col sm:flex-row gap-4 mt-6">
              <button
                type="submit"
                className="btn-primary flex-1"
                disabled={loading}
              >
                {loading ? 'Uploading...' : 'Upload Conversation'}
              </button>
              <label className="btn-secondary flex-1 text-center cursor-pointer">
                <input
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                Upload JSON File
              </label>
            </div>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {success && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  Conversation uploaded successfully! Redirecting...
                </p>
              </div>
            )}
          </form>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Sample Button */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Quick Start
            </h3>
            <button
              type="button"
              onClick={loadSample}
              className="btn-secondary w-full"
            >
              Load Sample JSON
            </button>
          </div>

          {/* Format Guide */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              JSON Format
            </h3>
            <div className="text-sm text-gray-600 space-y-3">
              <div>
                <p className="font-medium text-gray-900">Required fields:</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>messages (array)</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-gray-900">Optional fields:</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>title (string)</li>
                </ul>
              </div>
              <div>
                <p className="font-medium text-gray-900">Message structure:</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>sender: "user" or "agent"</li>
                  <li>text: message content</li>
                  <li>timestamp: ISO 8601 format</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UploadConversation