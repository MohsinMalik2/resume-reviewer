from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import uuid

class BaseAgent(ABC):
    """Base class for all AI agents in the system"""
    
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.status = "initialized"
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None):
        """Log agent activity for monitoring"""
        print(f"[{self.agent_id}] {activity}: {details or ''}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "created_at": self.created_at
        }

class AgentResult:
    """Standard result format for agent communication"""
    
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }