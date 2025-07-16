"""
Smart Home IoT Backend - Main FastAPI Application
===============================================

This is the main entry point for the Smart Home IoT backend API.
It configures the FastAPI application with all necessary middleware,
routes, and WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import structlog
from datetime import datetime
import json

# Core imports
from app.core.config import settings
from app.core.database import influxdb_client
from app.core.websocket import websocket_manager
from app.core.security import get_password_hash

# Workers
from app.workers.sensor_simulator import sensor_simulator

# API routes
from app.api.auth import router as auth_router
from app.api.sensors import router as sensors_router
from app.api.rooms import router as rooms_router
from app.api.dashboard import router as dashboard_router
from app.api.alerts import router as alerts_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Smart Home IoT Backend...")
    
    # Initialize database connection
    try:
        await influxdb_client.initialize()
        logger.info("InfluxDB connection established")
    except Exception as e:
        logger.error(f"Failed to connect to InfluxDB: {e}")
        raise
    
    # Start sensor simulation system
    try:
        await sensor_simulator.start()
        logger.info("Sensor simulation system started")
    except Exception as e:
        logger.error(f"Failed to start sensor simulation system: {e}")
        # Continue startup even if sensors fail
    
    logger.info("Backend startup completed successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Home IoT Backend...")
    
    # Stop sensor simulation system
    try:
        await sensor_simulator.stop()
        logger.info("Sensor simulation system stopped")
    except Exception as e:
        logger.error(f"Error stopping sensor simulation system: {e}")
    
    # Close database connections
    try:
        await influxdb_client.close()
        logger.info("InfluxDB connection closed")
    except Exception as e:
        logger.error(f"Error closing InfluxDB connection: {e}")
    
    logger.info("Backend shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Smart Home IoT API",
    description="A comprehensive Smart Home IoT monitoring system with real-time sensor data, energy monitoring, and security features.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(sensors_router, prefix="/api/v1/sensors", tags=["Sensors"])
app.include_router(rooms_router, prefix="/api/v1/rooms", tags=["Rooms"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API status.
    """
    try:
        # Check database connectivity
        db_status = await influxdb_client.health_check()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "Smart Home IoT Backend",
                "version": "1.0.0",
                "database": {
                    "influxdb": db_status
                }
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service": "Smart Home IoT Backend",
                "error": str(e)
            }
        )


# WebSocket endpoint for real-time data
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sensor data streaming.
    """
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            # Parse and handle the message
            try:
                message = json.loads(data)
                await websocket_manager.handle_message(websocket, message)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Smart Home IoT Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # Use structlog instead
    ) 