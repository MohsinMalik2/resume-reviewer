import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from typing import Dict, Any, Optional, List

# Global variables
db = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global db
    
    if firebase_admin._apps:
        # Already initialized
        db = firestore.client()
        return
    
    try:
        # Create credentials from environment variables
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
        }
        
        # Initialize Firebase
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        
        print("Firebase initialized successfully")
        
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        raise

def get_db():
    """Get Firestore database instance"""
    global db
    if db is None:
        initialize_firebase()
    return db

class FirebaseService:
    """Service class for Firebase operations"""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> str:
        """Create a new user in Firestore"""
        try:
            db = get_db()
            doc_ref = db.collection('users').document()
            user_data['id'] = doc_ref.id
            doc_ref.set(user_data)
            return doc_ref.id
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            db = get_db()
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = query.stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                return user_data
            
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            raise
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            db = get_db()
            doc_ref = db.collection('users').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                return user_data
            
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            raise
    
    @staticmethod
    def create_job(job_data: Dict[str, Any]) -> str:
        """Create a new job in Firestore"""
        try:
            db = get_db()
            doc_ref = db.collection('jobs').document()
            job_data['id'] = doc_ref.id
            doc_ref.set(job_data)
            return doc_ref.id
        except Exception as e:
            print(f"Error creating job: {e}")
            raise
    
    @staticmethod
    def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        try:
            db = get_db()
            doc_ref = db.collection('jobs').document(job_id)
            doc = doc_ref.get()
            
            if doc.exists:
                job_data = doc.to_dict()
                job_data['id'] = doc.id
                return job_data
            
            return None
        except Exception as e:
            print(f"Error getting job by ID: {e}")
            raise
    
    @staticmethod
    def get_jobs_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Get all jobs for a user"""
        try:
            db = get_db()
            jobs_ref = db.collection('jobs')
            query = jobs_ref.where('userId', '==', user_id).order_by('createdAt', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            
            jobs = []
            for doc in docs:
                job_data = doc.to_dict()
                job_data['id'] = doc.id
                jobs.append(job_data)
            
            return jobs
        except Exception as e:
            print(f"Error getting jobs by user: {e}")
            raise
    
    @staticmethod
    def create_candidates(candidates_data: List[Dict[str, Any]]) -> List[str]:
        """Create multiple candidates in Firestore"""
        try:
            db = get_db()
            batch = db.batch()
            candidate_ids = []
            
            for candidate_data in candidates_data:
                doc_ref = db.collection('candidates').document()
                candidate_data['id'] = doc_ref.id
                batch.set(doc_ref, candidate_data)
                candidate_ids.append(doc_ref.id)
            
            batch.commit()
            return candidate_ids
        except Exception as e:
            print(f"Error creating candidates: {e}")
            raise
    
    @staticmethod
    def get_candidates_by_job(job_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for a job"""
        try:
            db = get_db()
            candidates_ref = db.collection('candidates')
            query = candidates_ref.where('jobId', '==', job_id).order_by('score', direction=firestore.Query.DESCENDING)
            docs = query.stream()
            
            candidates = []
            for doc in docs:
                candidate_data = doc.to_dict()
                candidate_data['id'] = doc.id
                candidates.append(candidate_data)
            
            return candidates
        except Exception as e:
            print(f"Error getting candidates by job: {e}")
            raise
    
    @staticmethod
    def create_rejection_emails(emails_data: List[Dict[str, Any]]) -> List[str]:
        """Create multiple rejection emails in Firestore"""
        try:
            db = get_db()
            batch = db.batch()
            email_ids = []
            
            for email_data in emails_data:
                doc_ref = db.collection('rejection_emails').document()
                email_data['id'] = doc_ref.id
                batch.set(doc_ref, email_data)
                email_ids.append(doc_ref.id)
            
            batch.commit()
            return email_ids
        except Exception as e:
            print(f"Error creating rejection emails: {e}")
            raise
    
    @staticmethod
    def get_rejection_emails_by_job(job_id: str) -> List[Dict[str, Any]]:
        """Get all rejection emails for a job"""
        try:
            db = get_db()
            emails_ref = db.collection('rejection_emails')
            query = emails_ref.where('jobId', '==', job_id)
            docs = query.stream()
            
            emails = []
            for doc in docs:
                email_data = doc.to_dict()
                email_data['id'] = doc.id
                emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"Error getting rejection emails by job: {e}")
            raise