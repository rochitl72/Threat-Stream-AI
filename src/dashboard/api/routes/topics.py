"""
Kafka Topics API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from loguru import logger

from src.config import Config
from src.dashboard.services.kafka_monitor import get_kafka_monitor

router = APIRouter()


@router.get("/")
async def list_topics() -> List[str]:
    """List all Kafka topics"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        topics = await monitor.list_topics()
        return topics
    except Exception as e:
        logger.error(f"Error listing topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_name}")
async def get_topic_info(topic_name: str) -> Dict[str, Any]:
    """Get information about a specific topic"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        info = await monitor.get_topic_info(topic_name)
        return info
    except Exception as e:
        logger.error(f"Error getting topic info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_name}/messages")
async def get_recent_messages(topic_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent messages from a topic"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        messages = await monitor.get_recent_messages(topic_name, limit)
        return messages
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_name}/metrics")
async def get_topic_metrics(topic_name: str) -> Dict[str, Any]:
    """Get metrics for a topic"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        metrics = await monitor.get_topic_metrics(topic_name)
        return metrics
    except Exception as e:
        logger.error(f"Error getting topic metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

