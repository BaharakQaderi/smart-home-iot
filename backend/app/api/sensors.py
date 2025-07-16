"""
Smart Home IoT Backend - Sensors API
===================================

This module contains sensor-related endpoints for data retrieval
and sensor management with real-time sensor simulation.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime, timedelta
import asyncio

from app.core.security import get_current_user
from app.core.database import influxdb_client
from app.workers.sensor_simulator import sensor_simulator
from app.workers.temperature import temperature_worker
from app.workers.humidity import humidity_worker
from app.workers.energy import energy_worker

logger = structlog.get_logger(__name__)

router = APIRouter()


# Pydantic models for request/response
class SensorData(BaseModel):
    sensor_id: str
    sensor_type: str
    room_id: str
    value: float
    unit: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class SensorResponse(BaseModel):
    sensor_id: str
    sensor_type: str
    room_id: str
    name: str
    status: str
    last_reading: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None


class SensorHistoryRequest(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    aggregation: Optional[str] = "raw"  # raw, 1m, 5m, 1h, 1d
    limit: Optional[int] = 100


class SystemStatusResponse(BaseModel):
    system_status: str
    is_running: bool
    uptime_seconds: int
    workers: Dict[str, Any]
    statistics: Dict[str, Any]
    timestamp: str


class RoomSummaryResponse(BaseModel):
    room_id: str
    timestamp: str
    temperature: Dict[str, Any]
    humidity: Dict[str, Any]
    energy: Dict[str, Any]
    comfort_score: Dict[str, Any]
    alerts: List[Dict[str, Any]]


@router.get("/", response_model=List[SensorResponse])
async def get_all_sensors(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get all sensors with their current status and latest readings.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List[SensorResponse]: List of all sensors
    """
    try:
        sensors = []
        
        # Temperature sensors
        for room_id in temperature_worker.room_configs.keys():
            sensor_id = f"temp_{room_id}_001"
            try:
                latest_reading = await temperature_worker.generate_temperature_reading(room_id, sensor_id)
                sensors.append(SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="temperature",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Temperature",
                    status="active" if temperature_worker.is_running else "inactive",
                    last_reading=latest_reading,
                    config=temperature_worker.room_configs[room_id]
                ))
            except Exception as e:
                logger.error(f"Error getting temperature sensor {sensor_id}: {e}")
                sensors.append(SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="temperature",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Temperature",
                    status="error",
                    last_reading=None
                ))
        
        # Humidity sensors
        for room_id in humidity_worker.room_configs.keys():
            sensor_id = f"humid_{room_id}_001"
            try:
                latest_reading = await humidity_worker.generate_humidity_reading(room_id, sensor_id)
                sensors.append(SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="humidity",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Humidity",
                    status="active" if humidity_worker.is_running else "inactive",
                    last_reading=latest_reading,
                    config=humidity_worker.room_configs[room_id]
                ))
            except Exception as e:
                logger.error(f"Error getting humidity sensor {sensor_id}: {e}")
                sensors.append(SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="humidity",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Humidity",
                    status="error",
                    last_reading=None
                ))
        
        # Energy sensors
        for room_id in energy_worker.device_configs.keys():
            sensor_id = f"energy_{room_id}_001"
            try:
                latest_reading = await energy_worker.generate_energy_reading(room_id)
                sensors.append(SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="energy",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Energy Monitor",
                    status="active" if energy_worker.is_running else "inactive",
                    last_reading=latest_reading,
                    config=energy_worker.device_configs[room_id]
                ))
            except Exception as e:
                logger.error(f"Error getting energy sensor {sensor_id}: {e}")
                sensors.append(SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="energy",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Energy Monitor",
                    status="error",
                    last_reading=None
                ))
        
        logger.info(f"Retrieved {len(sensors)} sensors")
        return sensors
        
    except Exception as e:
        logger.error(f"Failed to get sensors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/latest", response_model=Dict[str, Any])
