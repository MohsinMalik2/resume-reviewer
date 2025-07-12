from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from datetime import datetime
import time
import uuid

from app.models.resume import (
    ProcessResumeResponse, 
    CandidateResult, 
    RejectionEmail, 
    JobHistory,
    JobDetails,
    CandidateStatus
)
from app.services.auth_service import AuthService
from app.services.firebase_service import FirebaseService
from app.agents.orchestrator import AgentOrchestrator
from app.services.ai_service import get_model

router = APIRouter()
security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user ID from token"""
    user = AuthService.get_current_user(credentials.credentials)
    return user.id

@router.post("/process", response_model=ProcessResumeResponse)
async def process_resumes(
    jobDescription: str = Form(...),
    resumes: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Process uploaded resumes using multi-agent system"""
    start_time = time.time()
    
    try:
        # Initialize multi-agent orchestrator
        gemini_model = get_model()
        orchestrator = AgentOrchestrator(gemini_model)
        
        # Validate files
        if not resumes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No resume files uploaded"
            )
        
        if len(resumes) > 20:  # Limit number of files
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 files allowed per request"
            )
        
        # Validate job description
        if not jobDescription.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job description is required"
            )
        
        # Prepare files for multi-agent processing
        files_data = []
        
        for resume_file in resumes:
            file_content = await resume_file.read()
            files_data.append({
                "filename": resume_file.filename,
                "content": file_content
            })
        
        if not files_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files uploaded"
            )
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Process with multi-agent system
        orchestrator_input = {
            "files": files_data,
            "job_description": jobDescription,
            "job_id": job_id,
            "user_id": user_id,
            "job_requirements": {},  # Could be extracted from job description
            "company_info": {}  # Could be from user profile
        }
        
        # Run multi-agent workflow
        workflow_result = await orchestrator.process_resumes(orchestrator_input)
        
        # Extract results for database storage
        candidates = workflow_result["candidates"]
        rejection_emails = workflow_result["rejectionEmails"]
        
        # Create job record
        now = datetime.utcnow()
        job_data = {
            "id": job_id,
            "userId": user_id,
            "jobDescription": jobDescription,
            "totalProcessed": workflow_result["totalProcessed"],
            "shortlistedCount": workflow_result["shortlistedCount"],
            "rejectedCount": workflow_result["rejectedCount"],
            "averageScore": workflow_result["averageScore"],
            "processingTime": workflow_result["processingTime"],
            "createdAt": now,
            "updatedAt": now,
            "multiAgentMetadata": workflow_result["multiAgentResults"]["workflow_metadata"]
        }
        
        FirebaseService.create_job(job_data)
        
        # Save candidates
        candidates_data = []
        for candidate in candidates:
            candidate_data = candidate.copy()
            candidate_data["jobId"] = job_id
            candidate_data["createdAt"] = now
            candidates_data.append(candidate_data)
        
        if candidates_data:
            FirebaseService.create_candidates(candidates_data)
        
        # Save rejection emails
        if rejection_emails:
            emails_data = []
            for email in rejection_emails:
                email_data = email.copy()
                email_data["jobId"] = job_id
                email_data["createdAt"] = now
                emails_data.append(email_data)
            
            FirebaseService.create_rejection_emails(emails_data)
        
        # Return the workflow result (already in correct format)
        return workflow_result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Multi-agent resume processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent resume processing failed: {str(e)}"
        )

@router.get("/history", response_model=List[JobHistory])
async def get_job_history(user_id: str = Depends(get_current_user_id)):
    """Get user's job processing history"""
    try:
        jobs_data = FirebaseService.get_jobs_by_user(user_id)
        
        jobs = []
        for job_data in jobs_data:
            job = JobHistory(
                id=job_data["id"],
                jobDescription=job_data["jobDescription"],
                totalProcessed=job_data["totalProcessed"],
                shortlistedCount=job_data["shortlistedCount"],
                rejectedCount=job_data["rejectedCount"],
                averageScore=job_data["averageScore"],
                processingTime=job_data["processingTime"],
                createdAt=job_data["createdAt"]
            )
            jobs.append(job)
        
        return jobs
        
    except Exception as e:
        print(f"Get job history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job history"
        )

@router.get("/job/{job_id}", response_model=JobDetails)
async def get_job_details(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Get detailed results for a specific job"""
    try:
        # Get job data
        job_data = FirebaseService.get_job_by_id(job_id)
        
        if not job_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Verify job belongs to user
        if job_data["userId"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get candidates
        candidates_data = FirebaseService.get_candidates_by_job(job_id)
        candidates = []
        for candidate_data in candidates_data:
            candidate = CandidateResult(**candidate_data)
            candidates.append(candidate)
        
        # Get rejection emails
        emails_data = FirebaseService.get_rejection_emails_by_job(job_id)
        rejection_emails = []
        for email_data in emails_data:
            email = RejectionEmail(**email_data)
            rejection_emails.append(email)
        
        # Return job details
        return JobDetails(
            jobId=job_data["id"],
            jobDescription=job_data["jobDescription"],
            candidates=candidates,
            rejectionEmails=rejection_emails,
            totalProcessed=job_data["totalProcessed"],
            shortlistedCount=job_data["shortlistedCount"],
            rejectedCount=job_data["rejectedCount"],
            averageScore=job_data["averageScore"],
            processingTime=job_data["processingTime"],
            createdAt=job_data["createdAt"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get job details error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job details"
        )