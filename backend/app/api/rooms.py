"""
Smart Home IoT Backend - Rooms API
==================================

This module contains room-related endpoints for room management
and sensor organization.
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
class RoomResponse(BaseModel):
    room_id: str
    name: str
    description: Optional[str] = None
    floor: int
    sensor_count: int
    status: str


@router.get("/", response_model=List[RoomResponse])
async def get_all_rooms(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get all rooms.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List[RoomResponse]: List of all rooms
    """
    try:
        # Mock room data for Phase 1
        mock_rooms = [
            {
                "room_id": "living_room",
                "name": "Living Room",
                "description": "Main living area",
                "floor": 1,
                "sensor_count": 3,
                "status": "active"
            },
            {
                "room_id": "bedroom",
                "name": "Master Bedroom",
                "description": "Master bedroom",
                "floor": 2,
                "sensor_count": 2,
                "status": "active"
            },
            {
                "room_id": "kitchen",
                "name": "Kitchen",
                "description": "Kitchen area",
                "floor": 1,
                "sensor_count": 4,
                "status": "active"
            }
        ]
        
        return [RoomResponse(**room) for room in mock_rooms]
        
    except Exception as e:
        logger.error(f"Failed to get rooms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get specific room information.
    
    Args:
        room_id: Room ID
        current_user: Current authenticated user
        
    Returns:
        RoomResponse: Room information
    """
    try:
        # Mock room data for Phase 1
        mock_room = {
            "room_id": room_id,
            "name": room_id.replace("_", " ").title(),
            "description": f"Description for {room_id}",
            "floor": 1,
            "sensor_count": 2,
            "status": "active"
        }
        
        return RoomResponse(**mock_room)
        
    except Exception as e:
        logger.error(f"Failed to get room {room_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 