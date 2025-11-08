# Kipps.AI - Post-Conversation Analysis System

A complete full-stack solution for analyzing customer support conversations using Django REST Framework and React.

## Features

- 📊 **Automated Analysis**: 10+ metrics including clarity, relevance, accuracy, empathy, sentiment
- 🎯 **Smart Detection**: Fallback counting, resolution detection, escalation prediction
- 📈 **Interactive Dashboard**: Visualize conversation metrics with charts and badges
- 🔄 **Scheduled Tasks**: Daily auto-analysis of new conversations using Celery Beat
- 🎨 **Responsive UI**: Mobile-friendly interface built with React and Tailwind CSS
- 🐳 **Docker Ready**: Complete containerization for easy deployment

## Architecture

### Backend (Django)
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Task Queue**: Celery + Redis
- **Analysis**: Rule-based heuristics + TextBlob/VADER sentiment analysis

### Frontend (React)
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Charts**: Chart.js + React-ChartJS-2
- **API Client**: Axios

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- Redis (for Celery)

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd kipps-ai-analysis
```

2. **Set up environment variables**
```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your settings

# Frontend
cd ../frontend
cp .env.example .env
# Edit .env if needed
```

3. **Start all services**
```bash
cd backend
docker-compose up --build
```

4. **Access the application**
- Backend API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- Frontend: http://localhost:5173/

### Option 2: Local Development

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
python -m textblob.download_corpora
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env for local development (use SQLite)
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Start Redis** (in a separate terminal)
```bash
redis-server
```

7. **Start Celery worker** (in a separate terminal)
```bash
celery -A config worker -l info
```

8. **Start Celery Beat** (in a separate terminal)
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

9. **Run development server**
```bash
python manage.py runserver
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Set up environment**
```bash
cp .env.example .env
# Default: VITE_API_BASE_URL=http://localhost:8000/api
```

3. **Start development server**
```bash
npm run dev
```

4. **Access frontend**
```
http://localhost:5173
```

## API Documentation

### Endpoints

#### Conversations

**Create Conversation**
```http
POST /api/conversations/
Content-Type: application/json

{
  "title": "Customer Support Issue",
  "messages": [
    {
      "sender": "user",
      "text": "I need help with my order",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "sender": "agent",
      "text": "I'd be happy to help you with that!",
      "timestamp": "2024-01-15T10:00:30Z"
    }
  ]
}
```

**List Conversations**
```http
GET /api/conversations/?page=1
```

**Get Conversation Details**
```http
GET /api/conversations/{id}/
```

**Analyze Conversation**
```http
POST /api/conversations/{id}/analyze/
```

#### Analysis

**List All Analyses**
```http
GET /api/analysis/?sentiment=positive&min_score=80&date_from=2024-01-01
```

### Sample cURL Commands
```bash
# Create a conversation
curl -X POST http://localhost:8000/api/conversations/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Conversation",
    "messages": [
      {
        "sender": "user",
        "text": "Hello, I need help",
        "timestamp": "2024-01-15T10:00:00Z"
      },
      {
        "sender": "agent",
        "text": "I understand. How can I assist you?",
        "timestamp": "2024-01-15T10:00:30Z"
      }
    ]
  }'

# Analyze a conversation
curl -X POST http://localhost:8000/api/conversations/1/analyze/

# Get analysis results
curl http://localhost:8000/api/analysis/
```

## Analysis Metrics

The system computes the following metrics:

1. **Clarity Score** (0-100): Measures message clarity based on sentence length and jargon usage
2. **Relevance Score** (0-100): Keyword overlap between user questions and agent responses
3. **Accuracy Score** (0-100): Confidence indicators vs. uncertain language
4. **Completeness Score** (0-100): Whether all user questions were addressed
5. **Empathy Score** (0-100): Presence of empathetic phrases
6. **Fallback Count**: Number of "I don't know" type responses
7. **Sentiment**: positive/neutral/negative (using VADER)
8. **Resolution**: Boolean indicating if issue was resolved
9. **Escalation Needed**: Whether conversation should be escalated
10. **Avg Response Time**: Average agent response time in seconds
11. **Overall Score**: Weighted average of key metrics

## Scheduled Tasks

The system runs a daily task (2 AM UTC) to automatically analyze all unanalyzed conversations.

To manually trigger the task:
```bash
# In Django shell
python manage.py shell
>>> from conversations.tasks import analyze_unanalyzed_conversations
>>> analyze_unanalyzed_conversations.delay()
```

## Running Tests
```bash
cd backend
python manage.py test conversations

# Or with pytest
pytest
```

## Project Structure
```
kipps-ai-analysis/
├── backend/
│   ├── config/              # Django settings
│   ├── conversations/       # Main app
│   │   ├── analysis.py     # Analysis logic
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── serializers.py  # DRF serializers
│   │   ├── tasks.py        # Celery tasks
│   │   └── tests.py        # Unit tests
│   ├── requirements.txt
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── api/            # API client
│   │   └── styles/         # CSS files
│   ├── package.json
│   └── Dockerfile
└── README.md
```

## Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_ENGINE=django.db.backends.sqlite3
CELERY_BROKER_URL=redis://redis:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Deployment

### Production Checklist

1. Set `DEBUG=False` in backend .env
2. Change `SECRET_KEY` to a secure random string
3. Update `ALLOWED_HOSTS` with your domain
4. Use PostgreSQL instead of SQLite
5. Set up proper CORS_ALLOWED_ORIGINS
6. Use environment variables for all secrets
7. Set up proper logging
8. Configure Nginx/Apache as reverse proxy
9. Use Gunicorn for WSGI server
10. Set up SSL certificates

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

## Troubleshooting

### Celery not running
- Ensure Redis is running: `redis-cli ping`
- Check Celery worker logs: `docker-compose logs celery`

### CORS errors
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check that requests include proper headers

### Database errors
- Run migrations: `python manage.py migrate`
- Check database connectivity

### Frontend can't connect to API
- Verify `VITE_API_BASE_URL` in frontend .env
- Ensure backend is running on the specified port

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API examples in postman_collection.json