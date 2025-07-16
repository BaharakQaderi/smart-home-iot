"""
Smart Home IoT Backend - Database Connection
==========================================

This module handles InfluxDB database connections and provides
a client interface for sensor data storage and retrieval.
"""

from influxdb_client import InfluxDBClient as InfluxDBClientLib, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.query_api import QueryApi
from influxdb_client.client.write_api import WriteApi
from influxdb_client.client.exceptions import InfluxDBError
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import structlog
import asyncio
from datetime import datetime, timezone
import json

from app.core.config import settings

logger = structlog.get_logger(__name__)


class InfluxDBManager:
    """
    InfluxDB client wrapper for Smart Home IoT system.
    """
    
    def __init__(self):
        self._client: Optional[InfluxDBClientLib] = None
        self._write_api: Optional[WriteApi] = None
        self._query_api: Optional[QueryApi] = None
        self._is_connected: bool = False
    
    async def initialize(self):
        """Initialize InfluxDB connection."""
        try:
            # Create client with correct parameters for InfluxDB 2.x
            self._client = InfluxDBClientLib(
                url="http://influxdb:8086",
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG
            )
            
            # Create write API with batching
            self._write_api = self._client.write_api(
                write_options=WriteOptions(
                    batch_size=500,
                    flush_interval=10_000,
                    jitter_interval=2_000,
                    retry_interval=5_000,
                    max_retries=3,
                    max_retry_delay=30_000,
                    exponential_base=2
                )
            )
            
            # Create query API
            self._query_api = self._client.query_api()
            
            # Test connection
            await self._test_connection()
            
            self._is_connected = True
            logger.info("InfluxDB connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB: {e}")
            raise
    
    async def _test_connection(self):
        """Test database connection."""
        try:
            # Simple health check query
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.health()
            )
            
            if result.status != "pass":
                raise InfluxDBError(f"InfluxDB health check failed: {result.message}")
                
        except Exception as e:
            logger.error(f"InfluxDB connection test failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status."""
        try:
            if not self._is_connected:
                return {
                    "status": "unhealthy",
                    "message": "Not connected to InfluxDB",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test with a simple query
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.health()
            )
            
            return {
                "status": "healthy" if result.status == "pass" else "unhealthy",
                "message": result.message,
                "timestamp": datetime.utcnow().isoformat(),
                "version": result.version if hasattr(result, 'version') else "unknown"
            }
            
        except Exception as e:
            logger.error(f"InfluxDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def write_sensor_data(self, measurement: str, tags: Dict[str, str], fields: Dict[str, Any], timestamp: Optional[datetime] = None):
        """Write sensor data to InfluxDB."""
        try:
            if not self._is_connected:
                raise InfluxDBError("Not connected to InfluxDB")
            
            # Create point
            point = Point(measurement)
            
            # Add tags
            for key, value in tags.items():
                point.tag(key, str(value))
            
            # Add fields
            for key, value in fields.items():
                if isinstance(value, (int, float)):
                    point.field(key, value)
                else:
                    point.field(key, str(value))
            
            # Set timestamp
            if timestamp:
                point.time(timestamp, timezone.utc)
            else:
                point.time(datetime.utcnow(), timezone.utc)
            
            # Write point
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._write_api.write(bucket=settings.INFLUXDB_BUCKET, record=point)
            )
            
            logger.debug(f"Wrote data point: {measurement} with tags {tags}")
            
        except Exception as e:
            logger.error(f"Failed to write sensor data: {e}")
            raise
    
    async def write_batch_sensor_data(self, data_points: List[Dict[str, Any]]):
        """Write multiple sensor data points in batch."""
        try:
            if not self._is_connected:
                raise InfluxDBError("Not connected to InfluxDB")
            
            points = []
            for data in data_points:
                point = Point(data["measurement"])
                
                # Add tags
                for key, value in data.get("tags", {}).items():
                    point.tag(key, str(value))
                
                # Add fields
                for key, value in data.get("fields", {}).items():
                    if isinstance(value, (int, float)):
                        point.field(key, value)
                    else:
                        point.field(key, str(value))
                
                # Set timestamp
                if data.get("timestamp"):
                    point.time(data["timestamp"], timezone.utc)
                else:
                    point.time(datetime.utcnow(), timezone.utc)
                
                points.append(point)
            
            # Write batch
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._write_api.write(bucket=settings.INFLUXDB_BUCKET, record=points)
            )
            
            logger.debug(f"Wrote {len(points)} data points in batch")
            
        except Exception as e:
            logger.error(f"Failed to write batch sensor data: {e}")
            raise
    
    async def query_sensor_data(self, query: str) -> List[Dict[str, Any]]:
        """Query sensor data from InfluxDB."""
        try:
            if not self._is_connected:
                raise InfluxDBError("Not connected to InfluxDB")
            
            # Execute query
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._query_api.query(query, org=settings.INFLUXDB_ORG)
            )
            
            # Process results
            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        "measurement": record.get_measurement(),
                        "time": record.get_time(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        "tags": record.values
                    })
            
            logger.debug(f"Queried {len(data)} records")
            return data
            
        except Exception as e:
            logger.error(f"Failed to query sensor data: {e}")
            raise
    
    async def get_latest_sensor_data(self, measurement: str, room_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get latest sensor data for a measurement."""
        try:
            # Build query
            query = f'''
            from(bucket: "{settings.INFLUXDB_BUCKET}")
                |> range(start: -1h)
                |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            '''
            
            if room_id:
                query += f'|> filter(fn: (r) => r["room_id"] == "{room_id}")'
            
            query += '''
                |> last()
            '''
            
            return await self.query_sensor_data(query)
            
        except Exception as e:
            logger.error(f"Failed to get latest sensor data: {e}")
            raise
    
    async def get_sensor_data_range(self, measurement: str, start_time: str, end_time: str, room_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get sensor data within a time range."""
        try:
            # Build query
            query = f'''
            from(bucket: "{settings.INFLUXDB_BUCKET}")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            '''
            
            if room_id:
                query += f'|> filter(fn: (r) => r["room_id"] == "{room_id}")'
            
            query += '''
                |> sort(columns: ["_time"])
            '''
            
            return await self.query_sensor_data(query)
            
        except Exception as e:
            logger.error(f"Failed to get sensor data range: {e}")
            raise
    
    async def get_aggregated_data(self, measurement: str, aggregation: str, window: str, room_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get aggregated sensor data."""
        try:
            # Build query
            query = f'''
            from(bucket: "{settings.INFLUXDB_BUCKET}")
                |> range(start: -24h)
                |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            '''
            
            if room_id:
                query += f'|> filter(fn: (r) => r["room_id"] == "{room_id}")'
            
            query += f'''
                |> aggregateWindow(every: {window}, fn: {aggregation})
                |> sort(columns: ["_time"])
            '''
            
            return await self.query_sensor_data(query)
            
        except Exception as e:
            logger.error(f"Failed to get aggregated data: {e}")
            raise
    
    async def close(self):
        """Close InfluxDB connection."""
        try:
            if self._write_api:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._write_api.close
                )
            
            if self._client:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._client.close
                )
            
            self._is_connected = False
            logger.info("InfluxDB connection closed")
            
        except Exception as e:
            logger.error(f"Error closing InfluxDB connection: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to InfluxDB."""
        return self._is_connected


# Create global client instance
influxdb_client = InfluxDBManager()


# Context manager for database operations
@asynccontextmanager
async def get_db_client():
    """Context manager for database operations."""
    if not influxdb_client.is_connected:
        await influxdb_client.initialize()
    
    try:
        yield influxdb_client
    finally:
        pass  # Keep connection alive for reuse 