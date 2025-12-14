"""
MITRE ATT&CK Mapper
Maps threats to MITRE ATT&CK for AI framework
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

from src.models.threat import ThreatProfile, ThreatType
from src.models.mitre import MITREMapping, MITRETactic, COMMON_AI_TECHNIQUES
from src.utils.logger import setup_logger

logger = setup_logger("mitre_mapper")


class MITREMapper:
    """Maps threats to MITRE ATT&CK for AI framework"""
    
    def __init__(self):
        """Initialize the MITRE mapper"""
        self.logger = logger
        self.ai_techniques = COMMON_AI_TECHNIQUES
    
    def map_threat_profile(self, profile: ThreatProfile) -> MITREMapping:
        """
        Map threat profile to MITRE ATT&CK framework
        
        Args:
            profile: ThreatProfile to map
            
        Returns:
            MITREMapping
        """
        # Determine primary tactic and technique based on threat type
        tactic, technique = self._determine_mitre_mapping(profile)
        
        # Get additional mappings
        additional_tactics, additional_techniques = self._get_additional_mappings(profile)
        
        # Determine if AI-specific
        is_ai_specific = self._is_ai_specific_threat(profile)
        
        # Create mapping
        mapping = MITREMapping(
            mapping_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            threat_profile_id=profile.profile_id,
            primary_tactic=tactic,
            primary_technique=technique,
            additional_tactics=additional_tactics,
            additional_techniques=additional_techniques,
            confidence_score=profile.confidence_score,
            mapping_reason=self._generate_mapping_reason(profile, tactic, technique),
            kill_chain_phase=self._determine_kill_chain_phase(tactic),
            ai_specific=is_ai_specific,
            metadata={
                "threat_type": profile.threat_type.value,
                "severity": profile.severity.value
            }
        )
        
        return mapping
    
    def _determine_mitre_mapping(
        self,
        profile: ThreatProfile
    ) -> tuple[str, str]:
        """
        Determine primary MITRE tactic and technique
        
        Args:
            profile: ThreatProfile
            
        Returns:
            Tuple of (tactic, technique)
        """
        threat_type = profile.threat_type
        
        # Mapping logic based on threat type
        mapping_rules = {
            ThreatType.MALWARE: (MITRETactic.EXECUTION.value, "T1059.001"),
            ThreatType.EXPLOIT: (MITRETactic.INITIAL_ACCESS.value, "T1190"),
            ThreatType.PHISHING: (MITRETactic.INITIAL_ACCESS.value, "T1566"),
            ThreatType.DDoS: (MITRETactic.IMPACT.value, "T1498"),
            ThreatType.DATA_EXFILTRATION: (MITRETactic.EXFILTRATION.value, "T1041"),
            ThreatType.UNAUTHORIZED_ACCESS: (MITRETactic.INITIAL_ACCESS.value, "T1078"),
            ThreatType.AI_POWERED_ATTACK: (MITRETactic.AI_MODEL_EXPLOITATION.value, "T1059.001-AI"),
            ThreatType.AUTONOMOUS_HACKING: (MITRETactic.AI_MODEL_EXPLOITATION.value, "T1059.001-AI"),
        }
        
        tactic, technique = mapping_rules.get(
            threat_type,
            (MITRETactic.EXECUTION.value, "T1059")
        )
        
        # Check for autonomous system indicators
        if profile.autonomous_system_indicators:
            if threat_type in [ThreatType.AI_POWERED_ATTACK, ThreatType.AUTONOMOUS_HACKING]:
                technique = "T1059.001-AI"
            tactic = MITRETactic.AI_MODEL_EXPLOITATION.value
        
        return tactic, technique
    
    def _get_additional_mappings(
        self,
        profile: ThreatProfile
    ) -> tuple[List[str], List[str]]:
        """
        Get additional MITRE tactics and techniques
        
        Args:
            profile: ThreatProfile
            
        Returns:
            Tuple of (additional_tactics, additional_techniques)
        """
        additional_tactics = []
        additional_techniques = []
        
        # Add based on behavioral patterns
        if "persistence" in str(profile.behavioral_patterns).lower():
            additional_tactics.append(MITRETactic.PERSISTENCE.value)
            additional_techniques.append("T1543")
        
        if "evasion" in str(profile.behavioral_patterns).lower():
            additional_tactics.append(MITRETactic.DEFENSE_EVASION.value)
            additional_techniques.append("T1562.001-AI")  # Adversarial examples
        
        if "credential" in str(profile.indicators_of_compromise).lower():
            additional_tactics.append(MITRETactic.CREDENTIAL_ACCESS.value)
            additional_techniques.append("T1110")
        
        return additional_tactics, additional_techniques
    
    def _is_ai_specific_threat(self, profile: ThreatProfile) -> bool:
        """Determine if threat is AI-specific"""
        ai_indicators = [
            ThreatType.AI_POWERED_ATTACK,
            ThreatType.AUTONOMOUS_HACKING
        ]
        
        if profile.threat_type in ai_indicators:
            return True
        
        if profile.autonomous_system_indicators:
            return True
        
        # Check behavioral patterns
        ai_keywords = ["ai", "ml", "model", "autonomous", "automated", "neural"]
        patterns_str = " ".join(profile.behavioral_patterns).lower()
        
        return any(keyword in patterns_str for keyword in ai_keywords)
    
    def _determine_kill_chain_phase(self, tactic: str) -> str:
        """Determine kill chain phase from tactic"""
        phase_mapping = {
            MITRETactic.INITIAL_ACCESS.value: "Initial Access",
            MITRETactic.EXECUTION.value: "Execution",
            MITRETactic.PERSISTENCE.value: "Persistence",
            MITRETactic.PRIVILEGE_ESCALATION.value: "Privilege Escalation",
            MITRETactic.DEFENSE_EVASION.value: "Defense Evasion",
            MITRETactic.CREDENTIAL_ACCESS.value: "Credential Access",
            MITRETactic.DISCOVERY.value: "Discovery",
            MITRETactic.LATERAL_MOVEMENT.value: "Lateral Movement",
            MITRETactic.COLLECTION.value: "Collection",
            MITRETactic.COMMAND_AND_CONTROL.value: "Command and Control",
            MITRETactic.EXFILTRATION.value: "Exfiltration",
            MITRETactic.IMPACT.value: "Impact",
        }
        
        return phase_mapping.get(tactic, "Unknown")
    
    def _generate_mapping_reason(
        self,
        profile: ThreatProfile,
        tactic: str,
        technique: str
    ) -> str:
        """Generate human-readable mapping reason"""
        reason = f"Mapped to {tactic} / {technique} based on "
        reason += f"threat type: {profile.threat_type.value}, "
        reason += f"severity: {profile.severity.value}"
        
        if profile.autonomous_system_indicators:
            reason += ", autonomous system indicators detected"
        
        return reason


