"""
MITRE ATT&CK API Routes
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from loguru import logger

from src.dashboard.services.kafka_monitor import get_kafka_monitor

router = APIRouter()


@router.get("/mappings")
async def get_mitre_mappings(limit: int = 50) -> List[Dict[str, Any]]:
    """Get MITRE ATT&CK mappings"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        mappings = await monitor.get_mitre_mappings(limit)
        return mappings
    except Exception as e:
        logger.error(f"Error getting MITRE mappings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tactics")
async def get_tactics() -> List[str]:
    """Get all MITRE tactics"""
    try:
        from src.models.mitre import MITRETactic
        tactics = [tactic.value for tactic in MITRETactic]
        return tactics
    except Exception as e:
        logger.error(f"Error getting tactics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/techniques")
async def get_techniques() -> List[Dict[str, Any]]:
    """Get all MITRE techniques"""
    try:
        from src.models.mitre import COMMON_AI_TECHNIQUES
        return COMMON_AI_TECHNIQUES
    except Exception as e:
        logger.error(f"Error getting techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/matrix")
async def get_mitre_matrix() -> Dict[str, Any]:
    """Get MITRE ATT&CK matrix data"""
    try:
        monitor = get_kafka_monitor()
        if not monitor:
            raise HTTPException(status_code=503, detail="Kafka monitor not available")
        
        matrix = await monitor.get_mitre_matrix()
        return matrix
    except Exception as e:
        logger.error(f"Error getting MITRE matrix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

