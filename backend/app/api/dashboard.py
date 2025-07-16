"""
Smart Home IoT Backend - Dashboard API
======================================

This module contains dashboard-related endpoints for overview
and summary data.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime

from app.core.security import get_current_user

logger = structlog.get_logger(__name__)

router = APIRouter()


# Pydantic models for request/response
class DashboardSummary(BaseModel):
    total_sensors: int
    active_sensors: int
    total_rooms: int
    system_status: str
    last_updated: str


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get dashboard summary data.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        DashboardSummary: Dashboard summary information
    """
    try:
        # Mock dashboard data for Phase 1
        summary = {
            "total_sensors": 15,
            "active_sensors": 14,
            "total_rooms": 5,
            "system_status": "healthy",
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return DashboardSummary(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/system-status")
async def get_system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get system status information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: System status information
    """
    try:
        # Mock system status for Phase 1
        status_info = {
            "overall_status": "healthy",
            "services": {
                "api": "healthy",
                "database": "healthy",
                "websocket": "healthy"
            },
            "uptime": "2 hours 30 minutes",
            "last_check": datetime.utcnow().isoformat()
        }
        
        return status_info
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 