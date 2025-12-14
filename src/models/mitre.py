"""
MITRE ATT&CK for AI models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MITRETactic(str, Enum):
    """MITRE ATT&CK for AI Tactics"""
    # Initial Access
    INITIAL_ACCESS = "TA0001"
    
    # Execution
    EXECUTION = "TA0002"
    
    # Persistence
    PERSISTENCE = "TA0003"
    
    # Privilege Escalation
    PRIVILEGE_ESCALATION = "TA0004"
    
    # Defense Evasion
    DEFENSE_EVASION = "TA0005"
    
    # Credential Access
    CREDENTIAL_ACCESS = "TA0006"
    
    # Discovery
    DISCOVERY = "TA0007"
    
    # Lateral Movement
    LATERAL_MOVEMENT = "TA0008"
    
    # Collection
    COLLECTION = "TA0009"
    
    # Command and Control
    COMMAND_AND_CONTROL = "TA0011"
    
    # Exfiltration
    EXFILTRATION = "TA0010"
    
    # Impact
    IMPACT = "TA0040"
    
    # AI-Specific Tactics
    AI_MODEL_ACCESS = "TA0001-AI"
    AI_MODEL_EXPLOITATION = "TA0002-AI"
    AI_MODEL_POISONING = "TA0003-AI"
    AI_ADVERSARIAL_EXAMPLES = "TA0005-AI"


class MITRETechnique(BaseModel):
    """MITRE ATT&CK Technique"""
    technique_id: str  # e.g., "T1059.001"
    name: str
    description: str
    tactic: str
    subtechniques: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    
    # AI-Specific
    ai_related: bool = False
    ai_model_type: Optional[str] = None


class MITREMapping(BaseModel):
    """Mapping of threat to MITRE ATT&CK framework"""
    mapping_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    threat_profile_id: str
    
    # MITRE Mapping
    primary_tactic: str
    primary_technique: str
    additional_tactics: List[str] = Field(default_factory=list)
    additional_techniques: List[str] = Field(default_factory=list)
    
    # Mapping Confidence
    confidence_score: float = Field(ge=0.0, le=1.0)
    mapping_reason: str
    
    # Additional Context
    kill_chain_phase: Optional[str] = None
    ai_specific: bool = False
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Common MITRE ATT&CK for AI Techniques
COMMON_AI_TECHNIQUES = {
    "T1059.001-AI": {
        "technique_id": "T1059.001-AI",
        "name": "Command and Scripting Interpreter: Python for AI",
        "description": "Adversaries may use Python to interact with AI models",
        "tactic": "EXECUTION",
        "ai_related": True
    },
    "T1071.001-AI": {
        "technique_id": "T1071.001-AI",
        "name": "Application Layer Protocol: AI API Abuse",
        "description": "Adversaries may abuse AI APIs for malicious purposes",
        "tactic": "COMMAND_AND_CONTROL",
        "ai_related": True
    },
    "T1565.001-AI": {
        "technique_id": "T1565.001-AI",
        "name": "Data Manipulation: Model Poisoning",
        "description": "Adversaries may poison training data to compromise AI models",
        "tactic": "AI_MODEL_POISONING",
        "ai_related": True
    },
    "T1562.001-AI": {
        "technique_id": "T1562.001-AI",
        "name": "Impair Defenses: Adversarial Examples",
        "description": "Adversaries may use adversarial examples to evade AI-based detection",
        "tactic": "DEFENSE_EVASION",
        "ai_related": True
    }
}


