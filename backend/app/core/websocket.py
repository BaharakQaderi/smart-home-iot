"""
Smart Home IoT Backend - WebSocket Manager
========================================

This module handles WebSocket connections for real-time communication
between the backend and frontend clients.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import asyncio
import structlog
from datetime import datetime
from uuid import uuid4

logger = structlog.get_logger(__name__)


class WebSocketManager:
    """
    WebSocket connection manager for handling real-time communication.
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.room_subscriptions: Dict[str, List[str]] = {}  # room_id -> [connection_ids]
        self.sensor_subscriptions: Dict[str, List[str]] = {}  # sensor_type -> [connection_ids]
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """
        Accept a WebSocket connection and assign it a unique ID.
        
        Args:
            websocket: WebSocket connection
            client_id: Optional client ID, if not provided, generates a UUID
            
        Returns:
            str: Connection ID
        """
        try:
            await websocket.accept()
            
            # Generate connection ID if not provided
            if not client_id:
                client_id = str(uuid4())
            
            # Store connection
            self.active_connections[client_id] = websocket
            self.connection_metadata[client_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "client_ip": websocket.client.host if websocket.client else "unknown",
                "subscriptions": {
                    "rooms": [],
                    "sensors": []
                }
            }
            
            # Send connection confirmation
            await self.send_personal_message(client_id, {
                "type": "connection_confirmed",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to Smart Home IoT WebSocket"
            })
            
            logger.info(f"WebSocket client {client_id} connected")
            return client_id
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket client: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """
        Disconnect a WebSocket client.
        
        Args:
            client_id: Connection ID to disconnect
        """
        try:
            # Remove from active connections
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            # Remove from metadata
            if client_id in self.connection_metadata:
                del self.connection_metadata[client_id]
            
            # Remove from room subscriptions
            for room_id, subscribers in self.room_subscriptions.items():
                if client_id in subscribers:
                    subscribers.remove(client_id)
            
            # Remove from sensor subscriptions
            for sensor_type, subscribers in self.sensor_subscriptions.items():
                if client_id in subscribers:
                    subscribers.remove(client_id)
            
            logger.info(f"WebSocket client {client_id} disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket client {client_id}: {e}")
    
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific client.
        
        Args:
            client_id: Connection ID
            message: Message to send
        """
        try:
            if client_id in self.active_connections:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Sent message to client {client_id}: {message.get('type', 'unknown')}")
            else:
                logger.warning(f"Attempted to send message to non-existent client {client_id}")
                
        except Exception as e:
            logger.error(f"Failed to send message to client {client_id}: {e}")
            # Remove dead connection
            self.disconnect(client_id)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        if not self.active_connections:
            return
        
        # Send to all active connections
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send broadcast message to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
        
        logger.debug(f"Broadcast message to {len(self.active_connections)} clients: {message.get('type', 'unknown')}")
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any]):
        """
        Broadcast a message to all clients subscribed to a specific room.
        
        Args:
            room_id: Room ID
            message: Message to broadcast
        """
        if room_id not in self.room_subscriptions:
            return
        
        subscribers = self.room_subscriptions[room_id].copy()
        disconnected_clients = []
        
        for client_id in subscribers:
            try:
                if client_id in self.active_connections:
                    websocket = self.active_connections[client_id]
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Failed to send room message to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.room_subscriptions[room_id]:
                self.room_subscriptions[room_id].remove(client_id)
            self.disconnect(client_id)
        
        logger.debug(f"Broadcast message to {len(subscribers)} clients in room {room_id}: {message.get('type', 'unknown')}")
    
    async def broadcast_sensor_data(self, sensor_type: str, data: Dict[str, Any]):
        """
        Broadcast sensor data to subscribed clients.
        
        Args:
            sensor_type: Type of sensor (temperature, humidity, etc.)
            data: Sensor data
        """
        message = {
            "type": "sensor_data",
            "sensor_type": sensor_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all clients subscribed to this sensor type
        if sensor_type in self.sensor_subscriptions:
            subscribers = self.sensor_subscriptions[sensor_type].copy()
            disconnected_clients = []
            
            for client_id in subscribers:
                try:
                    if client_id in self.active_connections:
                        websocket = self.active_connections[client_id]
                        await websocket.send_text(json.dumps(message))
                    else:
                        disconnected_clients.append(client_id)
                except Exception as e:
                    logger.error(f"Failed to send sensor data to client {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # Remove disconnected clients
            for client_id in disconnected_clients:
                if client_id in self.sensor_subscriptions[sensor_type]:
                    self.sensor_subscriptions[sensor_type].remove(client_id)
                self.disconnect(client_id)
        
        # Also send to all clients (for dashboard updates)
        await self.broadcast_message(message)
    
    async def handle_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Handle incoming messages from clients.
        
        Args:
            websocket: WebSocket connection
            message: Received message
        """
        try:
            # Find client ID
            client_id = None
            for cid, ws in self.active_connections.items():
                if ws == websocket:
                    client_id = cid
                    break
            
            if not client_id:
                logger.warning("Received message from unknown client")
                return
            
            message_type = message.get("type")
            
            if message_type == "subscribe_room":
                await self._handle_room_subscription(client_id, message)
            elif message_type == "unsubscribe_room":
                await self._handle_room_unsubscription(client_id, message)
            elif message_type == "subscribe_sensor":
                await self._handle_sensor_subscription(client_id, message)
            elif message_type == "unsubscribe_sensor":
                await self._handle_sensor_unsubscription(client_id, message)
            elif message_type == "ping":
                await self._handle_ping(client_id, message)
            elif message_type == "get_status":
                await self._handle_status_request(client_id, message)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_personal_message(client_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
    
    async def _handle_room_subscription(self, client_id: str, message: Dict[str, Any]):
        """Handle room subscription request."""
        room_id = message.get("room_id")
        
        if not room_id:
            await self.send_personal_message(client_id, {
                "type": "error",
                "message": "room_id is required for room subscription"
            })
            return
        
        # Add to room subscriptions
        if room_id not in self.room_subscriptions:
            self.room_subscriptions[room_id] = []
        
        if client_id not in self.room_subscriptions[room_id]:
            self.room_subscriptions[room_id].append(client_id)
            self.connection_metadata[client_id]["subscriptions"]["rooms"].append(room_id)
        
        await self.send_personal_message(client_id, {
            "type": "subscription_confirmed",
            "subscription_type": "room",
            "room_id": room_id,
            "message": f"Subscribed to room {room_id}"
        })
        
        logger.info(f"Client {client_id} subscribed to room {room_id}")
    
    async def _handle_room_unsubscription(self, client_id: str, message: Dict[str, Any]):
        """Handle room unsubscription request."""
        room_id = message.get("room_id")
        
        if not room_id:
            await self.send_personal_message(client_id, {
                "type": "error",
                "message": "room_id is required for room unsubscription"
            })
            return
        
        # Remove from room subscriptions
        if room_id in self.room_subscriptions and client_id in self.room_subscriptions[room_id]:
            self.room_subscriptions[room_id].remove(client_id)
            self.connection_metadata[client_id]["subscriptions"]["rooms"].remove(room_id)
        
        await self.send_personal_message(client_id, {
            "type": "unsubscription_confirmed",
            "subscription_type": "room",
            "room_id": room_id,
            "message": f"Unsubscribed from room {room_id}"
        })
        
        logger.info(f"Client {client_id} unsubscribed from room {room_id}")
    
    async def _handle_sensor_subscription(self, client_id: str, message: Dict[str, Any]):
        """Handle sensor subscription request."""
        sensor_type = message.get("sensor_type")
        
        if not sensor_type:
            await self.send_personal_message(client_id, {
                "type": "error",
                "message": "sensor_type is required for sensor subscription"
            })
            return
        
        # Add to sensor subscriptions
        if sensor_type not in self.sensor_subscriptions:
            self.sensor_subscriptions[sensor_type] = []
        
        if client_id not in self.sensor_subscriptions[sensor_type]:
            self.sensor_subscriptions[sensor_type].append(client_id)
            self.connection_metadata[client_id]["subscriptions"]["sensors"].append(sensor_type)
        
        await self.send_personal_message(client_id, {
            "type": "subscription_confirmed",
            "subscription_type": "sensor",
            "sensor_type": sensor_type,
            "message": f"Subscribed to sensor {sensor_type}"
        })
        
        logger.info(f"Client {client_id} subscribed to sensor {sensor_type}")
    
    async def _handle_sensor_unsubscription(self, client_id: str, message: Dict[str, Any]):
        """Handle sensor unsubscription request."""
        sensor_type = message.get("sensor_type")
        
        if not sensor_type:
            await self.send_personal_message(client_id, {
                "type": "error",
                "message": "sensor_type is required for sensor unsubscription"
            })
            return
        
        # Remove from sensor subscriptions
        if sensor_type in self.sensor_subscriptions and client_id in self.sensor_subscriptions[sensor_type]:
            self.sensor_subscriptions[sensor_type].remove(client_id)
            self.connection_metadata[client_id]["subscriptions"]["sensors"].remove(sensor_type)
        
        await self.send_personal_message(client_id, {
            "type": "unsubscription_confirmed",
            "subscription_type": "sensor",
            "sensor_type": sensor_type,
            "message": f"Unsubscribed from sensor {sensor_type}"
        })
        
        logger.info(f"Client {client_id} unsubscribed from sensor {sensor_type}")
    
    async def _handle_ping(self, client_id: str, message: Dict[str, Any]):
        """Handle ping request."""
        await self.send_personal_message(client_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "pong"
        })
    
    async def _handle_status_request(self, client_id: str, message: Dict[str, Any]):
        """Handle status request."""
        await self.send_personal_message(client_id, {
            "type": "status",
            "client_id": client_id,
            "connected_clients": len(self.active_connections),
            "subscriptions": self.connection_metadata[client_id]["subscriptions"],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        return {
            "active_connections": len(self.active_connections),
            "room_subscriptions": {
                room_id: len(subscribers)
                for room_id, subscribers in self.room_subscriptions.items()
            },
            "sensor_subscriptions": {
                sensor_type: len(subscribers)
                for sensor_type, subscribers in self.sensor_subscriptions.items()
            }
        }


# Create global WebSocket manager instance
websocket_manager = WebSocketManager() 