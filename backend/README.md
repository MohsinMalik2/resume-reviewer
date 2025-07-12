# Auto Screener Agent - Backend API

AI-Powered Resume Screening & Rejection Automation Backend built with FastAPI, Firebase, and Google Gemini AI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Firebase Project
- Google AI API Key (for Gemini)

### Installation

1. **Clone and navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Setup**
```bash
cp .env.example .env
```

Edit `.env` file with your credentials:
- Firebase service account credentials
- Google AI API key
- JWT secret key
- CORS origins

### Firebase Setup

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project
   - Enable Firestore Database

2. **Generate Service Account**
   - Go to Project Settings > Service Accounts
   - Generate new private key
   - Download JSON file

3. **Configure Environment**
   - Extract values from JSON file to `.env`
   - Set up Firestore security rules

### Google AI Setup

1. **Get API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create new API key
   - Add to `.env` as `GOOGLE_AI_API_KEY`

### Run the Server

```bash
# Development
python run.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   └── resume.py
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   └── resumes.py
│   └── services/            # Business logic
│       ├── auth_service.py
│       ├── firebase_service.py
│       ├── ai_service.py
│       └── file_service.py
├── requirements.txt
├── .env.example
├── run.py
└── README.md
```

## 🔐 Authentication

The API uses JWT tokens for authentication:
- **Access Token**: 24 hours (configurable)
- **Refresh Token**: 30 days (configurable)
- **Secure**: Bcrypt password hashing

## 🤖 AI Processing

**Resume Analysis**:
- Text extraction from PDF/DOC/DOCX
- Gemini AI analysis against job description
- Scoring (0-100) based on fit
- Skill extraction and experience parsing

**Email Generation**:
- Personalized rejection emails
- Professional tone and formatting
- Contextual feedback based on analysis

## 🗄️ Database Schema

**Users Collection**:
```json
{
  "id": "string",
  "email": "string",
  "firstName": "string",
  "lastName": "string",
  "company": "string",
  "hashed_password": "string",
  "createdAt": "timestamp"
}
```

**Jobs Collection**:
```json
{
  "id": "string",
  "userId": "string",
  "jobDescription": "string",
  "totalProcessed": "number",
  "shortlistedCount": "number",
  "rejectedCount": "number",
  "averageScore": "number",
  "processingTime": "number",
  "createdAt": "timestamp"
}
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t auto-screener-backend .

# Run container
docker run -p 3001:3001 --env-file .env auto-screener-backend
```

### Cloud Deployment
- **Google Cloud Run**
- **AWS Lambda** (with Mangum)
- **Heroku**
- **DigitalOcean App Platform**

### Environment Variables for Production
```bash
DEBUG=False
HOST=0.0.0.0
PORT=3001
ALLOWED_ORIGINS=https://your-frontend-domain.com
JWT_SECRET_KEY=your-super-secure-secret-key
```

## 🔧 Configuration

### File Upload Limits
- **Max file size**: 10MB per file
- **Max files**: 20 files per request
- **Supported formats**: PDF, DOC, DOCX

### Rate Limiting (Recommended)
- **Auth endpoints**: 5 requests/minute
- **Resume processing**: 3 requests/minute
- **Other endpoints**: 60 requests/minute

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📊 Monitoring

### Health Checks
- `GET /health` - Basic health check
- `GET /` - API information

### Logging
- Structured logging with uvicorn
- Error tracking and monitoring
- Performance metrics

## 🔒 Security

### Best Practices
- **HTTPS only** in production
- **CORS** properly configured
- **Input validation** on all endpoints
- **File type validation** for uploads
- **JWT token expiration**
- **Password hashing** with bcrypt

### Security Headers
```python
# Add to main.py for production
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
```

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Connection Error**
   - Check service account credentials
   - Verify project ID
   - Ensure Firestore is enabled

2. **Gemini AI Error**
   - Verify API key is correct
   - Check API quotas and limits
   - Ensure billing is enabled

3. **File Processing Error**
   - Check file format support
   - Verify file size limits
   - Test with different PDF/DOC files

### Debug Mode
```bash
DEBUG=True python run.py
```

## 📞 Support

For issues and questions:
- Check the logs for detailed error messages
- Verify environment variables
- Test with sample files
- Review API documentation

## 🔄 Updates

To update the backend:
```bash
git pull origin main
pip install -r requirements.txt
python run.py
```

---

**Auto Screener Agent Backend** - Built with ❤️ using FastAPI, Firebase, and Google Gemini AI