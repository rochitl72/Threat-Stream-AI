#!/usr/bin/env python3
"""
Test script for ThreatStream AI system
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.producers.telemetry_producer import TelemetryProducer
from src.producers.code_producer import CodeProducer
from src.producers.darkweb_producer import DarkWebProducer
from src.utils.logger import setup_logger

logger = setup_logger("test_system")


def test_kafka_connection():
    """Test Kafka connection"""
    logger.info("Testing Kafka connection...")
    try:
        from confluent_kafka import Producer
        producer = Producer(Config.get_kafka_config())
        producer.flush()
        logger.info("✅ Kafka connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Kafka connection failed: {e}")
        return False


def test_vertex_ai():
    """Test Vertex AI connection"""
    logger.info("Testing Vertex AI connection...")
    try:
        import vertexai
        vertexai.init(
            project=Config.GOOGLE_CLOUD_PROJECT,
            location=Config.VERTEX_AI_LOCATION
        )
        from vertexai.generative_models import GenerativeModel
        model = GenerativeModel(Config.GEMINI_MODEL)
        logger.info("✅ Vertex AI connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Vertex AI connection failed: {e}")
        logger.info("Note: This might work when running actual analysis")
        return False


def test_producers():
    """Test Kafka producers"""
    logger.info("Testing Kafka producers...")
    
    try:
        # Test telemetry producer
        logger.info("Testing TelemetryProducer...")
        telemetry_prod = TelemetryProducer()
        telemetry_prod.produce_telemetry({
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "protocol": "TCP",
            "port": 443,
            "bytes_sent": 1024,
            "bytes_received": 2048
        })
        telemetry_prod.close()
        logger.info("✅ TelemetryProducer working")
        
        # Test code producer
        logger.info("Testing CodeProducer...")
        code_prod = CodeProducer()
        code_prod.produce_code_sample({
            "source": "github",
            "code_content": "print('test')",
            "language": "python"
        })
        code_prod.close()
        logger.info("✅ CodeProducer working")
        
        # Test dark web producer
        logger.info("Testing DarkWebProducer...")
        darkweb_prod = DarkWebProducer()
        darkweb_prod.produce_feed({
            "source": "test_forum",
            "content": "Test dark web feed",
            "keywords": ["test"]
        })
        darkweb_prod.close()
        logger.info("✅ DarkWebProducer working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Producer test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("=" * 50)
    logger.info("ThreatStream AI System Test")
    logger.info("=" * 50)
    
    results = {
        "Kafka Connection": test_kafka_connection(),
        "Vertex AI Connection": test_vertex_ai(),
        "Kafka Producers": test_producers(),
    }
    
    logger.info("=" * 50)
    logger.info("Test Results:")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("🎉 All tests passed!")
    else:
        logger.warning("⚠️  Some tests failed. Check logs above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


