# Kipps.AI Demo Script

## Overview
This demo walks through the complete Kipps.AI Post-Conversation Analysis system, showcasing its key features and capabilities.

## Architecture Quick Overview

### Backend (Django)
- **API Layer**: Django REST Framework with ViewSets
- **Analysis Engine**: Modular analyzer using TextBlob/VADER for sentiment
- **Task Queue**: Celery + Redis for scheduled analysis
- **Database**: PostgreSQL (prod) / SQLite (dev)

### Frontend (React)
- **UI Framework**: React 18 with Tailwind CSS
- **Routing**: React Router for SPA navigation
- **Data Visualization**: Chart.js for metrics display
- **API Client**: Axios with interceptors

## Demo Flow

### 1. Starting the Application
```bash
# Terminal 1: Start backend services
cd backend
docker-compose up

# Terminal 2: Start frontend (if not using Docker)
cd frontend
npm run dev
```

**Access Points:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

### 2. Dashboard Overview

Navigate to http://localhost:5173

**Highlight:**
- Clean, responsive interface
- Conversation cards showing analysis status
- Quick access to upload and reports
- Mobile-friendly navigation drawer

### 3. Upload a Conversation

Click "Upload" in the navbar

**Demo Steps:**
1. Click "Load Sample JSON" to populate the form
2. Show the JSON structure:
   - Title field (optional)
   - Messages array with sender, text, timestamp
3. Click "Upload Conversation"
4. Automatic redirect to conversation detail page

**Sample JSON:**
```json
{
  "title": "Order Tracking Issue",
  "messages": [
    {
      "sender": "user",
      "text": "Hi, I can't track my order #12345",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "sender": "agent",
      "text": "I understand your concern. Let me help you with that right away.",
      "timestamp": "2024-01-15T10:00:30Z"
    },
    {
      "sender": "user",
      "text": "Thank you!",
      "timestamp": "2024-01-15T10:01:00Z"
    },
    {
      "sender": "agent",
      "text": "I've checked your order. It shipped yesterday and will arrive tomorrow. You can track it here: [link]",
      "timestamp": "2024-01-15T10:02:00Z"
    },
    {
      "sender": "user",
      "text": "Perfect! That's exactly what I needed. Thanks for the quick help!",
      "timestamp": "2024-01-15T10:02:30Z"
    }
  ]
}
```

### 4. Conversation Detail Page

After upload, you'll see:
- All messages in chat bubble format
- User messages on right (blue)
- Agent messages on left (gray)
- Timestamps for each message

**Highlight:**
- Clean message display
- Scrollable conversation history
- "Analyze Conversation" button

### 5. Run Analysis

Click "Analyze Conversation"

**What Happens:**
1. API call to `/api/conversations/{id}/analyze/`
2. Backend runs ConversationAnalyzer
3. Computes 10+ metrics in real-time
4. Saves results to database
5. UI updates with analysis results

**Analysis Output:**
- **Overall Score**: Weighted average (e.g., 87/100)
- **Sentiment Badge**: Positive/Neutral/Negative
- **Status Badges**: Resolved, Escalation Needed
- **Radar Chart**: Visual breakdown of 5 key metrics
- **Progress Bars**: Detailed scores for all metrics
- **Additional Insights**: Fallback count, response time, etc.

### 6. Understanding the Metrics

**Clarity Score (0-100)**
- Measures sentence length and jargon usage
- Shorter sentences = clearer communication
- Less technical jargon = higher score

**Relevance Score (0-100)**
- Keyword overlap between questions and answers
- Higher overlap = more relevant responses

**Accuracy Score (0-100)**
- Confidence indicators vs. uncertain language
- "Definitely" vs "Maybe" affects score

**Completeness Score (0-100)**
- Were all user questions addressed?
- Response ratio to user questions

**Empathy Score (0-100)**
- Detects empathetic phrases
- "I understand", "I apologize", etc.

**Fallback Count**
- Times agent said "I don't know"
- "Can't help", "Sorry I don't have that"

**Sentiment Analysis**
- Uses VADER sentiment analyzer
- Positive/Neutral/Negative classification

