import google.generativeai as genai
import json
import re
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentResult

class ReasoningAgent(BaseAgent):
    """
    Agent 2: Reasoning Agent
    Responsible for analyzing extracted data, scoring candidates, and making decisions
    """
    
    def __init__(self, gemini_model):
        super().__init__()
        self.agent_type = "reasoning"
        self.model = gemini_model
        self.capabilities = [
            "resume_analysis",
            "candidate_scoring", 
            "requirement_matching",
            "decision_making",
            "ranking_generation"
        ]
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Analyze extracted resume data and make reasoning decisions
        
        Input: {
            "extracted_resumes": [...],
            "job_description": str,
            "job_requirements": {...}
        }
        
        Output: {
            "analyzed_candidates": [
                {
                    "candidate_id": str,
                    "analysis": {...},
                    "score": int,
                    "decision": "shortlist|reject",
                    "reasoning": str,
                    "strengths": [...],
                    "weaknesses": [...],
                    "fit_assessment": {...}
                }
            ],
            "ranking": [...],
            "statistics": {...}
        }
        """
        try:
            self.status = "reasoning"
            self.log_activity("Starting candidate analysis", {
                "candidate_count": len(input_data.get("extracted_resumes", []))
            })
            
            job_description = input_data.get("job_description", "")
            extracted_resumes = input_data.get("extracted_resumes", [])
            
            analyzed_candidates = []
            
            for resume_data in extracted_resumes:
                try:
                    # Perform deep analysis on each candidate
                    analysis_result = await self._analyze_candidate(
                        resume_data, 
                        job_description
                    )
                    
                    analyzed_candidates.append(analysis_result)
                    
                    self.log_activity("Candidate analyzed", {
                        "filename": resume_data["filename"],
                        "score": analysis_result["score"],
                        "decision": analysis_result["decision"]
                    })
                    
                except Exception as e:
                    self.log_activity("Candidate analysis failed", {
                        "filename": resume_data["filename"],
                        "error": str(e)
                    })
                    continue
            
            # Generate ranking and statistics
            ranking = self._generate_ranking(analyzed_candidates)
            statistics = self._calculate_statistics(analyzed_candidates)
            
            self.status = "completed"
            
            return AgentResult(
                success=True,
                data={
                    "analyzed_candidates": analyzed_candidates,
                    "ranking": ranking,
                    "statistics": statistics
                },
                metadata={
                    "total_analyzed": len(analyzed_candidates),
                    "shortlisted": len([c for c in analyzed_candidates if c["decision"] == "shortlist"]),
                    "rejected": len([c for c in analyzed_candidates if c["decision"] == "reject"]),
                    "agent_type": self.agent_type
                }
            )
            
        except Exception as e:
            self.status = "failed"
            self.log_activity("Reasoning failed", {"error": str(e)})
            return AgentResult(success=False, error=str(e))
    
    async def _analyze_candidate(self, resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a single candidate"""
        
        # Prepare analysis prompt for Gemini
        analysis_prompt = self._create_analysis_prompt(resume_data, job_description)
        
        try:
            # Get AI analysis
            response = self.model.generate_content(analysis_prompt)
            ai_analysis = self._parse_ai_response(response.text)
            
            # Enhance with rule-based analysis
            rule_based_analysis = self._rule_based_analysis(resume_data, job_description)
            
            # Combine AI and rule-based analysis
            final_analysis = self._combine_analyses(ai_analysis, rule_based_analysis)
            
            # Make final decision
            decision = "shortlist" if final_analysis["score"] >= 75 else "reject"
            
            return {
                "candidate_id": resume_data["file_id"],
                "filename": resume_data["filename"],
                "analysis": final_analysis,
                "score": final_analysis["score"],
                "decision": decision,
                "reasoning": final_analysis["reasoning"],
                "strengths": final_analysis["strengths"],
                "weaknesses": final_analysis["weaknesses"],
                "fit_assessment": final_analysis["fit_assessment"],
                "candidate_info": final_analysis["candidate_info"],
                "analysis_metadata": {
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "ai_confidence": final_analysis.get("confidence", 0.8),
                    "analysis_method": "hybrid_ai_rule_based"
                }
            }
            
        except Exception as e:
            # Fallback to rule-based analysis only
            self.log_activity("AI analysis failed, using rule-based fallback", {"error": str(e)})
            return self._fallback_analysis(resume_data, job_description)
    
    def _create_analysis_prompt(self, resume_data: Dict[str, Any], job_description: str) -> str:
        """Create comprehensive analysis prompt for Gemini AI"""
        
        raw_text = resume_data["raw_text"]
        structured_data = resume_data["structured_data"]
        
        prompt = f"""
You are an expert HR recruiter and talent acquisition specialist. Analyze this resume against the job description and provide a comprehensive assessment.

JOB DESCRIPTION:
{job_description}

RESUME CONTENT:
{raw_text}

STRUCTURED DATA EXTRACTED:
- Contact Info: {structured_data.get('contact_info', {})}
- Skills Found: {structured_data.get('skills', [])}
- Experience Indicators: {structured_data.get('experience', {})}
- Education: {structured_data.get('education', [])}

Please provide a detailed analysis in the following JSON format:

{{
    "candidate_info": {{
        "name": "Full name of candidate",
        "email": "Email address",
        "phone": "Phone number if available",
        "location": "Location if mentioned"
    }},
    "score": 85,
    "reasoning": "Detailed explanation of the score and decision",
    "strengths": ["List", "of", "candidate", "strengths"],
    "weaknesses": ["List", "of", "areas", "for", "improvement"],
    "fit_assessment": {{
        "technical_fit": 90,
        "experience_fit": 80,
        "cultural_fit": 85,
        "overall_fit": 85
    }},
    "detailed_analysis": {{
        "technical_skills": "Assessment of technical capabilities",
        "experience_level": "Years and quality of experience",
        "education_relevance": "How education aligns with role",
        "career_progression": "Analysis of career growth",
        "achievements": "Notable accomplishments mentioned"
    }},
    "red_flags": ["Any", "concerns", "or", "issues"],
    "recommendation": "Strong recommendation with specific reasons",
    "confidence": 0.9
}}

SCORING CRITERIA:
- Technical Skills Match (30%): How well do their skills align with job requirements?
- Experience Relevance (25%): Years and quality of relevant experience
- Education Background (15%): Educational qualifications and relevance
- Career Progression (15%): Growth trajectory and achievements
- Cultural Fit Indicators (15%): Communication, leadership, teamwork signs

Score Range:
- 90-100: Exceptional candidate, perfect fit
- 80-89: Strong candidate, very good fit
- 70-79: Good candidate, decent fit
- 60-69: Average candidate, some concerns
- Below 60: Poor fit, significant gaps

Provide only the JSON response, no additional text.
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in AI response")
                
        except Exception as e:
            self.log_activity("AI response parsing failed", {"error": str(e)})
            return self._create_fallback_ai_analysis()
    
    def _rule_based_analysis(self, resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Perform rule-based analysis as backup/enhancement"""
        
        structured_data = resume_data["structured_data"]
        raw_text = resume_data["raw_text"].lower()
        job_desc_lower = job_description.lower()
        
        # Calculate skill match percentage
        skills_found = structured_data.get("skills", [])
        skill_match_score = self._calculate_skill_match(skills_found, job_desc_lower)
        
        # Calculate experience score
        experience_data = structured_data.get("experience", {})
        experience_score = self._calculate_experience_score(experience_data, job_desc_lower)
        
        # Calculate education score
        education_data = structured_data.get("education", [])
        education_score = self._calculate_education_score(education_data, job_desc_lower)
        
        # Calculate overall score
        overall_score = int(
            skill_match_score * 0.4 + 
            experience_score * 0.35 + 
            education_score * 0.25
        )
        
        return {
            "score": overall_score,
            "skill_match_score": skill_match_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "analysis_method": "rule_based"
        }
    
    def _calculate_skill_match(self, skills_found: List[str], job_description: str) -> int:
        """Calculate skill match percentage"""
        if not skills_found:
            return 30  # Base score for no skills detected
        
        skill_matches = 0
        for skill in skills_found:
            if skill.lower() in job_description:
                skill_matches += 1
        
        # Calculate percentage with bonus for multiple matches
        match_percentage = min(100, (skill_matches / max(len(skills_found), 1)) * 100)
        
        # Bonus for having many relevant skills
        if skill_matches >= 5:
            match_percentage = min(100, match_percentage + 10)
        
        return int(match_percentage)
    
    def _calculate_experience_score(self, experience_data: Dict[str, Any], job_description: str) -> int:
        """Calculate experience relevance score"""
        max_years = experience_data.get("max_years", 0)
        job_titles = experience_data.get("job_titles_found", [])
        
        # Base score from years of experience
        if max_years >= 5:
            years_score = 90
        elif max_years >= 3:
            years_score = 75
        elif max_years >= 1:
            years_score = 60
        else:
            years_score = 40
        
        # Bonus for relevant job titles
        title_bonus = 0
        for title in job_titles:
            if title.lower() in job_description:
                title_bonus += 5
        
        return min(100, years_score + title_bonus)
    
    def _calculate_education_score(self, education_data: List[str], job_description: str) -> int:
        """Calculate education relevance score"""
        if not education_data:
            return 50  # Neutral score for no education detected
        
        education_score = 60  # Base score for having education
        
        # Check for relevant degrees
        relevant_terms = ['computer', 'engineering', 'science', 'technology', 'business']
        for edu in education_data:
            for term in relevant_terms:
                if term in edu.lower() and term in job_description:
                    education_score += 10
        
        # Check for advanced degrees
        advanced_degrees = ['master', 'phd', 'doctorate', 'mba']
        for edu in education_data:
            if any(degree in edu.lower() for degree in advanced_degrees):
                education_score += 15
                break
        
        return min(100, education_score)
    
    def _combine_analyses(self, ai_analysis: Dict[str, Any], rule_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine AI and rule-based analyses"""
        
        # Weight AI analysis more heavily if available
        if ai_analysis.get("score"):
            final_score = int(ai_analysis["score"] * 0.7 + rule_analysis["score"] * 0.3)
        else:
            final_score = rule_analysis["score"]
        
        # Combine the best of both analyses
        combined = {
            "score": final_score,
            "reasoning": ai_analysis.get("reasoning", f"Rule-based analysis score: {rule_analysis['score']}"),
            "strengths": ai_analysis.get("strengths", ["Technical skills match", "Relevant experience"]),
            "weaknesses": ai_analysis.get("weaknesses", ["Areas for improvement identified"]),
            "fit_assessment": ai_analysis.get("fit_assessment", {
                "technical_fit": rule_analysis["skill_match_score"],
                "experience_fit": rule_analysis["experience_score"],
                "education_fit": rule_analysis["education_score"],
                "overall_fit": final_score
            }),
            "candidate_info": ai_analysis.get("candidate_info", {
                "name": "Candidate Name",
                "email": "email@example.com"
            }),
            "detailed_analysis": ai_analysis.get("detailed_analysis", {}),
            "confidence": ai_analysis.get("confidence", 0.8)
        }
        
        return combined
    
    def _fallback_analysis(self, resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Fallback analysis when AI fails"""
        rule_analysis = self._rule_based_analysis(resume_data, job_description)
        
        decision = "shortlist" if rule_analysis["score"] >= 75 else "reject"
        
        # Add candidate_info to rule_analysis
        rule_analysis["candidate_info"] = {
            "name": "Candidate",
            "email": "email@example.com"
        }
        
        return {
            "candidate_id": resume_data["file_id"],
            "filename": resume_data["filename"],
            "analysis": rule_analysis,
            "score": rule_analysis["score"],
            "decision": decision,
            "reasoning": f"Rule-based analysis: Score {rule_analysis['score']}/100",
            "strengths": ["Skills identified", "Experience detected"],
            "weaknesses": ["Detailed analysis unavailable"],
            "fit_assessment": {
                "overall_fit": rule_analysis["score"]
            }
        }
    
    def _create_fallback_ai_analysis(self) -> Dict[str, Any]:
        """Create fallback AI analysis structure"""
        return {
            "score": 65,
            "reasoning": "Analysis completed with limited data",
            "strengths": ["Resume submitted", "Basic qualifications"],
            "weaknesses": ["Detailed analysis unavailable"],
            "fit_assessment": {"overall_fit": 65},
            "candidate_info": {"name": "Candidate", "email": "email@example.com"},
            "confidence": 0.5
        }
    
    def _generate_ranking(self, analyzed_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate ranked list of candidates"""
        # Sort by score (descending)
        sorted_candidates = sorted(
            analyzed_candidates, 
            key=lambda x: x["score"], 
            reverse=True
        )
        
        ranking = []
        for i, candidate in enumerate(sorted_candidates):
            ranking.append({
                "rank": i + 1,
                "candidate_id": candidate["candidate_id"],
                "filename": candidate["filename"],
                "score": candidate["score"],
                "decision": candidate["decision"],
                "tier": self._get_candidate_tier(candidate["score"])
            })
        
        return ranking
    
    def _get_candidate_tier(self, score: int) -> str:
        """Categorize candidate into tiers"""
        if score >= 90:
            return "exceptional"
        elif score >= 80:
            return "strong"
        elif score >= 70:
            return "good"
        elif score >= 60:
            return "average"
        else:
            return "poor"
    
    def _calculate_statistics(self, analyzed_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate analysis statistics"""
        if not analyzed_candidates:
            return {}
        
        scores = [c["score"] for c in analyzed_candidates]
        shortlisted = [c for c in analyzed_candidates if c["decision"] == "shortlist"]
        rejected = [c for c in analyzed_candidates if c["decision"] == "reject"]
        
        return {
            "total_candidates": len(analyzed_candidates),
            "shortlisted_count": len(shortlisted),
            "rejected_count": len(rejected),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "shortlist_rate": len(shortlisted) / len(analyzed_candidates) * 100,
            "score_distribution": {
                "exceptional": len([s for s in scores if s >= 90]),
                "strong": len([s for s in scores if 80 <= s < 90]),
                "good": len([s for s in scores if 70 <= s < 80]),
                "average": len([s for s in scores if 60 <= s < 70]),
                "poor": len([s for s in scores if s < 60])
            }
        }