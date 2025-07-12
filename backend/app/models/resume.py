from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CandidateStatus(str, Enum):
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"

class ProcessResumeRequest(BaseModel):
    jobDescription: str

class CandidateResult(BaseModel):
    id: str
    fileName: str
    candidate: str
    email: EmailStr
    phone: Optional[str] = None
    score: int  # 0-100
    status: CandidateStatus
    summary: str
    experience: str
    skills: List[str]
    education: Optional[str] = None
    location: Optional[str] = None
    extractedText: Optional[str] = None

class RejectionEmail(BaseModel):
    candidateId: str
    candidate: str
    email: EmailStr
    subject: str
    content: str

class ProcessResumeResponse(BaseModel):
    jobId: str
    candidates: List[CandidateResult]
    rejectionEmails: List[RejectionEmail]
    totalProcessed: int
    shortlistedCount: int
    rejectedCount: int
    averageScore: float
    processingTime: int  # milliseconds

class JobHistory(BaseModel):
    id: str
    jobDescription: str
    totalProcessed: int
    shortlistedCount: int
    rejectedCount: int
    averageScore: float
    processingTime: int
    createdAt: datetime

class JobDetails(ProcessResumeResponse):
    jobDescription: str
    createdAt: datetime