"""
Threats API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from loguru import logger

from src.dashboard.services.kafka_monitor import get_kafka_monitor

router = APIRouter()


@router.get("/")
async def list_threats(limit: int = 50) -> List[Dict[str, Any]]:
    """List recent threats"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        threats = await monitor.get_recent_threats(limit)
        return threats
    except Exception as e:
        logger.error(f"Error listing threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{threat_id}")
async def get_threat_details(threat_id: str) -> Dict[str, Any]:
    """Get details of a specific threat"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        threat = await monitor.get_threat_details(threat_id)
        if not threat:
            raise HTTPException(status_code=404, detail="Threat not found")
        
        return threat
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting threat details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/recent")
async def get_recent_profiles(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent threat profiles"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        profiles = await monitor.get_recent_profiles(limit)
        return profiles
    except Exception as e:
        logger.error(f"Error getting profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/recent")
async def get_recent_alerts(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent threat alerts"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        alerts = await monitor.get_recent_alerts(limit)
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

