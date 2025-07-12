from typing import Dict, Any, List
from datetime import datetime
import asyncio
import uuid

from .base_agent import BaseAgent, AgentResult
from .data_extraction_agent import DataExtractionAgent
from .reasoning_agent import ReasoningAgent
from .execution_agent import ExecutionAgent

class AgentOrchestrator:
    """
    Multi-Agent Orchestrator
    Coordinates the collaboration between all three vertical AI agents
    """
    
    def __init__(self, gemini_model):
        self.orchestrator_id = str(uuid.uuid4())
        self.gemini_model = gemini_model
        
        # Initialize all agents
        self.data_extraction_agent = DataExtractionAgent()
        self.reasoning_agent = ReasoningAgent(gemini_model)
        self.execution_agent = ExecutionAgent(gemini_model)
        
        self.workflow_status = "initialized"
        self.workflow_history = []
        
    async def process_resumes(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestration method that coordinates all agents
        
        Input: {
            "files": [{"filename": str, "content": bytes}],
            "job_description": str,
            "job_id": str,
            "user_id": str
        }
        
        Output: Complete processing results from all agents
        """
        
        workflow_start = datetime.utcnow()
        self.workflow_status = "processing"
        
        try:
            self._log_workflow("Workflow started", {
                "file_count": len(input_data.get("files", [])),
                "job_id": input_data.get("job_id"),
                "user_id": input_data.get("user_id")
            })
            
            # PHASE 1: Data Extraction Agent
            self._log_workflow("Phase 1: Starting data extraction")
            extraction_result = await self.data_extraction_agent.process({
                "files": input_data["files"],
                "job_id": input_data["job_id"]
            })
            
            if not extraction_result.success:
                raise Exception(f"Data extraction failed: {extraction_result.error}")
            
            self._log_workflow("Phase 1: Data extraction completed", {
                "extracted_count": len(extraction_result.data["extracted_resumes"])
            })
            
            # PHASE 2: Reasoning Agent
            self._log_workflow("Phase 2: Starting candidate analysis and reasoning")
            reasoning_result = await self.reasoning_agent.process({
                "extracted_resumes": extraction_result.data["extracted_resumes"],
                "job_description": input_data["job_description"],
                "job_requirements": input_data.get("job_requirements", {}),
                "comparison_score": input_data.get("comparison_score", 50)
            })
            
            if not reasoning_result.success:
                raise Exception(f"Reasoning failed: {reasoning_result.error}")
            
            self._log_workflow("Phase 2: Reasoning completed", {
                "analyzed_count": len(reasoning_result.data["analyzed_candidates"]),
                "shortlisted": reasoning_result.metadata["shortlisted"],
                "rejected": reasoning_result.metadata["rejected"]
            })
            
            # PHASE 3: Execution Agent
            self._log_workflow("Phase 3: Starting execution and output generation")
            execution_result = await self.execution_agent.process({
                "analyzed_candidates": reasoning_result.data["analyzed_candidates"],
                "job_description": input_data["job_description"],
                "job_requirements": input_data.get("job_requirements", {}),
                "company_info": input_data.get("company_info", {})
            })
            
            if not execution_result.success:
                raise Exception(f"Execution failed: {execution_result.error}")
            
            self._log_workflow("Phase 3: Execution completed", {
                "shortlisted_final": len(execution_result.data["shortlisted_candidates"]),
                "rejection_emails": len(execution_result.data["rejection_emails"]),
                "escalated_cases": len(execution_result.data["escalated_cases"])
            })
            
            # PHASE 4: Final Orchestration and Quality Assurance
            self._log_workflow("Phase 4: Final orchestration and QA")
            final_result = await self._finalize_workflow(
                extraction_result,
                reasoning_result, 
                execution_result,
                input_data,
                workflow_start
            )
            
            self.workflow_status = "completed"
            self._log_workflow("Workflow completed successfully")
            
            return final_result
            
        except Exception as e:
            self.workflow_status = "failed"
            self._log_workflow("Workflow failed", {"error": str(e)})
            raise Exception(f"Multi-agent workflow failed: {str(e)}")
    
    async def _finalize_workflow(self, extraction_result: AgentResult, reasoning_result: AgentResult, 
                                execution_result: AgentResult, input_data: Dict[str, Any], 
                                workflow_start: datetime) -> Dict[str, Any]:
        """Finalize workflow and create comprehensive output"""
        
        workflow_end = datetime.utcnow()
        processing_time = int((workflow_end - workflow_start).total_seconds() * 1000)
        
        # Extract key data
        shortlisted_candidates = execution_result.data["shortlisted_candidates"]
        rejection_emails = execution_result.data["rejection_emails"]
        escalated_cases = execution_result.data["escalated_cases"]
        
        # Calculate final statistics
        total_processed = len(extraction_result.data["extracted_resumes"])
        shortlisted_count = len(shortlisted_candidates)
        rejected_count = len(rejection_emails)
        average_score = reasoning_result.data["statistics"]["average_score"]
        
        # Create workflow metadata
        workflow_metadata = {
            "orchestrator_id": self.orchestrator_id,
            "workflow_start": workflow_start.isoformat(),
            "workflow_end": workflow_end.isoformat(),
            "processing_time_ms": processing_time,
            "agent_performance": {
                "data_extraction": {
                    "status": extraction_result.success,
                    "files_processed": len(extraction_result.data["extracted_resumes"]),
                    "extraction_success_rate": extraction_result.metadata["successful_extractions"] / extraction_result.metadata["total_files"] * 100
                },
                "reasoning": {
                    "status": reasoning_result.success,
                    "candidates_analyzed": len(reasoning_result.data["analyzed_candidates"]),
                    "average_confidence": self._calculate_average_confidence(reasoning_result.data["analyzed_candidates"])
                },
                "execution": {
                    "status": execution_result.success,
                    "emails_generated": len(rejection_emails),
                    "escalations_identified": len(escalated_cases)
                }
            },
            "quality_metrics": {
                "data_extraction_quality": self._assess_extraction_quality(extraction_result),
                "reasoning_quality": self._assess_reasoning_quality(reasoning_result),
                "execution_quality": self._assess_execution_quality(execution_result)
            }
        }
        
        # Create final response in the format expected by the frontend
        final_response = {
            "jobId": input_data["job_id"],
            "candidates": self._format_candidates_for_frontend(shortlisted_candidates, rejection_emails),
            "rejectionEmails": self._format_rejection_emails_for_frontend(rejection_emails),
            "totalProcessed": total_processed,
            "shortlistedCount": shortlisted_count,
            "rejectedCount": rejected_count,
            "averageScore": round(average_score, 1),
            "processingTime": processing_time,
            
            # Additional multi-agent specific data
            "multiAgentResults": {
                "extraction_results": extraction_result.data,
                "reasoning_results": reasoning_result.data,
                "execution_results": execution_result.data,
                "escalated_cases": escalated_cases,
                "workflow_metadata": workflow_metadata,
                "agent_collaboration_log": self.workflow_history
            }
        }
        
        return final_response
    
    def _format_candidates_for_frontend(self, shortlisted: List[Dict], rejected_emails: List[Dict]) -> List[Dict[str, Any]]:
        """Format all candidates for frontend consumption"""
        all_candidates = []
        
        # Add shortlisted candidates
        for candidate in shortlisted:
            all_candidates.append({
                "id": candidate["id"],
                "fileName": candidate["fileName"],
                "candidate": candidate["candidate"],
                "email": candidate["email"],
                "phone": candidate.get("phone"),
                "score": candidate["score"],
                "status": "shortlisted",
                "summary": candidate["summary"],
                "experience": candidate["experience"],
                "skills": candidate["skills"],
                "education": candidate.get("education"),
                "location": candidate.get("location"),
                "extractedText": None  # Don't send full text to frontend
            })
        
        # Add rejected candidates (from rejection emails)
        for email in rejected_emails:
            all_candidates.append({
                "id": email["candidateId"],
                "fileName": f"rejected_candidate_{email['candidateId']}.pdf",  # Placeholder
                "candidate": email["candidate"],
                "email": email["email"],
                "phone": None,
                "score": email["candidate_score"],
                "status": "rejected",
                "summary": f"Score: {email['candidate_score']}/100. Reasons: {', '.join(email['rejection_reasons'])}",
                "experience": "Not specified",
                "skills": [],
                "education": None,
                "location": None,
                "extractedText": None
            })
        
        return all_candidates
    
    def _format_rejection_emails_for_frontend(self, rejection_emails: List[Dict]) -> List[Dict[str, Any]]:
        """Format rejection emails for frontend"""
        formatted_emails = []
        
        for email in rejection_emails:
            formatted_emails.append({
                "candidateId": email["candidateId"],
                "candidate": email["candidate"],
                "email": email["email"],
                "subject": email["subject"],
                "content": email["content"]
            })
        
        return formatted_emails
    
    def _calculate_average_confidence(self, analyzed_candidates: List[Dict]) -> float:
        """Calculate average AI confidence across all candidates"""
        confidences = [c["analysis"].get("confidence", 0.8) for c in analyzed_candidates]
        return sum(confidences) / len(confidences) if confidences else 0.8
    
    def _assess_extraction_quality(self, extraction_result: AgentResult) -> Dict[str, Any]:
        """Assess quality of data extraction"""
        metadata = extraction_result.metadata
        success_rate = metadata["successful_extractions"] / metadata["total_files"] * 100
        
        return {
            "success_rate": success_rate,
            "quality_score": "high" if success_rate >= 90 else "medium" if success_rate >= 70 else "low",
            "total_files": metadata["total_files"],
            "successful_extractions": metadata["successful_extractions"]
        }
    
    def _assess_reasoning_quality(self, reasoning_result: AgentResult) -> Dict[str, Any]:
        """Assess quality of reasoning analysis"""
        statistics = reasoning_result.data["statistics"]
        
        # Quality indicators
        score_variance = self._calculate_score_variance(reasoning_result.data["analyzed_candidates"])
        reasonable_shortlist_rate = 10 <= statistics.get("shortlist_rate", 0) <= 40
        
        quality_score = "high"
        if score_variance < 10:  # Too little variance might indicate poor discrimination
            quality_score = "medium"
        if not reasonable_shortlist_rate:
            quality_score = "low"
        
        return {
            "quality_score": quality_score,
            "score_variance": score_variance,
            "shortlist_rate": statistics.get("shortlist_rate", 0),
            "average_score": statistics["average_score"],
            "reasonable_distribution": reasonable_shortlist_rate
        }
    
    def _assess_execution_quality(self, execution_result: AgentResult) -> Dict[str, Any]:
        """Assess quality of execution"""
        summary = execution_result.data["execution_summary"]
        
        # Quality indicators
        personalization_rate = (summary["execution_quality_metrics"]["personalized_emails_generated"] / 
                               summary["rejected_count"] * 100) if summary["rejected_count"] > 0 else 100
        
        escalation_rate = summary["execution_quality_metrics"]["escalation_rate"]
        
        quality_score = "high"
        if personalization_rate < 80:
            quality_score = "medium"
        if escalation_rate > 30:  # Too many escalations might indicate issues
            quality_score = "low"
        
        return {
            "quality_score": quality_score,
            "personalization_rate": personalization_rate,
            "escalation_rate": escalation_rate,
            "emails_generated": summary["rejected_count"]
        }
    
    def _calculate_score_variance(self, analyzed_candidates: List[Dict]) -> float:
        """Calculate variance in candidate scores"""
        scores = [c["score"] for c in analyzed_candidates]
        if len(scores) < 2:
            return 0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        return variance ** 0.5  # Standard deviation
    
    def _log_workflow(self, message: str, details: Dict[str, Any] = None):
        """Log workflow activity"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": self.orchestrator_id,
            "message": message,
            "details": details or {}
        }
        
        self.workflow_history.append(log_entry)
        print(f"[ORCHESTRATOR-{self.orchestrator_id[:8]}] {message}: {details or ''}")
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "status": self.workflow_status,
            "agents_status": {
                "data_extraction": self.data_extraction_agent.get_status(),
                "reasoning": self.reasoning_agent.get_status(),
                "execution": self.execution_agent.get_status()
            },
            "workflow_history": self.workflow_history[-10:]  # Last 10 entries
        }