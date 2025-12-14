"""
Data Generator API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from loguru import logger

from src.dashboard.services.data_generator_service import get_data_generator_service

router = APIRouter()


@router.post("/generate/all")
async def generate_all(
    duration: Optional[float] = Query(None),
    count: Optional[int] = Query(None)
) -> Dict[str, Any]:
    """Generate all data types"""
    # #region agent log
    import json; log_data = {"location": "generator.py:19", "message": "generate_all route called", "data": {"duration": duration, "count": count}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "G"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
    # #endregion
    
    service = get_data_generator_service()
    
    # #region agent log
    log_data = {"location": "generator.py:23", "message": "Service check", "data": {"service_available": service is not None}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "H"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
    # #endregion
    
    if not service:
        # #region agent log
        log_data = {"location": "generator.py:26", "message": "Service not available", "data": {}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "I"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    try:
        result = await service.generate_all(duration=duration, count=count)
        # #region agent log
        log_data = {"location": "generator.py:31", "message": "Service call successful", "data": {"result_success": result.get("success") if isinstance(result, dict) else None}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "J"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        return result
    except Exception as e:
        # #region agent log
        log_data = {"location": "generator.py:35", "message": "Exception in generate_all", "data": {"error": str(e), "error_type": type(e).__name__}, "timestamp": __import__("time").time() * 1000, "sessionId": "debug-session", "runId": "run1", "hypothesisId": "K"}; open("/Users/rochitlen/Downloads/animus/.cursor/debug.log", "a").write(json.dumps(log_data) + "\n")
        # #endregion
        logger.error(f"Error in generate_all: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/telemetry")
async def generate_telemetry(
    count: Optional[int] = Query(None),
    duration: Optional[float] = Query(None),
    pattern: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Generate telemetry data"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    result = await service.generate_telemetry(count=count, duration=duration, pattern=pattern)
    return result


@router.post("/generate/code")
async def generate_code(
    count: Optional[int] = Query(None),
    duration: Optional[float] = Query(None),
    pattern: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Generate code samples"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    result = await service.generate_code(count=count, duration=duration, pattern=pattern)
    return result


@router.post("/generate/darkweb")
async def generate_darkweb(
    count: Optional[int] = Query(None),
    duration: Optional[float] = Query(None),
    pattern: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """Generate dark web feeds"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    result = await service.generate_darkweb(count=count, duration=duration, pattern=pattern)
    return result


@router.post("/scenario/{scenario_name}")
async def run_scenario(
    scenario_name: str,
    duration: Optional[float] = Query(None)
) -> Dict[str, Any]:
    """Run a predefined attack scenario"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    result = await service.run_scenario(scenario_name, duration=duration)
    return result


@router.get("/scenarios")
async def list_scenarios() -> Dict[str, Any]:
    """List available scenarios"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    result = await service.list_scenarios()
    return result


@router.get("/active")
async def get_active_generators() -> Dict[str, Any]:
    """Get list of active generators"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    active = service.get_active_generators()
    return {
        "active_generators": active,
        "count": len(active)
    }


@router.post("/stop/{task_id}")
async def stop_generator(task_id: str) -> Dict[str, Any]:
    """Stop a running generator"""
    service = get_data_generator_service()
    if not service:
        raise HTTPException(status_code=503, detail="Data generator service not available")
    
    result = service.stop_generator(task_id)
    return result

