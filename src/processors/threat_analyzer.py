"""
Threat Analyzer using Vertex AI
"""

import json
import uuid
from typing import Dict, Any, List
from datetime import datetime

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("Warning: Vertex AI not available. Using mock analysis.")

from src.config import Config
from src.models.threat import ThreatProfile, ThreatType, ThreatSeverity, ThreatEvent
from src.utils.logger import setup_logger

logger = setup_logger("threat_analyzer")


class ThreatAnalyzer:
    """Analyzes threats using Vertex AI"""
    
    def __init__(self):
        """Initialize the threat analyzer"""
        self.config = Config
        self.logger = logger
        
        if VERTEX_AI_AVAILABLE:
            try:
                import os
                
                # Check if credentials file exists and is valid
                creds_path = Config.GOOGLE_APPLICATION_CREDENTIALS
                use_adc = False
                old_creds = None
                
                if creds_path and os.path.exists(creds_path):
                    file_size = os.path.getsize(creds_path)
                    if file_size == 0:
                        # Empty file - use ADC instead
                        self.logger.info("Credentials file is empty, using Application Default Credentials")
                        use_adc = True
                        # Temporarily unset to force ADC
                        old_creds = os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
                elif not creds_path:
                    # No file specified - use ADC
                    use_adc = True
                    self.logger.info("No credentials file specified, using Application Default Credentials")
                
                try:
                    vertexai.init(
                        project=Config.GOOGLE_CLOUD_PROJECT,
                        location=Config.VERTEX_AI_LOCATION
                    )
                    self.model = GenerativeModel(Config.GEMINI_MODEL)
                    
                    if use_adc:
                        self.logger.info("✅ Vertex AI initialized with ADC")
                    else:
                        self.logger.info("✅ Vertex AI initialized with service account key")
                        
                finally:
                    # Restore env var if we removed it
                    if use_adc and old_creds:
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = old_creds
                        
            except Exception as e:
                self.logger.error(f"Failed to initialize Vertex AI: {e}")
                self.logger.warning("Falling back to mock analysis")
                self.model = None
        else:
            self.model = None
    
    def analyze_telemetry(self, telemetry_data: Dict[str, Any]) -> ThreatEvent:
        """
        Analyze telemetry data for threats
        
        Args:
            telemetry_data: Telemetry event data
            
        Returns:
            ThreatEvent if threat detected, None otherwise
        """
        try:
            # Prepare prompt for Vertex AI
            prompt = self._create_telemetry_prompt(telemetry_data)
            
            # Get AI analysis
            analysis = self._get_ai_analysis(prompt)
            
            # Parse AI response
            threat_event = self._parse_analysis(analysis, telemetry_data, "telemetry")
            
            return threat_event
            
        except Exception as e:
            self.logger.error(f"Error analyzing telemetry: {e}")
            return None
    
    def analyze_code_sample(self, code_data: Dict[str, Any]) -> ThreatEvent:
        """
        Analyze code sample for malicious patterns
        
        Args:
            code_data: Code sample data
            
        Returns:
            ThreatEvent if threat detected, None otherwise
        """
        try:
            prompt = self._create_code_analysis_prompt(code_data)
            analysis = self._get_ai_analysis(prompt)
            threat_event = self._parse_analysis(analysis, code_data, "code_sample")
            
            return threat_event
            
        except Exception as e:
            self.logger.error(f"Error analyzing code sample: {e}")
            return None
    
    def analyze_darkweb_feed(self, feed_data: Dict[str, Any]) -> ThreatEvent:
        """
        Analyze dark web feed for threat intelligence
        
        Args:
            feed_data: Dark web feed data
            
        Returns:
            ThreatEvent if threat detected, None otherwise
        """
        try:
            prompt = self._create_darkweb_prompt(feed_data)
            analysis = self._get_ai_analysis(prompt)
            threat_event = self._parse_analysis(analysis, feed_data, "darkweb")
            
            return threat_event
            
        except Exception as e:
            self.logger.error(f"Error analyzing dark web feed: {e}")
            return None
    
    def create_threat_profile(
        self,
        threat_events: List[ThreatEvent]
    ) -> ThreatProfile:
        """
        Create comprehensive threat profile from multiple events
        
        Args:
            threat_events: List of related threat events
            
        Returns:
            ThreatProfile
        """
        if not threat_events:
            return None
        
        # Aggregate threat information
        primary_event = threat_events[0]
        event_ids = [e.event_id for e in threat_events]
        
        # Use AI to create comprehensive profile
        prompt = self._create_profile_prompt(threat_events)
        ai_analysis = self._get_ai_analysis(prompt)
        
        # Parse AI response
        profile_data = self._parse_profile_analysis(ai_analysis, threat_events)
        
        profile = ThreatProfile(
            profile_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            threat_type=primary_event.threat_type,
            severity=primary_event.severity,
            confidence_score=primary_event.confidence_score,
            ai_analysis=profile_data.get("analysis", {}),
            behavioral_patterns=profile_data.get("behavioral_patterns", []),
            indicators_of_compromise=profile_data.get("iocs", []),
            autonomous_system_indicators=profile_data.get("autonomous_indicators", []),
            source_events=event_ids,
            metadata={"ai_model": Config.GEMINI_MODEL}
        )
        
        return profile
    
    def _get_ai_analysis(self, prompt: str) -> Dict[str, Any]:
        """
        Get analysis from Vertex AI
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            AI analysis response
        """
        if not self.model:
            # Mock response for testing
            return self._mock_analysis()
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON response from AI
            # AI should return structured JSON
            response_text = response.text
            
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]
            
            return json.loads(response_text)
            
        except Exception as e:
            self.logger.error(f"Error getting AI analysis: {e}")
            return self._mock_analysis()
    
    def _create_telemetry_prompt(self, telemetry: Dict[str, Any]) -> str:
        """Create prompt for telemetry analysis"""
        return f"""Analyze this network telemetry data for security threats:

{json.dumps(telemetry, indent=2)}

Return a JSON response with:
{{
    "is_threat": boolean,
    "threat_type": "malware|exploit|phishing|ddos|unauthorized_access|ai_powered_attack|autonomous_hacking|unknown",
    "severity": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "description": "brief description",
    "indicators": ["list of indicators"],
    "autonomous_system_indicators": ["signs of automated/autonomous behavior"]
}}"""
    
    def _create_code_analysis_prompt(self, code: Dict[str, Any]) -> str:
        """Create prompt for code analysis"""
        code_content = code.get("code_content", "")[:2000]  # Limit length
        return f"""Analyze this code sample for malicious patterns:

Code:
{code_content}

Language: {code.get('language', 'unknown')}
Source: {code.get('source', 'unknown')}

Return a JSON response with:
{{
    "is_threat": boolean,
    "threat_type": "malware|exploit|phishing|ddos|data_exfiltration|unauthorized_access|ai_powered_attack|autonomous_hacking|unknown",
    "severity": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "description": "brief description",
    "malicious_patterns": ["list of patterns found"],
    "autonomous_system_indicators": ["signs of automated/autonomous behavior"]
}}"""
    
    def _create_darkweb_prompt(self, feed: Dict[str, Any]) -> str:
        """Create prompt for dark web feed analysis"""
        content = feed.get("content", "")[:2000]
        return f"""Analyze this dark web feed for threat intelligence:

Content:
{content}

Keywords: {', '.join(feed.get('keywords', []))}

Return a JSON response with:
{{
    "is_threat": boolean,
    "threat_type": "malware|exploit|phishing|ddos|data_exfiltration|unauthorized_access|ai_powered_attack|autonomous_hacking|unknown",
    "severity": "low|medium|high|critical",
    "confidence": 0.0-1.0,
    "description": "brief description",
    "threat_indicators": ["list of threat indicators"],
    "autonomous_system_indicators": ["signs of automated/autonomous behavior"]
}}"""
    
    def _create_profile_prompt(self, events: List[ThreatEvent]) -> str:
        """Create prompt for threat profile generation"""
        events_summary = [{
            "event_id": e.event_id,
            "threat_type": e.threat_type.value,
            "severity": e.severity.value,
            "description": e.description
        } for e in events]
        
        return f"""Analyze these related threat events and create a comprehensive threat profile:

Events:
{json.dumps(events_summary, indent=2)}

Return a JSON response with:
{{
    "analysis": {{
        "summary": "comprehensive threat analysis",
        "attack_vector": "description of attack vector",
        "target": "likely targets"
    }},
    "behavioral_patterns": ["list of behavioral patterns"],
    "iocs": ["indicators of compromise"],
    "autonomous_indicators": ["signs of autonomous hacking system"]
}}"""
    
    def _parse_analysis(
        self,
        analysis: Dict[str, Any],
        source_data: Dict[str, Any],
        source_type: str
    ) -> ThreatEvent:
        """Parse AI analysis into ThreatEvent"""
        if not analysis.get("is_threat", False):
            return None
        
        return ThreatEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            threat_type=ThreatType(analysis.get("threat_type", "unknown")),
            severity=ThreatSeverity(analysis.get("severity", "low")),
            source=source_type,
            confidence_score=float(analysis.get("confidence", 0.5)),
            description=analysis.get("description", "Threat detected"),
            raw_data=source_data,
            metadata={"ai_analysis": analysis}
        )
    
    def _parse_profile_analysis(
        self,
        analysis: Dict[str, Any],
        events: List[ThreatEvent]
    ) -> Dict[str, Any]:
        """Parse profile analysis"""
        return {
            "analysis": analysis.get("analysis", {}),
            "behavioral_patterns": analysis.get("behavioral_patterns", []),
            "iocs": analysis.get("iocs", []),
            "autonomous_indicators": analysis.get("autonomous_indicators", [])
        }
    
    def _mock_analysis(self) -> Dict[str, Any]:
        """Mock analysis for testing when Vertex AI is unavailable"""
        return {
            "is_threat": True,
            "threat_type": "autonomous_hacking",
            "severity": "high",
            "confidence": 0.75,
            "description": "Mock threat detected - autonomous system indicators present",
            "indicators": ["automated_pattern", "rapid_execution"],
            "autonomous_system_indicators": ["high_frequency", "pattern_based"]
        }


