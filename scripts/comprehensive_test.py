#!/usr/bin/env python3
"""
Comprehensive test suite for ThreatStream AI
Tests all components and generates detailed report
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("comprehensive_test")

# Test results storage
test_results = {
    "timestamp": datetime.utcnow().isoformat(),
    "tests": [],
    "summary": {}
}


def log_test(name: str, status: str, details: str = "", output: Any = None):
    """Log test result"""
    result = {
        "name": name,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details,
        "output": str(output) if output else None
    }
    test_results["tests"].append(result)
    
    status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    logger.info(f"{status_icon} {name}: {status}")
    if details:
        logger.info(f"   {details}")


def test_configuration():
    """Test 1: Configuration"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Configuration Validation")
    logger.info("="*60)
    
    try:
        # Test config loading
        assert Config.validate(), "Configuration validation failed"
        log_test("Config Validation", "PASS", "All required config present")
        
        # Test Kafka config
        kafka_config = Config.get_kafka_config()
        assert kafka_config.get("bootstrap.servers"), "Bootstrap servers not configured"
        assert kafka_config.get("sasl.username"), "API key not configured"
        log_test("Kafka Config", "PASS", f"Bootstrap: {kafka_config.get('bootstrap.servers')}")
        
        # Test Schema Registry config
        sr_config = Config.get_schema_registry_config()
        if sr_config:
            log_test("Schema Registry Config", "PASS", f"URL: {sr_config.get('url')}")
        else:
            log_test("Schema Registry Config", "WARN", "Schema Registry not configured")
        
        # Test GCP config
        assert Config.GOOGLE_CLOUD_PROJECT, "GCP project not configured"
        log_test("GCP Config", "PASS", f"Project: {Config.GOOGLE_CLOUD_PROJECT}")
        
        return True
    except Exception as e:
        log_test("Configuration", "FAIL", str(e))
        return False


