import React from 'react'

const MessageBubble = ({ message }) => {
  const isAgent = message.sender === 'agent'

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className={`flex ${isAgent ? 'justify-start' : 'justify-end'} mb-4`}>
      <div
        className={`max-w-[80%] sm:max-w-[70%] rounded-lg px-4 py-3 ${
          isAgent
            ? 'bg-gray-100 text-gray-900'
            : 'bg-primary-600 text-white'
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium">
            {isAgent ? 'Agent' : 'User'}
          </span>
          <span className={`text-xs ${isAgent ? 'text-gray-500' : 'text-primary-100'}`}>
            {formatTime(message.timestamp)}
          </span>
        </div>
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.text}
        </p>
      </div>
    </div>
  )
}

export default MessageBubble