async def get_latest_readings(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get latest readings from all sensors.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Latest readings organized by sensor type
    """
    try:
        readings = await sensor_simulator.get_all_latest_readings()
        logger.info("Retrieved latest readings from all sensors")
        return readings
        
    except Exception as e:
        logger.error(f"Failed to get latest readings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get sensor system status.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        SystemStatusResponse: System status information
    """
    try:
        status = await sensor_simulator.get_system_status()
        return SystemStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/start")
async def start_sensor_system(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Start the sensor simulation system.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Success message
    """
    try:
        await sensor_simulator.start()
        logger.info("Sensor system started")
        return {"message": "Sensor system started successfully"}
        
    except Exception as e:
        logger.error(f"Failed to start sensor system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start sensor system"
        )


@router.post("/stop")
async def stop_sensor_system(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Stop the sensor simulation system.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Success message
    """
    try:
        await sensor_simulator.stop()
        logger.info("Sensor system stopped")
        return {"message": "Sensor system stopped successfully"}
        
    except Exception as e:
        logger.error(f"Failed to stop sensor system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop sensor system"
        )


@router.post("/restart/{worker_name}")
async def restart_worker(
    worker_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Restart a specific sensor worker.
    
    Args:
        worker_name: Name of the worker to restart (temperature, humidity, energy)
        current_user: Current authenticated user
        
    Returns:
        Dict[str, str]: Success message
    """
    try:
        success = await sensor_simulator.restart_worker(worker_name)
        if success:
            logger.info(f"Worker {worker_name} restarted successfully")
            return {"message": f"Worker {worker_name} restarted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to restart worker {worker_name}"
            )
        
    except Exception as e:
        logger.error(f"Failed to restart worker {worker_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{sensor_id}", response_model=SensorResponse)
async def get_sensor(sensor_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get specific sensor information.
    
    Args:
        sensor_id: Sensor ID
        current_user: Current authenticated user
        
    Returns:
        SensorResponse: Sensor information
    """
    try:
        # Parse sensor ID to determine type and room
        if sensor_id.startswith("temp_"):
            room_id = sensor_id.replace("temp_", "").replace("_001", "")
            if room_id in temperature_worker.room_configs:
                latest_reading = await temperature_worker.generate_temperature_reading(room_id, sensor_id)
                return SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="temperature",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Temperature",
                    status="active" if temperature_worker.is_running else "inactive",
                    last_reading=latest_reading,
                    config=temperature_worker.room_configs[room_id]
                )
        
        elif sensor_id.startswith("humid_"):
            room_id = sensor_id.replace("humid_", "").replace("_001", "")
            if room_id in humidity_worker.room_configs:
                latest_reading = await humidity_worker.generate_humidity_reading(room_id, sensor_id)
                return SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="humidity",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Humidity",
                    status="active" if humidity_worker.is_running else "inactive",
                    last_reading=latest_reading,
                    config=humidity_worker.room_configs[room_id]
                )
        
        elif sensor_id.startswith("energy_"):
            room_id = sensor_id.replace("energy_", "").replace("_001", "")
            if room_id in energy_worker.device_configs:
                latest_reading = await energy_worker.generate_energy_reading(room_id)
                return SensorResponse(
                    sensor_id=sensor_id,
                    sensor_type="energy",
                    room_id=room_id,
                    name=f"{room_id.replace('_', ' ').title()} Energy Monitor",
                    status="active" if energy_worker.is_running else "inactive",
                    last_reading=latest_reading,
                    config=energy_worker.device_configs[room_id]
                )
        
        # Sensor not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor {sensor_id} not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sensor {sensor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{sensor_id}/history")
async def get_sensor_history(
    sensor_id: str,
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    aggregation: Optional[str] = Query("raw", description="Aggregation level (raw, 1m, 5m, 1h, 1d)"),
    limit: Optional[int] = Query(100, description="Maximum number of points"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get sensor data history from InfluxDB.
    
    Args:
        sensor_id: Sensor ID
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        aggregation: Aggregation level
        limit: Maximum number of data points
        current_user: Current authenticated user
        
    Returns:
        List[Dict]: Historical sensor data
    """
    try:
        # Set default time range if not provided
        if not end_time:
            end_time = datetime.now().isoformat()
        if not start_time:
            start_time = (datetime.now() - timedelta(hours=24)).isoformat()
        
        # Determine measurement name based on sensor type
        measurement = None
        if sensor_id.startswith("temp_"):
            measurement = "temperature"
        elif sensor_id.startswith("humid_"):
            measurement = "humidity"
        elif sensor_id.startswith("energy_"):
            measurement = "energy_consumption"
        
        if not measurement:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sensor ID format"
            )
        
        # Build InfluxDB query
        query_api = influxdb_client._query_api
        
        # Aggregation query based on level
        if aggregation == "raw":
            query = f'''
                from(bucket: "sensors")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "{measurement}")
                |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
                |> limit(n: {limit})
                |> sort(columns: ["_time"], desc: true)
            '''
        else:
            # Aggregated query
            query = f'''
                from(bucket: "sensors")
                |> range(start: {start_time}, stop: {end_time})
                |> filter(fn: (r) => r["_measurement"] == "{measurement}")
                |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
                |> aggregateWindow(every: {aggregation}, fn: mean, createEmpty: false)
                |> limit(n: {limit})
                |> sort(columns: ["_time"], desc: true)
            '''
        
        # Execute query
        result = query_api.query(org="smarthome", query=query)
        
        # Process results
        data_points = []
        for table in result:
            for record in table.records:
                data_points.append({
                    "timestamp": record.get_time().isoformat(),
                    "value": record.get_value(),
                    "field": record.get_field(),
                    "sensor_id": record.values.get("sensor_id"),
                    "room_id": record.values.get("room_id"),
                })
        
        logger.info(f"Retrieved {len(data_points)} data points for sensor {sensor_id}")
        return data_points
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sensor history for {sensor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/type/{sensor_type}", response_model=List[SensorResponse])
async def get_sensors_by_type(
    sensor_type: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get sensors by type.
    
    Args:
        sensor_type: Sensor type (temperature, humidity, energy)
        current_user: Current authenticated user
        
    Returns:
        List[SensorResponse]: List of sensors of specified type
    """
    try:
        sensors = []
        
        if sensor_type == "temperature":
            for room_id in temperature_worker.room_configs.keys():
                sensor_id = f"temp_{room_id}_001"
                try:
                    latest_reading = await temperature_worker.generate_temperature_reading(room_id, sensor_id)
                    sensors.append(SensorResponse(
                        sensor_id=sensor_id,
                        sensor_type="temperature",
                        room_id=room_id,
                        name=f"{room_id.replace('_', ' ').title()} Temperature",
                        status="active" if temperature_worker.is_running else "inactive",
                        last_reading=latest_reading,
                        config=temperature_worker.room_configs[room_id]
                    ))
                except Exception as e:
                    logger.error(f"Error getting temperature sensor {sensor_id}: {e}")
        
        elif sensor_type == "humidity":
            for room_id in humidity_worker.room_configs.keys():
                sensor_id = f"humid_{room_id}_001"
                try:
                    latest_reading = await humidity_worker.generate_humidity_reading(room_id, sensor_id)
                    sensors.append(SensorResponse(
                        sensor_id=sensor_id,
                        sensor_type="humidity",
                        room_id=room_id,
                        name=f"{room_id.replace('_', ' ').title()} Humidity",
                        status="active" if humidity_worker.is_running else "inactive",
                        last_reading=latest_reading,
                        config=humidity_worker.room_configs[room_id]
                    ))
                except Exception as e:
                    logger.error(f"Error getting humidity sensor {sensor_id}: {e}")
        
        elif sensor_type == "energy":
            for room_id in energy_worker.device_configs.keys():
                sensor_id = f"energy_{room_id}_001"
                try:
                    latest_reading = await energy_worker.generate_energy_reading(room_id)
                    sensors.append(SensorResponse(
                        sensor_id=sensor_id,
                        sensor_type="energy",
                        room_id=room_id,
                        name=f"{room_id.replace('_', ' ').title()} Energy Monitor",
                        status="active" if energy_worker.is_running else "inactive",
                        last_reading=latest_reading,
                        config=energy_worker.device_configs[room_id]
                    ))
                except Exception as e:
                    logger.error(f"Error getting energy sensor {sensor_id}: {e}")
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sensor type: {sensor_type}"
            )
        
        logger.info(f"Retrieved {len(sensors)} sensors of type {sensor_type}")
        return sensors
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sensors by type {sensor_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/room/{room_id}/summary", response_model=RoomSummaryResponse)
async def get_room_summary(
    room_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get comprehensive room summary with all sensor data.
    
    Args:
        room_id: Room ID
        current_user: Current authenticated user
        
    Returns:
        RoomSummaryResponse: Complete room summary
    """
    try:
        summary = await sensor_simulator.get_room_summary(room_id)
        
        if "error" in summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found or error retrieving data"
            )
        
        return RoomSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get room summary for {room_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/energy/total")
async def get_total_energy_consumption(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get total home energy consumption.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict[str, Any]: Total energy consumption data
    """
    try:
        total_consumption = await energy_worker.get_total_consumption()
        logger.info("Retrieved total energy consumption")
        return total_consumption
        
    except Exception as e:
        logger.error(f"Failed to get total energy consumption: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 