# Auto Screener Agent - API Documentation

## Overview
This document provides comprehensive guidelines for building the backend API for the Auto Screener Agent platform. The frontend is built with React and expects specific API endpoints for authentication and resume processing.

## Technology Stack Recommendations
- **Backend**: Python (FastAPI/Flask/Django)
- **Database**: Firebase Firestore or PostgreSQL
- **Authentication**: Firebase Auth or JWT tokens
- **File Storage**: Firebase Storage or AWS S3
- **AI Processing**: OpenAI GPT-4, Google Gemini, or custom ML models

## Base URL Structure
```
Production: https://your-domain.com/api
Development: http://localhost:3001/api
```

## Authentication System

### Overview
The platform uses JWT-based authentication with refresh tokens. Users can register, login, and access protected resources.

### Database Schema (Users Collection)
```json
{
  "id": "string (UUID)",
  "email": "string (unique)",
  "firstName": "string",
  "lastName": "string", 
  "company": "string (optional)",
  "role": "string (optional)",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Authentication Endpoints

#### 1. User Registration
```
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "firstName": "John",
  "lastName": "Doe",
  "company": "Tech Corp" // optional
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "company": "Tech Corp",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "token": "jwt-access-token",
  "refreshToken": "jwt-refresh-token"
}
```

**Error Response (400 Bad Request):**
```json
{
  "message": "Email already exists",
  "code": "EMAIL_EXISTS"
}
```

#### 2. User Login
```
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "company": "Tech Corp",
    "createdAt": "2024-01-15T10:30:00Z"
  },
  "token": "jwt-access-token",
  "refreshToken": "jwt-refresh-token"
}
```

#### 3. Get Current User
```
GET /api/auth/me
Authorization: Bearer {jwt-token}
```

**Response (200 OK):**
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "company": "Tech Corp",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

#### 4. Refresh Token
```
POST /api/auth/refresh
```

**Request Body:**
```json
{
  "refreshToken": "jwt-refresh-token"
}
```

**Response (200 OK):**
```json
{
  "user": { /* user object */ },
  "token": "new-jwt-access-token",
  "refreshToken": "new-jwt-refresh-token"
}
```

#### 5. Logout
```
POST /api/auth/logout
Authorization: Bearer {jwt-token}
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

## Resume Processing System

### Database Schema

#### Jobs Collection
```json
{
  "id": "string (UUID)",
  "userId": "string (foreign key)",
  "jobDescription": "string",
  "totalProcessed": "number",
  "shortlistedCount": "number", 
  "rejectedCount": "number",
  "averageScore": "number",
  "processingTime": "number (milliseconds)",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

#### Candidates Collection
```json
{
  "id": "string (UUID)",
  "jobId": "string (foreign key)",
  "fileName": "string",
  "candidate": "string",
  "email": "string",
  "phone": "string (optional)",
  "score": "number (0-100)",
  "status": "string (shortlisted|rejected)",
  "summary": "string",
  "experience": "string",
  "skills": "array of strings",
  "education": "string (optional)",
  "location": "string (optional)",
  "extractedText": "string (optional)",
  "createdAt": "timestamp"
}
```

#### Rejection Emails Collection
```json
{
  "id": "string (UUID)",
  "jobId": "string (foreign key)",
  "candidateId": "string (foreign key)",
  "candidate": "string",
  "email": "string",
  "subject": "string",
  "content": "string",
  "createdAt": "timestamp"
}
```

### Resume Processing Endpoints

#### 1. Process Resumes
```
POST /api/resumes/process
Authorization: Bearer {jwt-token}
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
jobDescription: "Software Engineer position requiring 3+ years experience..."
resumes: [file1.pdf, file2.docx, file3.pdf] // Multiple files
```

**Processing Steps:**
1. **File Validation**: Check file types (PDF, DOC, DOCX) and sizes
2. **Text Extraction**: Extract text from uploaded resume files
3. **AI Analysis**: Use AI to analyze each resume against job description
4. **Scoring**: Generate fit scores (0-100) for each candidate
5. **Classification**: Determine shortlisted vs rejected (typically score >= 80)
6. **Email Generation**: Create personalized rejection emails
7. **Data Storage**: Save all results to database

**Response (200 OK):**
```json
{
  "jobId": "uuid-string",
  "candidates": [
    {
      "id": "candidate-uuid",
      "fileName": "john_doe_resume.pdf",
      "candidate": "John Doe",
      "email": "john.doe@email.com",
      "phone": "+1-555-0123",
      "score": 85,
      "status": "shortlisted",
      "summary": "Excellent match with 5+ years of relevant experience...",
      "experience": "5 years",
      "skills": ["JavaScript", "React", "Node.js", "Python"],
      "education": "BS Computer Science",
      "location": "San Francisco, CA"
    }
  ],
  "rejectionEmails": [
    {
      "candidateId": "candidate-uuid",
      "candidate": "Jane Smith", 
      "email": "jane.smith@email.com",
      "subject": "Thank you for your application - Software Engineer Position",
      "content": "Dear Jane Smith,\n\nThank you for taking the time..."
    }
  ],
  "totalProcessed": 10,
  "shortlistedCount": 3,
  "rejectedCount": 7,
  "averageScore": 72,
  "processingTime": 15000
}
```

#### 2. Get Job History
```
GET /api/resumes/history
Authorization: Bearer {jwt-token}
```

**Response (200 OK):**
```json
[
  {
    "id": "job-uuid",
    "jobDescription": "Software Engineer position...",
    "totalProcessed": 10,
    "shortlistedCount": 3,
    "rejectedCount": 7,
    "averageScore": 72,
    "processingTime": 15000,
    "createdAt": "2024-01-15T10:30:00Z"
  }
]
```

#### 3. Get Job Details
```
GET /api/resumes/job/{jobId}
Authorization: Bearer {jwt-token}
```

**Response (200 OK):**
```json
{
  "jobId": "job-uuid",
  "jobDescription": "Software Engineer position...",
  "candidates": [ /* array of candidates */ ],
  "rejectionEmails": [ /* array of rejection emails */ ],
  "totalProcessed": 10,
  "shortlistedCount": 3,
  "rejectedCount": 7,
  "averageScore": 72,
  "processingTime": 15000
}
```

## AI Processing Guidelines

### Resume Text Extraction
- **PDF Files**: Use libraries like PyPDF2, pdfplumber, or pymupdf
- **DOC/DOCX Files**: Use python-docx or mammoth
- **Error Handling**: Gracefully handle corrupted or password-protected files

### AI Analysis Prompt Structure
```
You are an expert HR recruiter. Analyze this resume against the job description and provide:

