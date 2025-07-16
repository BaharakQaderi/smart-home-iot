"""
Smart Home IoT Backend Core Module
=================================

This module contains core functionality including configuration,
database connections, security, and WebSocket management.
"""

from .config import settings
from .database import influxdb_client
from .websocket import websocket_manager
from .security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_admin_user
)

__all__ = [
    "settings",
    "influxdb_client",
    "websocket_manager",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_current_user",
    "get_current_admin_user"
] 