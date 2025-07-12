import google.generativeai as genai
import json
import re
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentResult

class ExecutionAgent(BaseAgent):
    """
    Agent 3: Execution Agent
    Responsible for executing final tasks: generating shortlists, creating rejection emails,
    and escalating complex cases
    """
    
    def __init__(self, gemini_model):
        super().__init__()
        self.agent_type = "execution"
        self.model = gemini_model
        self.capabilities = [
            "shortlist_generation",
            "rejection_email_creation",
            "personalized_communication",
            "escalation_handling",
            "final_output_formatting"
        ]
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute final tasks based on reasoning agent decisions
        
        Input: {
            "analyzed_candidates": [...],
            "job_description": str,
            "job_requirements": {...},
            "company_info": {...}
        }
        
        Output: {
            "shortlisted_candidates": [...],
            "rejection_emails": [...],
            "escalated_cases": [...],
            "execution_summary": {...}
        }
        """
        try:
            self.status = "executing"
            self.log_activity("Starting execution phase", {
                "candidate_count": len(input_data.get("analyzed_candidates", []))
            })
            
            analyzed_candidates = input_data.get("analyzed_candidates", [])
            job_description = input_data.get("job_description", "")
            
            # Separate shortlisted and rejected candidates
            shortlisted = [c for c in analyzed_candidates if c["decision"] == "shortlist"]
            rejected = [c for c in analyzed_candidates if c["decision"] == "reject"]
            
            # Generate final shortlist with enhanced data
            shortlisted_candidates = await self._generate_shortlist(shortlisted, job_description)
            
            # Generate personalized rejection emails
            rejection_emails = await self._generate_rejection_emails(rejected, job_description)
            
            # Check for escalation cases
            escalated_cases = await self._check_escalation_cases(analyzed_candidates)
            
            # Create execution summary
            execution_summary = self._create_execution_summary(
                shortlisted_candidates, 
                rejection_emails, 
                escalated_cases
            )
            
            self.status = "completed"
            
            return AgentResult(
                success=True,
                data={
                    "shortlisted_candidates": shortlisted_candidates,
                    "rejection_emails": rejection_emails,
                    "escalated_cases": escalated_cases,
                    "execution_summary": execution_summary
                },
                metadata={
                    "shortlisted_count": len(shortlisted_candidates),
                    "rejection_emails_count": len(rejection_emails),
                    "escalated_count": len(escalated_cases),
                    "agent_type": self.agent_type
                }
            )
            
        except Exception as e:
            self.status = "failed"
            self.log_activity("Execution failed", {"error": str(e)})
            return AgentResult(success=False, error=str(e))
    
    async def _generate_shortlist(self, shortlisted_candidates: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """Generate enhanced shortlist with additional insights"""
        
        enhanced_shortlist = []
        
        for candidate in shortlisted_candidates:
            try:
                # Enhance candidate data with additional insights
                enhanced_candidate = await self._enhance_candidate_data(candidate, job_description)
                enhanced_shortlist.append(enhanced_candidate)
                
                self.log_activity("Candidate enhanced for shortlist", {
                    "filename": candidate["filename"],
                    "score": candidate["score"]
                })
                
            except Exception as e:
                self.log_activity("Candidate enhancement failed", {
                    "filename": candidate["filename"],
                    "error": str(e)
                })
                # Add candidate without enhancement
                enhanced_shortlist.append(self._create_basic_shortlist_entry(candidate))
        
        # Sort by score and add ranking
        enhanced_shortlist.sort(key=lambda x: x["score"], reverse=True)
        for i, candidate in enumerate(enhanced_shortlist):
            candidate["shortlist_rank"] = i + 1
        
        return enhanced_shortlist
    
    async def _enhance_candidate_data(self, candidate: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Enhance candidate data with additional insights"""
        
        # Create enhancement prompt
        enhancement_prompt = f"""
Based on the candidate analysis, provide additional insights for the shortlist.

CANDIDATE ANALYSIS:
{json.dumps(candidate["analysis"], indent=2)}

JOB DESCRIPTION:
{job_description}

Provide enhanced insights in JSON format:
{{
    "interview_focus_areas": ["Key areas to explore in interview"],
    "potential_concerns": ["Areas that need clarification"],
    "value_proposition": "Why this candidate stands out",
    "next_steps": "Recommended next steps for this candidate",
    "interview_questions": ["Suggested interview questions"],
    "salary_expectations": "Estimated salary range based on experience",
    "cultural_fit_indicators": ["Signs of cultural alignment"],
    "growth_potential": "Assessment of candidate's growth potential"
}}
"""
        
        try:
            response = self.model.generate_content(enhancement_prompt)
            enhancement_data = self._parse_enhancement_response(response.text)
            
            # Create enhanced candidate entry
            enhanced_candidate = {
                "id": candidate["candidate_id"],
                "fileName": candidate["filename"],
                "candidate": candidate["analysis"]["candidate_info"].get("name", "Candidate Name"),
                "email": candidate["analysis"]["candidate_info"].get("email", "email@example.com"),
                "phone": candidate["analysis"]["candidate_info"].get("phone"),
                "score": candidate["score"],
                "status": "shortlisted",
                "summary": candidate["reasoning"],
                "experience": self._extract_experience_summary(candidate),
                "skills": candidate["strengths"],
                "education": self._extract_education_summary(candidate),
                "location": candidate["analysis"]["candidate_info"].get("location"),
                "strengths": candidate["strengths"],
                "weaknesses": candidate["weaknesses"],
                "fit_assessment": candidate["fit_assessment"],
                "enhancement_insights": enhancement_data,
                "detailed_analysis": candidate["analysis"].get("detailed_analysis", {}),
                "recommendation": candidate["analysis"].get("recommendation", "Recommended for interview")
            }
            
            return enhanced_candidate
            
        except Exception as e:
            self.log_activity("Enhancement failed, using basic data", {"error": str(e)})
            return self._create_basic_shortlist_entry(candidate)
    
    def _parse_enhancement_response(self, response_text: str) -> Dict[str, Any]:
        """Parse enhancement response from AI"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._create_fallback_enhancement()
        except:
            return self._create_fallback_enhancement()
    
    def _create_fallback_enhancement(self) -> Dict[str, Any]:
        """Create fallback enhancement data"""
        return {
            "interview_focus_areas": ["Technical skills", "Experience relevance"],
            "potential_concerns": ["None identified"],
            "value_proposition": "Strong candidate with relevant experience",
            "next_steps": "Schedule technical interview",
            "interview_questions": ["Tell me about your experience with..."],
            "cultural_fit_indicators": ["Professional communication"],
            "growth_potential": "Good potential for growth"
        }
    
    def _create_basic_shortlist_entry(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Create basic shortlist entry without enhancement"""
        return {
            "id": candidate["candidate_id"],
            "fileName": candidate["filename"],
            "candidate": candidate["analysis"]["candidate_info"].get("name", "Candidate Name"),
            "email": candidate["analysis"]["candidate_info"].get("email", "email@example.com"),
            "phone": candidate["analysis"]["candidate_info"].get("phone"),
            "score": candidate["score"],
            "status": "shortlisted",
            "summary": candidate["reasoning"],
            "experience": self._extract_experience_summary(candidate),
            "skills": candidate["strengths"],
            "strengths": candidate["strengths"],
            "weaknesses": candidate["weaknesses"],
            "fit_assessment": candidate["fit_assessment"]
        }
    
    async def _generate_rejection_emails(self, rejected_candidates: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """Generate personalized rejection emails for each rejected candidate"""
        
        rejection_emails = []
        
        # Extract job title from description
        job_title = self._extract_job_title(job_description)
        
        for candidate in rejected_candidates:
            try:
                # Generate personalized rejection email
                email_data = await self._create_personalized_rejection_email(
                    candidate, 
                    job_title, 
                    job_description
                )
                
                rejection_emails.append(email_data)
                
                self.log_activity("Rejection email generated", {
                    "filename": candidate["filename"],
                    "candidate": email_data["candidate"]
                })
                
            except Exception as e:
                self.log_activity("Rejection email generation failed", {
                    "filename": candidate["filename"],
                    "error": str(e)
                })
                # Create fallback email
                fallback_email = self._create_fallback_rejection_email(candidate, job_title)
                rejection_emails.append(fallback_email)
        
        return rejection_emails
    
    async def _create_personalized_rejection_email(self, candidate: Dict[str, Any], job_title: str, job_description: str) -> Dict[str, Any]:
        """Create personalized rejection email using AI"""
        
        candidate_name = candidate["analysis"]["candidate_info"].get("name", "Candidate")
        candidate_email = candidate["analysis"]["candidate_info"].get("email", "email@example.com")
        rejection_reasons = candidate["weaknesses"]
        candidate_strengths = candidate["strengths"]
        
        email_prompt = f"""
Create a professional, empathetic rejection email for a job candidate.

CANDIDATE DETAILS:
- Name: {candidate_name}
- Score: {candidate["score"]}/100
- Strengths: {candidate_strengths}
- Areas for improvement: {rejection_reasons}
- Reasoning: {candidate["reasoning"]}

JOB DETAILS:
- Position: {job_title}
- Job Description: {job_description[:500]}...

REQUIREMENTS:
1. Professional and empathetic tone
2. Specific feedback based on the candidate's profile
3. Constructive criticism that helps the candidate improve
4. Encouragement for future applications
5. Mention specific strengths to soften the rejection
6. Explain exactly why they weren't selected (be specific but kind)

Provide the email in JSON format:
{{
    "subject": "Professional subject line",
    "content": "Complete email content with proper formatting and personalization"
}}

The email should be honest but encouraging, specific but not harsh.
"""
        
        try:
            response = self.model.generate_content(email_prompt)
            email_data = self._parse_email_response(response.text)
            
            return {
                "candidateId": candidate["candidate_id"],
                "candidate": candidate_name,
                "email": candidate_email,
                "subject": email_data["subject"],
                "content": email_data["content"],
                "rejection_reasons": rejection_reasons,
                "candidate_score": candidate["score"],
                "personalization_level": "high",
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.log_activity("AI email generation failed", {"error": str(e)})
            return self._create_fallback_rejection_email(candidate, job_title)
    
    def _parse_email_response(self, response_text: str) -> Dict[str, str]:
        """Parse email response from AI"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._create_fallback_email_content()
        except:
            return self._create_fallback_email_content()
    
    def _create_fallback_email_content(self) -> Dict[str, str]:
        """Create fallback email content"""
        return {
            "subject": "Thank you for your application",
            "content": "Thank you for your interest in our position. After careful consideration, we have decided to move forward with other candidates."
        }
    
    def _create_fallback_rejection_email(self, candidate: Dict[str, Any], job_title: str) -> Dict[str, Any]:
        """Create fallback rejection email"""
        candidate_name = candidate["analysis"]["candidate_info"].get("name", "Candidate")
        candidate_email = candidate["analysis"]["candidate_info"].get("email", "email@example.com")
        
        content = f"""Dear {candidate_name},

Thank you for taking the time to apply for the {job_title} position at our company. We appreciate your interest in joining our team.

After careful review of your application and qualifications, we have decided to move forward with other candidates whose experience more closely aligns with our current requirements.

Specifically, while we were impressed by your background, we found that other candidates had stronger alignment in the following areas:
- Technical skills that more closely match our immediate needs
- Experience level that better fits our current requirements

We encourage you to continue developing your skills and to apply for future opportunities that may be a better fit for your experience level.

Thank you again for your interest in our company.

Best regards,
HR Team"""

        return {
            "candidateId": candidate["candidate_id"],
            "candidate": candidate_name,
            "email": candidate_email,
            "subject": f"Thank you for your application - {job_title} Position",
            "content": content,
            "rejection_reasons": candidate["weaknesses"],
            "candidate_score": candidate["score"],
            "personalization_level": "basic",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _check_escalation_cases(self, analyzed_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for cases that need human escalation"""
        
        escalated_cases = []
        
        for candidate in analyzed_candidates:
            escalation_reasons = []
            
            # Check for borderline scores (need human review)
            if 70 <= candidate["score"] <= 79:
                escalation_reasons.append("Borderline score requiring human review")
            
            # Check for low AI confidence
            if candidate["analysis"].get("confidence", 1.0) < 0.6:
                escalation_reasons.append("Low AI confidence in analysis")
            
            # Check for conflicting signals
            if candidate["score"] >= 75 and len(candidate["weaknesses"]) >= 3:
                escalation_reasons.append("High score with multiple concerns")
            
            # Check for red flags
            red_flags = candidate["analysis"].get("red_flags", [])
            if red_flags:
                escalation_reasons.append(f"Red flags identified: {', '.join(red_flags)}")
            
            # Check for exceptional candidates (might need special handling)
            if candidate["score"] >= 95:
                escalation_reasons.append("Exceptional candidate - consider priority processing")
            
            if escalation_reasons:
                escalated_cases.append({
                    "candidate_id": candidate["candidate_id"],
                    "filename": candidate["filename"],
                    "candidate_name": candidate["analysis"]["candidate_info"].get("name", "Unknown"),
                    "score": candidate["score"],
                    "decision": candidate["decision"],
                    "escalation_reasons": escalation_reasons,
                    "escalation_priority": self._determine_escalation_priority(escalation_reasons),
                    "recommended_action": self._recommend_escalation_action(escalation_reasons),
                    "escalated_at": datetime.utcnow().isoformat()
                })
        
        return escalated_cases
    
    def _determine_escalation_priority(self, reasons: List[str]) -> str:
        """Determine escalation priority based on reasons"""
        if any("exceptional" in reason.lower() for reason in reasons):
            return "high"
        elif any("red flag" in reason.lower() for reason in reasons):
            return "high"
        elif any("borderline" in reason.lower() for reason in reasons):
            return "medium"
        else:
            return "low"
    
    def _recommend_escalation_action(self, reasons: List[str]) -> str:
        """Recommend action for escalated case"""
        if any("exceptional" in reason.lower() for reason in reasons):
            return "Fast-track for senior review and immediate interview scheduling"
        elif any("red flag" in reason.lower() for reason in reasons):
            return "Detailed manual review required before proceeding"
        elif any("borderline" in reason.lower() for reason in reasons):
            return "Human recruiter review to make final decision"
        else:
            return "Additional review recommended"
    
    def _create_execution_summary(self, shortlisted: List, rejections: List, escalated: List) -> Dict[str, Any]:
        """Create comprehensive execution summary"""
        
        total_processed = len(shortlisted) + len(rejections)
        
        return {
            "execution_timestamp": datetime.utcnow().isoformat(),
            "total_candidates_processed": total_processed,
            "shortlisted_count": len(shortlisted),
            "rejected_count": len(rejections),
            "escalated_count": len(escalated),
            "shortlist_rate": (len(shortlisted) / total_processed * 100) if total_processed > 0 else 0,
            "average_shortlist_score": sum(c["score"] for c in shortlisted) / len(shortlisted) if shortlisted else 0,
            "average_rejection_score": sum(r["candidate_score"] for r in rejections) / len(rejections) if rejections else 0,
            "execution_quality_metrics": {
                "personalized_emails_generated": len([r for r in rejections if r.get("personalization_level") == "high"]),
                "escalation_rate": (len(escalated) / total_processed * 100) if total_processed > 0 else 0,
                "high_priority_escalations": len([e for e in escalated if e["escalation_priority"] == "high"])
            },
            "recommendations": self._generate_process_recommendations(shortlisted, rejections, escalated)
        }
    
    def _generate_process_recommendations(self, shortlisted: List, rejections: List, escalated: List) -> List[str]:
        """Generate recommendations for improving the process"""
        recommendations = []
        
        total = len(shortlisted) + len(rejections)
        shortlist_rate = (len(shortlisted) / total * 100) if total > 0 else 0
        
        if shortlist_rate > 50:
            recommendations.append("High shortlist rate detected - consider tightening criteria")
        elif shortlist_rate < 10:
            recommendations.append("Low shortlist rate - consider reviewing job requirements")
        
        if len(escalated) > total * 0.3:
            recommendations.append("High escalation rate - consider improving AI training data")
        
        if shortlisted:
            avg_score = sum(c["score"] for c in shortlisted) / len(shortlisted)
            if avg_score < 80:
                recommendations.append("Average shortlist score is low - review selection criteria")
        
        return recommendations
    
    def _extract_job_title(self, job_description: str) -> str:
        """Extract job title from job description"""
        lines = job_description.split('\n')[:3]
        for line in lines:
            line = line.strip()
            if len(line) < 100 and any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
                return line
        
        return "Position"
    
    def _extract_experience_summary(self, candidate: Dict[str, Any]) -> str:
        """Extract experience summary from candidate data"""
        detailed_analysis = candidate["analysis"].get("detailed_analysis", {})
        experience_level = detailed_analysis.get("experience_level", "Experience level not specified")
        return experience_level
    
    def _extract_education_summary(self, candidate: Dict[str, Any]) -> str:
        """Extract education summary from candidate data"""
        detailed_analysis = candidate["analysis"].get("detailed_analysis", {})
        education_relevance = detailed_analysis.get("education_relevance", "Education background not specified")
        return education_relevance