Job Description:
{job_description}

Resume Content:
{extracted_text}

Please provide a JSON response with:
1. candidate_name: Full name of the candidate
2. email: Email address (extract from resume)
3. phone: Phone number (if available)
4. experience_years: Years of relevant experience
5. skills: Array of technical skills mentioned
6. education: Highest education level
7. location: Current location (if mentioned)
8. fit_score: Score from 0-100 based on job requirements
9. summary: 2-3 sentence summary of candidate fit
10. rejection_reason: If score < 80, explain why (for rejection email)
```

### Rejection Email Template
```
Dear {candidate_name},

Thank you for taking the time to apply for the {position_title} position at our company. We appreciate your interest in joining our team.

After careful review of your application and qualifications, we have decided to move forward with other candidates whose experience more closely aligns with our current requirements.

{personalized_feedback_based_on_analysis}

We were impressed by your background and encourage you to apply for future opportunities that may be a better fit for your skills and experience.

Thank you again for your interest in our company.

Best regards,
HR Team
```

## Implementation Tips

### Firebase Setup (Recommended)
1. **Authentication**: Use Firebase Auth for user management
2. **Database**: Firestore for storing jobs, candidates, and emails
3. **Storage**: Firebase Storage for uploaded resume files
4. **Security Rules**: Implement proper Firestore security rules

### Python Backend Structure
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models/              # Database models
│   ├── routes/              # API routes
│   │   ├── auth.py
│   │   └── resumes.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── resume_service.py
│   │   └── ai_service.py
│   └── utils/               # Utilities
│       ├── file_parser.py
│       └── email_generator.py
├── requirements.txt
└── .env
```

### Environment Variables
```
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI Service
OPENAI_API_KEY=your-openai-key
# OR
GOOGLE_AI_API_KEY=your-google-ai-key

# CORS
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend-domain.com
```

### Error Handling
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Invalid or expired token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: File processing errors
- **500 Internal Server Error**: Server errors

### Rate Limiting
Implement rate limiting for:
- Authentication endpoints: 5 requests per minute
- Resume processing: 3 requests per minute (due to AI processing time)
- File uploads: 10MB max file size, 20 files max per request

### Security Considerations
1. **Input Validation**: Validate all inputs and file types
2. **File Scanning**: Scan uploaded files for malware
3. **Data Privacy**: Encrypt sensitive data and implement GDPR compliance
4. **API Keys**: Secure AI service API keys
5. **CORS**: Configure proper CORS settings
6. **HTTPS**: Use HTTPS in production

## Testing
- **Unit Tests**: Test individual functions and services
- **Integration Tests**: Test API endpoints
- **Load Tests**: Test with multiple file uploads
- **Security Tests**: Test authentication and authorization

This documentation provides everything needed to build a robust backend for the Auto Screener Agent platform. The frontend is already configured to work with these exact API endpoints and data structures.