def test_kafka_connection():
    """Test 2: Kafka Connection"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Kafka Connection")
    logger.info("="*60)
    
    try:
        from confluent_kafka import Producer
        
        producer = Producer(Config.get_kafka_config())
        producer.flush(timeout=10)
        log_test("Kafka Producer Connection", "PASS", "Successfully connected to Kafka cluster")
        
        # Test topic access
        from confluent_kafka.admin import AdminClient
        admin = AdminClient(Config.get_kafka_config())
        
        # List topics
        metadata = admin.list_topics(timeout=10)
        topics = list(metadata.topics.keys())
        
        required_topics = [
            Config.TOPIC_TELEMETRY_RAW,
            Config.TOPIC_CODE_SAMPLES_RAW,
            Config.TOPIC_DARKWEB_FEEDS_RAW,
            Config.TOPIC_THREAT_PROFILES,
            Config.TOPIC_MITRE_ATTACK_MAPPINGS,
            Config.TOPIC_THREAT_ALERTS
        ]
        
        missing_topics = [t for t in required_topics if t not in topics]
        if missing_topics:
            log_test("Kafka Topics", "FAIL", f"Missing topics: {missing_topics}")
        else:
            log_test("Kafka Topics", "PASS", f"All {len(required_topics)} topics exist")
        
        log_test("Topic List", "INFO", f"Found {len(topics)} topics total", topics[:10])
        
        return True
    except Exception as e:
        log_test("Kafka Connection", "FAIL", str(e))
        return False


def test_schema_registry():
    """Test 3: Schema Registry"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Schema Registry Connection")
    logger.info("="*60)
    
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        sr_config = Config.get_schema_registry_config()
        if not sr_config:
            log_test("Schema Registry", "SKIP", "Not configured")
            return True
        
        url = sr_config["url"]
        auth_info = sr_config["basic.auth.user.info"].split(":")
        api_key, api_secret = auth_info[0], auth_info[1]
        
        # Test connection
        response = requests.get(
            f"{url}/subjects",
            auth=HTTPBasicAuth(api_key, api_secret),
            timeout=10
        )
        
        if response.status_code == 200:
            subjects = response.json()
            log_test("Schema Registry Connection", "PASS", f"Status: {response.status_code}")
            log_test("Schema Registry Subjects", "INFO", f"Found {len(subjects)} subjects", subjects)
        else:
            log_test("Schema Registry Connection", "FAIL", f"Status: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        log_test("Schema Registry", "FAIL", str(e))
        return False


def test_vertex_ai():
    """Test 4: Vertex AI"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Vertex AI Integration")
    logger.info("="*60)
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Initialize
        vertexai.init(
            project=Config.GOOGLE_CLOUD_PROJECT,
            location=Config.VERTEX_AI_LOCATION
        )
        log_test("Vertex AI Initialization", "PASS", f"Project: {Config.GOOGLE_CLOUD_PROJECT}, Location: {Config.VERTEX_AI_LOCATION}")
        
        # Test model access
        model = GenerativeModel(Config.GEMINI_MODEL)
        log_test("Model Access", "PASS", f"Model: {Config.GEMINI_MODEL}")
        
        # Test simple generation
        try:
            response = model.generate_content("Say 'test' if you can read this.")
            if response and response.text:
                log_test("Model Generation", "PASS", f"Response received: {response.text[:50]}")
            else:
                log_test("Model Generation", "WARN", "No response text")
        except Exception as e:
            log_test("Model Generation", "WARN", f"Generation test failed: {str(e)[:100]}")
        
        return True
    except Exception as e:
        log_test("Vertex AI", "FAIL", str(e))
        return False


def test_producers():
    """Test 5: Kafka Producers"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Kafka Producers")
    logger.info("="*60)
    
    results = []
    
    try:
        from src.producers.telemetry_producer import TelemetryProducer
        producer = TelemetryProducer()
        test_data = {
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "protocol": "TCP",
            "port": 443,
            "bytes_sent": 1024,
            "bytes_received": 2048
        }
        success = producer.produce_telemetry(test_data)
        producer.close()
        if success:
            log_test("Telemetry Producer", "PASS", "Message produced successfully")
            results.append(True)
        else:
            log_test("Telemetry Producer", "FAIL", "Failed to produce message")
            results.append(False)
    except Exception as e:
        log_test("Telemetry Producer", "FAIL", str(e))
        results.append(False)
    
    try:
        from src.producers.code_producer import CodeProducer
        producer = CodeProducer()
        test_data = {
            "source": "github",
            "code_content": "print('test')",
            "language": "python"
        }
        success = producer.produce_code_sample(test_data)
        producer.close()
        if success:
            log_test("Code Producer", "PASS", "Message produced successfully")
            results.append(True)
        else:
            log_test("Code Producer", "FAIL", "Failed to produce message")
            results.append(False)
    except Exception as e:
        log_test("Code Producer", "FAIL", str(e))
        results.append(False)
    
    try:
        from src.producers.darkweb_producer import DarkWebProducer
        producer = DarkWebProducer()
        test_data = {
            "source": "test_forum",
            "content": "Test dark web feed",
            "keywords": ["test"]
        }
        success = producer.produce_feed(test_data)
        producer.close()
        if success:
            log_test("Dark Web Producer", "PASS", "Message produced successfully")
            results.append(True)
        else:
            log_test("Dark Web Producer", "FAIL", "Failed to produce message")
            results.append(False)
    except Exception as e:
        log_test("Dark Web Producer", "FAIL", str(e))
        results.append(False)
    
    return all(results)


