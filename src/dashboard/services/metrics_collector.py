"""
Metrics Collector Service
Collects system-wide metrics
"""

import asyncio
import psutil
import time
from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque
from loguru import logger

from src.config import Config


class MetricsCollector:
    """Collects system and application metrics"""
    
    _instance = None
    
    def __init__(self):
        """Initialize metrics collector"""
        self.running = False
        self.throughput_history = deque(maxlen=100)  # Last 100 measurements
        self.latency_history = deque(maxlen=100)
        self.error_count = 0
        self.start_time = time.time()
        self.logger = logger.bind(component="metrics_collector")
    
    async def start(self):
        """Start collecting metrics"""
        self.running = True
        asyncio.create_task(self._collect_loop())
        self.logger.info("Metrics collector started")
    
    async def stop(self):
        """Stop collecting metrics"""
        self.running = False
        self.logger.info("Metrics collector stopped")
    
    async def _collect_loop(self):
        """Main metrics collection loop"""
        while self.running:
            try:
                # Collect metrics every 5 seconds
                await asyncio.sleep(5)
                
                # Collect system metrics
                # (In production, collect from actual Kafka/Vertex AI)
                
            except Exception as e:
                self.logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        try:
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total / 1024 / 1024 / 1024,  # GB
                    "used": memory.used / 1024 / 1024 / 1024,  # GB
                    "percent": memory.percent,
                    "process_memory_mb": process_memory
                },
                "uptime": time.time() - self.start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    async def get_kafka_metrics(self) -> Dict[str, Any]:
        """Get Kafka-specific metrics"""
        try:
            # In production, get from Kafka admin client
            return {
                "connection_status": "connected",
                "topics": len([
                    Config.TOPIC_TELEMETRY_RAW,
                    Config.TOPIC_CODE_SAMPLES_RAW,
                    Config.TOPIC_DARKWEB_FEEDS_RAW,
                    Config.TOPIC_THREAT_PROFILES,
                    Config.TOPIC_MITRE_ATTACK_MAPPINGS,
                    Config.TOPIC_THREAT_ALERTS
                ]),
                "consumer_lag": 0,  # Would get from consumer groups
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Kafka metrics: {e}")
            return {}
    
    async def get_vertex_ai_metrics(self) -> Dict[str, Any]:
        """Get Vertex AI metrics"""
        try:
            # In production, track actual API calls
            return {
                "model": Config.GEMINI_MODEL,
                "location": Config.VERTEX_AI_LOCATION,
                "project": Config.GOOGLE_CLOUD_PROJECT,
                "api_calls": 0,  # Would track actual calls
                "average_latency_ms": 0,
                "error_rate": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting Vertex AI metrics: {e}")
            return {}
    
    async def get_throughput_metrics(self) -> Dict[str, Any]:
        """Get throughput metrics"""
        try:
            return {
                "messages_per_second": 0.0,  # Would calculate from history
                "bytes_per_second": 0.0,
                "average_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "error_rate": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting throughput metrics: {e}")
            return {}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            "system": await self.get_system_metrics(),
            "kafka": await self.get_kafka_metrics(),
            "vertex_ai": await self.get_vertex_ai_metrics(),
            "throughput": await self.get_throughput_metrics()
        }


# Singleton instance
_metrics_collector_instance = None


def get_metrics_collector() -> Optional[MetricsCollector]:
    """Get metrics collector instance"""
    return _metrics_collector_instance


def set_metrics_collector(collector: MetricsCollector):
    """Set metrics collector instance"""
    global _metrics_collector_instance
    _metrics_collector_instance = collector

