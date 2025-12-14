"""
Metrics API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger

from src.dashboard.services.metrics_collector import get_metrics_collector

router = APIRouter()


@router.get("/system")
async def get_system_metrics() -> Dict[str, Any]:
    """Get system-wide metrics"""
    try:
        collector = get_metrics_collector()
        if not collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        metrics = await collector.get_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kafka")
async def get_kafka_metrics() -> Dict[str, Any]:
    """Get Kafka-specific metrics"""
    try:
        collector = get_metrics_collector()
        if not collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        metrics = await collector.get_kafka_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting Kafka metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vertex-ai")
async def get_vertex_ai_metrics() -> Dict[str, Any]:
    """Get Vertex AI metrics"""
    try:
        collector = get_metrics_collector()
        if not collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        metrics = await collector.get_vertex_ai_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting Vertex AI metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/throughput")
async def get_throughput_metrics() -> Dict[str, Any]:
    """Get throughput metrics"""
    try:
        collector = get_metrics_collector()
        if not collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")
        
        metrics = await collector.get_throughput_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting throughput metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