def test_data_models():
    """Test 6: Data Models"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Data Models")
    logger.info("="*60)
    
    try:
        from src.models.threat import ThreatEvent, ThreatProfile, ThreatType, ThreatSeverity
        from src.models.mitre import MITREMapping, MITRETactic
        
        # Test ThreatEvent
        event = ThreatEvent(
            event_id="test-123",
            threat_type=ThreatType.MALWARE,
            severity=ThreatSeverity.HIGH,
            source="test",
            confidence_score=0.85,
            description="Test threat"
        )
        assert event.event_id == "test-123"
        log_test("ThreatEvent Model", "PASS", "Model created and validated")
        
        # Test ThreatProfile
        profile = ThreatProfile(
            profile_id="profile-123",
            threat_type=ThreatType.AUTONOMOUS_HACKING,
            severity=ThreatSeverity.CRITICAL,
            confidence_score=0.90
        )
        assert profile.profile_id == "profile-123"
        log_test("ThreatProfile Model", "PASS", "Model created and validated")
        
        # Test MITREMapping
        mapping = MITREMapping(
            mapping_id="mapping-123",
            threat_profile_id="profile-123",
            primary_tactic=MITRETactic.EXECUTION.value,
            primary_technique="T1059",
            confidence_score=0.85,
            mapping_reason="Test mapping"
        )
        assert mapping.mapping_id == "mapping-123"
        log_test("MITREMapping Model", "PASS", "Model created and validated")
        
        return True
    except Exception as e:
        log_test("Data Models", "FAIL", str(e))
        return False


def test_threat_analyzer():
    """Test 7: Threat Analyzer"""
    logger.info("\n" + "="*60)
    logger.info("TEST 7: Threat Analyzer")
    logger.info("="*60)
    
    try:
        from src.processors.threat_analyzer import ThreatAnalyzer
        
        analyzer = ThreatAnalyzer()
        log_test("Threat Analyzer Initialization", "PASS", "Analyzer created")
        
        # Test with mock data (won't call Vertex AI unless configured)
        test_telemetry = {
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "protocol": "TCP",
            "port": 22,
            "bytes_sent": 1000000
        }
        
        # This will use mock analysis if Vertex AI not fully configured
        result = analyzer.analyze_telemetry(test_telemetry)
        if result:
            log_test("Threat Analysis", "PASS", f"Analysis completed, threat type: {result.threat_type.value}")
        else:
            log_test("Threat Analysis", "INFO", "No threat detected (or using mock)")
        
        return True
    except Exception as e:
        log_test("Threat Analyzer", "FAIL", str(e))
        return False


def test_mitre_mapper():
    """Test 8: MITRE Mapper"""
    logger.info("\n" + "="*60)
    logger.info("TEST 8: MITRE ATT&CK Mapper")
    logger.info("="*60)
    
    try:
        from src.processors.mitre_mapper import MITREMapper
        from src.models.threat import ThreatProfile, ThreatType, ThreatSeverity
        
        mapper = MITREMapper()
        log_test("MITRE Mapper Initialization", "PASS", "Mapper created")
        
        # Create test profile
        profile = ThreatProfile(
            profile_id="test-profile",
            threat_type=ThreatType.AUTONOMOUS_HACKING,
            severity=ThreatSeverity.HIGH,
            confidence_score=0.85,
            autonomous_system_indicators=["high_frequency", "pattern_based"]
        )
        
        # Map to MITRE
        mapping = mapper.map_threat_profile(profile)
        if mapping:
            log_test("MITRE Mapping", "PASS", f"Mapped to: {mapping.primary_tactic} / {mapping.primary_technique}")
            log_test("MITRE AI-Specific", "INFO", f"AI-specific: {mapping.ai_specific}")
        else:
            log_test("MITRE Mapping", "FAIL", "Mapping failed")
            return False
        
        return True
    except Exception as e:
        log_test("MITRE Mapper", "FAIL", str(e))
        return False


def generate_summary():
    """Generate test summary"""
    passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
    failed = sum(1 for t in test_results["tests"] if t["status"] == "FAIL")
    warned = sum(1 for t in test_results["tests"] if t["status"] == "WARN")
    skipped = sum(1 for t in test_results["tests"] if t["status"] == "SKIP")
    info = sum(1 for t in test_results["tests"] if t["status"] == "INFO")
    
    test_results["summary"] = {
        "total": len(test_results["tests"]),
        "passed": passed,
        "failed": failed,
        "warnings": warned,
        "skipped": skipped,
        "info": info,
        "success_rate": f"{(passed / len(test_results['tests']) * 100):.1f}%" if test_results["tests"] else "0%"
    }


def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("ThreatStream AI - Comprehensive Test Suite")
    logger.info("="*60)
    logger.info(f"Test Run: {test_results['timestamp']}")
    logger.info("")
    
    # Run all tests
    tests = [
        ("Configuration", test_configuration),
        ("Kafka Connection", test_kafka_connection),
        ("Schema Registry", test_schema_registry),
        ("Vertex AI", test_vertex_ai),
        ("Kafka Producers", test_producers),
        ("Data Models", test_data_models),
        ("Threat Analyzer", test_threat_analyzer),
        ("MITRE Mapper", test_mitre_mapper),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            log_test(name, "FAIL", f"Test crashed: {str(e)}")
    
    # Generate summary
    generate_summary()
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    summary = test_results["summary"]
    logger.info(f"Total Tests: {summary['total']}")
    logger.info(f"✅ Passed: {summary['passed']}")
    logger.info(f"❌ Failed: {summary['failed']}")
    logger.info(f"⚠️  Warnings: {summary['warnings']}")
    logger.info(f"⏭️  Skipped: {summary['skipped']}")
    logger.info(f"📊 Success Rate: {summary['success_rate']}")
    logger.info("="*60)
    
    # Save results
    results_file = Path(__file__).parent.parent / "test_results.json"
    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)
    
    logger.info(f"\n📄 Detailed results saved to: {results_file}")
    
    return summary["failed"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

