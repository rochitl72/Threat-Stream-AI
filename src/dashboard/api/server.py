"""
FastAPI Server for Dashboard
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from typing import List
import json
import asyncio
from loguru import logger

from src.config import Config
from src.dashboard.api.routes import topics, threats, metrics, mitre, generator
from src.dashboard.services.kafka_monitor import KafkaMonitor, set_kafka_monitor
from src.dashboard.services.metrics_collector import MetricsCollector, set_metrics_collector
from src.dashboard.services.data_generator_service import DataGeneratorService, set_data_generator_service

app = FastAPI(
    title="ThreatStream AI Dashboard API",
    description="Real-time monitoring API for ThreatStream AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Global exception handlers to ensure JSON responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": "Validation error", "details": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": f"Internal server error: {str(exc)}"}
    )

app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(threats.router, prefix="/api/threats", tags=["threats"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(mitre.router, prefix="/api/mitre", tags=["mitre"])
app.include_router(generator.router, prefix="/api/generator", tags=["generator"])

# Global services
kafka_monitor = None
metrics_collector = None
data_generator_service = None
active_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global kafka_monitor, metrics_collector, data_generator_service
    
    logger.info("Starting dashboard services...")
    
    try:
        kafka_monitor = KafkaMonitor()
        await kafka_monitor.start()
        set_kafka_monitor(kafka_monitor)
        
        metrics_collector = MetricsCollector()
        await metrics_collector.start()
        set_metrics_collector(metrics_collector)
        
        data_generator_service = DataGeneratorService()
        set_data_generator_service(data_generator_service)
        
        logger.info("Dashboard services started successfully")
    except Exception as e:
        logger.error(f"Error starting dashboard services: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global kafka_monitor, metrics_collector
    
    logger.info("Shutting down dashboard services...")
    
    if kafka_monitor:
        await kafka_monitor.stop()
    
    if metrics_collector:
        await metrics_collector.stop()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ThreatStream AI Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "kafka": "connected" if kafka_monitor and kafka_monitor.is_connected() else "disconnected",
        "metrics": "running" if metrics_collector else "stopped"
    }


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """WebSocket endpoint for live data streaming"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"WebSocket client connected. Total connections: {len(active_connections)}")
    
    try:
        while True:
            # Send live data every second
            if kafka_monitor:
                data = await kafka_monitor.get_live_data()
                await websocket.send_json(data)
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await websocket.accept()
    
    try:
        while True:
            if metrics_collector:
                metrics_data = await metrics_collector.get_metrics()
                await websocket.send_json(metrics_data)
            
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        logger.info("Metrics WebSocket disconnected")
    except Exception as e:
        logger.error(f"Metrics WebSocket error: {e}")


@app.websocket("/ws/threats")
async def websocket_threats(websocket: WebSocket):
    """WebSocket endpoint for real-time threat alerts"""
    await websocket.accept()
    
    try:
        if kafka_monitor:
            # Subscribe to threat-alerts topic
            await kafka_monitor.subscribe_to_threats(websocket)
    except WebSocketDisconnect:
        logger.info("Threats WebSocket disconnected")
    except Exception as e:
        logger.error(f"Threats WebSocket error: {e}")


def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    for connection in active_connections:
        try:
            asyncio.create_task(connection.send_json(message))
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "src.dashboard.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

