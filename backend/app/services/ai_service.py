import google.generativeai as genai
import os
import json
import re
from typing import Dict, Any, List
from datetime import datetime

# Global variables
model = None

def initialize_gemini():
    """Initialize Google Gemini AI"""
    global model
    
    try:
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        print("Gemini AI initialized successfully")
        
    except Exception as e:
        print(f"Error initializing Gemini AI: {e}")
        raise

def get_model():
    """Get Gemini model instance"""
    global model
    if model is None:
        initialize_gemini()
    return model

class AIService:
    """Service class for AI operations"""
    
    @staticmethod
    def analyze_resume(resume_text: str, job_description: str, file_name: str) -> Dict[str, Any]:
        """Analyze a resume against job description using Gemini AI"""
        try:
            model = get_model()
            
            prompt = f"""
You are an expert HR recruiter. Analyze this resume against the job description and provide a detailed assessment.

Job Description:
{job_description}

Resume Content:
{resume_text}

File Name: {file_name}

Please analyze the resume and provide a JSON response with the following structure:
{{
    "candidate_name": "Full name of the candidate",
    "email": "Email address (extract from resume, if not found use 'not_provided@email.com')",
    "phone": "Phone number (if available, otherwise null)",
    "experience_years": "Years of relevant experience (e.g., '3 years', '5+ years')",
    "skills": ["Array", "of", "technical", "skills", "mentioned"],
    "education": "Highest education level (if mentioned)",
    "location": "Current location (if mentioned, otherwise null)",
    "fit_score": 85,
    "summary": "2-3 sentence summary of candidate fit and strengths",
    "rejection_reason": "If score < 80, explain why in 1-2 sentences (for rejection email)"
}}

Important guidelines:
- fit_score should be 0-100 based on how well the candidate matches the job requirements
- Consider experience, skills, education, and overall fit
- Be realistic with scoring - not everyone should get high scores
- Extract actual information from the resume, don't make up details
- If email is not found in resume, use format: firstname.lastname@email.com
- Skills should be actual technical skills mentioned in the resume
- Summary should highlight why this candidate is/isn't a good fit

Provide only the JSON response, no additional text.
"""

            response = model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    result = json.loads(json_str)
                    
                    # Validate and clean the result
                    result = AIService._validate_analysis_result(result, file_name)
                    return result
                    
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Response text: {response_text}")
                    return AIService._create_fallback_result(file_name)
            else:
                print(f"No JSON found in response: {response_text}")
                return AIService._create_fallback_result(file_name)
                
        except Exception as e:
            print(f"Error analyzing resume with AI: {e}")
            return AIService._create_fallback_result(file_name)
    
    @staticmethod
    def _validate_analysis_result(result: Dict[str, Any], file_name: str) -> Dict[str, Any]:
        """Validate and clean AI analysis result"""
        
        # Ensure required fields exist with defaults
        validated_result = {
            "candidate_name": result.get("candidate_name", "Unknown Candidate"),
            "email": result.get("email", "not_provided@email.com"),
            "phone": result.get("phone"),
            "experience_years": result.get("experience_years", "Not specified"),
            "skills": result.get("skills", []),
            "education": result.get("education"),
            "location": result.get("location"),
            "fit_score": max(0, min(100, int(result.get("fit_score", 50)))),  # Ensure 0-100
            "summary": result.get("summary", "Analysis pending"),
            "rejection_reason": result.get("rejection_reason", "Does not meet minimum requirements")
        }
        
        # Ensure skills is a list
        if not isinstance(validated_result["skills"], list):
            validated_result["skills"] = []
        
        # Ensure email format
        email = validated_result["email"]
        if not email or email == "not_provided@email.com":
            # Try to create email from candidate name
            name = validated_result["candidate_name"].lower().replace(" ", ".")
            validated_result["email"] = f"{name}@email.com"
        
        return validated_result
    
    @staticmethod
    def _create_fallback_result(file_name: str) -> Dict[str, Any]:
        """Create fallback result when AI analysis fails"""
        return {
            "candidate_name": "Unknown Candidate",
            "email": "not_provided@email.com",
            "phone": None,
            "experience_years": "Not specified",
            "skills": [],
            "education": None,
            "location": None,
            "fit_score": 50,
            "summary": "Resume analysis failed, manual review required",
            "rejection_reason": "Unable to process resume automatically"
        }
    
    @staticmethod
    def generate_rejection_email(candidate_name: str, job_description: str, rejection_reason: str) -> Dict[str, str]:
        """Generate personalized rejection email using Gemini AI"""
        try:
            model = get_model()
            
            # Extract job title from job description (first few words)
            job_title = " ".join(job_description.split()[:5]) + " Position"
            
            prompt = f"""
Generate a professional, empathetic rejection email for a job candidate.

Candidate Name: {candidate_name}
Job Title: {job_title}
Rejection Reason: {rejection_reason}

Create a professional rejection email with:
1. A personalized subject line
2. A warm, respectful tone
3. Brief feedback based on the rejection reason
4. Encouragement for future applications
5. Professional closing

Provide the response in JSON format:
{{
    "subject": "Subject line for the email",
    "content": "Full email content with proper formatting"
}}

The email should be professional, empathetic, and constructive. Avoid being too specific about weaknesses.
"""

            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                try:
                    result = json.loads(json_str)
                    return {
                        "subject": result.get("subject", f"Thank you for your application - {job_title}"),
                        "content": result.get("content", AIService._create_fallback_email(candidate_name, job_title))
                    }
                except json.JSONDecodeError:
                    return AIService._create_fallback_email_dict(candidate_name, job_title)
            else:
                return AIService._create_fallback_email_dict(candidate_name, job_title)
                
        except Exception as e:
            print(f"Error generating rejection email: {e}")
            return AIService._create_fallback_email_dict(candidate_name, job_title)
    
    @staticmethod
    def _create_fallback_email_dict(candidate_name: str, job_title: str) -> Dict[str, str]:
        """Create fallback rejection email dictionary"""
        return {
            "subject": f"Thank you for your application - {job_title}",
            "content": AIService._create_fallback_email(candidate_name, job_title)
        }
    
    @staticmethod
    def _create_fallback_email(candidate_name: str, job_title: str) -> str:
        """Create fallback rejection email content"""
        return f"""Dear {candidate_name},

Thank you for taking the time to apply for the {job_title} at our company. We appreciate your interest in joining our team.

After careful review of your application and qualifications, we have decided to move forward with other candidates whose experience more closely aligns with our current requirements.

We were impressed by your background and encourage you to apply for future opportunities that may be a better fit for your skills and experience.

Thank you again for your interest in our company.

Best regards,
HR Team"""