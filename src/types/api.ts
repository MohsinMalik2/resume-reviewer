export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  company?: string;
  role?: string;
  createdAt: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  company?: string;
}

export interface ProcessResumeRequest {
  jobDescription: string;
  files: File[];
}

export interface CandidateResult {
  id: string;
  fileName: string;
  candidate: string;
  email: string;
  phone?: string;
  score: number;
  status: 'shortlisted' | 'rejected';
  summary: string;
  experience: string;
  skills: string[];
  education?: string;
  location?: string;
  extractedText?: string;
}

export interface RejectionEmail {
  candidateId: string;
  candidate: string;
  email: string;
  subject: string;
  content: string;
}

export interface ProcessResumeResponse {
  jobId: string;
  candidates: CandidateResult[];
  rejectionEmails: RejectionEmail[];
  totalProcessed: number;
  shortlistedCount: number;
  rejectedCount: number;
  averageScore: number;
  processingTime: number;
}

export interface ApiError {
  message: string;
  code: string;
  details?: any;
}