**Resolution Detection**
- Looks for resolution keywords
- "Resolved", "Fixed", "Thank you for helping"

**Escalation Detection**
- User asks for human agent
- Negative sentiment + fallbacks
- Excessive fallback count

**Response Time**
- Average seconds between user question and agent response
- Computed from message timestamps

### 7. Reports Page

Navigate to "Reports" in navbar

**Features:**
- **Filterable List**: All analyses in table format
- **Filters Sidebar**:
  - Sentiment filter
  - Minimum score threshold
  - Date range (from/to)
- **Sortable Columns**
- **Quick Actions**: "View Details" links
- **Pagination**: For large datasets

**Demo Steps:**
1. Show full list of analyses
2. Apply sentiment filter (e.g., "Positive only")
3. Set minimum score (e.g., 80)
4. Show results update in real-time
5. Click "View Details" to navigate back to conversation

### 8. Scheduled Analysis (Celery Beat)

**Background Process:**
- Runs daily at 2 AM UTC
- Automatically analyzes unanalyzed conversations
- No manual intervention required

**Check Celery Status:**
```bash
# View Celery logs
docker-compose logs celery

# View Celery Beat schedule
docker-compose logs celery-beat
```

**Manual Trigger:**
```bash
# Django shell
python manage.py shell
>>> from conversations.tasks import analyze_unanalyzed_conversations
>>> result = analyze_unanalyzed_conversations.delay()
>>> result.get()
```

### 9. API Testing

**Using cURL:**
```bash
# List conversations
curl http://localhost:8000/api/conversations/

# Get specific conversation
curl http://localhost:8000/api/conversations/1/

# Analyze conversation
curl -X POST http://localhost:8000/api/conversations/1/analyze/

# List analyses with filters
curl "http://localhost:8000/api/analysis/?sentiment=positive&min_score=80"
```

**Using Django Admin:**
1. Navigate to http://localhost:8000/admin
2. Login with superuser credentials
3. View/edit Conversations, Messages, Analyses
4. Check Celery Beat periodic tasks

### 10. Mobile Responsiveness

**Demo on Different Devices:**
1. Desktop: Full layout with sidebar
2. Tablet: Adjusted columns
3. Mobile: 
   - Hamburger menu for navigation
   - Stacked cards
   - Touch-friendly buttons
   - Horizontal scroll for tables

**Test in Chrome DevTools:**
- Toggle device toolbar (Ctrl+Shift+M)
- Switch between iPhone, iPad, Desktop views
- Show responsive breakpoints working

## Key Technical Highlights

### Backend
- **Modular Design**: Easy to swap analysis logic
- **RESTful API**: Standard HTTP methods
- **Async Tasks**: Celery for background processing
- **Comprehensive Tests**: Unit tests for all analysis functions
- **Docker Ready**: Complete containerization

### Frontend
- **Component Reusability**: ConversationCard, MessageBubble, etc.
- **State Management**: React hooks for local state
- **API Integration**: Axios with centralized config
- **Responsive Design**: Tailwind CSS breakpoints
- **Accessibility**: Semantic HTML, ARIA labels

### Analysis Engine
- **Rule-Based Heuristics**: Fast, interpretable results
- **ML-Lite Approach**: TextBlob/VADER for sentiment
- **Extensible**: Easy to add new metrics
- **Well-Documented**: Clear comments and docstrings

## Production Considerations

**Discussed in Demo:**
1. Environment variables for secrets
2. PostgreSQL for production database
3. Redis for task queue
4. Gunicorn for WSGI
5. Nginx for reverse proxy
6. SSL/TLS certificates
7. Logging and monitoring
8. Backup strategies
9. Scaling Celery workers
10. CDN for static files

## Demo Conclusion

**Summary:**
- Complete full-stack solution
- 10+ analysis metrics
- Automated scheduled tasks
- Interactive, responsive UI
- Production-ready architecture
- Docker containerization
- Comprehensive documentation

**Next Steps:**
- Add more sophisticated ML models
- Implement user authentication
- Add conversation search
- Export reports to PDF
- Real-time analysis via WebSockets
- Multi-language support