"""
Temperature sensor worker for realistic temperature data simulation.
Generates temperature readings with daily patterns, seasonal variations, and room-specific characteristics.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from app.core.database import influxdb_client
from app.core.websocket import websocket_manager
from app.config.sensor_config import get_temperature_config, get_simulation_config

logger = logging.getLogger(__name__)

class TemperatureWorker:
    """Temperature sensor simulation worker."""
    
    def __init__(self):
        self.influx_client = influxdb_client
        self.bucket = "sensors"
        self.org = "smarthome"
        self.is_running = False
        
        # Load configuration from config system
        self.temp_config = get_temperature_config()
        self.sim_config = get_simulation_config()
        
        # Room configurations from config system
        self.room_configs = self.temp_config.room_configs
        
        # Initialize room states
        self.room_states = {}
        for room_id, config in self.room_configs.items():
            self.room_states[room_id] = {
                "current_temp": config["base_temp"],
                "target_temp": config["base_temp"],
                "last_update": datetime.now(),
                "trend": 0.0,
                "heating_active": False,
                "cooling_active": False,
            }
    
    def get_seasonal_adjustment(self) -> float:
        """Calculate seasonal temperature adjustment based on current date."""
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        
        # Seasonal sine wave: peak in summer (day 172), trough in winter (day 355)
        seasonal_factor = math.sin((day_of_year - 81) * 2 * math.pi / 365)
        return seasonal_factor * self.temp_config.seasonal_variation
    
    def get_daily_pattern(self, room_id: str) -> float:
        """Calculate daily temperature pattern based on time of day."""
        now = datetime.now()
        hour = now.hour + now.minute / 60.0
        
        # Different patterns for different rooms
        if room_id == "bedroom":
            # Cooler at night, warmer during day
            daily_factor = -2.0 * math.cos((hour - 6) * 2 * math.pi / 24)
        elif room_id == "kitchen":
            # Peaks during meal times
            morning_peak = 1.5 * math.exp(-((hour - 8) ** 2) / 8)
            evening_peak = 2.0 * math.exp(-((hour - 18) ** 2) / 8)
            daily_factor = morning_peak + evening_peak
        elif room_id == "living_room":
            # Active during evening
            daily_factor = 1.0 * math.sin((hour - 12) * math.pi / 12)
        elif room_id == "bathroom":
            # Peaks during morning and evening routines
            morning_peak = 3.0 * math.exp(-((hour - 7) ** 2) / 2)
            evening_peak = 2.0 * math.exp(-((hour - 20) ** 2) / 4)
            daily_factor = morning_peak + evening_peak
        else:
            # Default gentle daily pattern
            daily_factor = 1.0 * math.sin((hour - 12) * math.pi / 12)
        
        return daily_factor
    
    def get_outdoor_temperature(self) -> float:
        """Get current outdoor temperature with realistic patterns."""
        seasonal_temp = self.get_seasonal_adjustment()
        daily_pattern = self.get_daily_pattern("outdoor")
        
        # Base outdoor temperature with seasonal and daily variations
        base_temp = self.room_configs["outdoor"]["base_temp"]
        outdoor_temp = base_temp + seasonal_temp + daily_pattern
        
        # Add some random variation
        outdoor_temp += random.gauss(0, 2.0)
        
        return outdoor_temp
    
    def update_room_temperature(self, room_id: str, outdoor_temp: float) -> float:
        """Update room temperature based on various factors."""
        config = self.room_configs[room_id]
        state = self.room_states[room_id]
        
        if room_id == "outdoor":
            # Outdoor temperature is calculated separately
            new_temp = outdoor_temp
        else:
            # Calculate target temperature based on patterns
            seasonal_adj = self.get_seasonal_adjustment() * 0.3  # Indoor is less affected
            daily_adj = self.get_daily_pattern(room_id)
            target_temp = config["base_temp"] + seasonal_adj + daily_adj
            
            # External influence from outdoor temperature
            external_influence = (outdoor_temp - config["base_temp"]) * config["external_influence"] * 0.1
            target_temp += external_influence
            
            # Simulate heating/cooling system
            temp_diff = target_temp - state["current_temp"]
            
            # Simple heating/cooling logic
            if temp_diff > 1.0:
                state["heating_active"] = True
                state["cooling_active"] = False
            elif temp_diff < -1.0:
                state["heating_active"] = False
                state["cooling_active"] = True
            else:
                state["heating_active"] = False
                state["cooling_active"] = False
            
            # Calculate temperature change rate
            thermal_mass = config["thermal_mass"]
            change_rate = temp_diff * (1 - thermal_mass) * 0.1
            
            # Apply heating/cooling effects
            if state["heating_active"]:
                change_rate += config["heating_efficiency"] * 0.5
            elif state["cooling_active"]:
                change_rate -= config["heating_efficiency"] * 0.3
            
            # Apply the change
            new_temp = state["current_temp"] + change_rate
            
            # Add sensor noise
            noise = random.gauss(0, config["sensor_accuracy"] * 0.1)
            new_temp += noise
        
        # Update state
        state["current_temp"] = new_temp
        state["target_temp"] = target_temp if room_id != "outdoor" else outdoor_temp
        state["last_update"] = datetime.now()
        
        return new_temp
    
    async def generate_temperature_reading(self, room_id: str, sensor_id: str) -> Dict:
        """Generate a realistic temperature reading for a room."""
        outdoor_temp = self.get_outdoor_temperature()
        temperature = self.update_room_temperature(room_id, outdoor_temp)
        
        # Ensure temperature is within realistic bounds
        temperature = max(self.temp_config.global_min_temp, min(self.temp_config.global_max_temp, temperature))
        
        reading = {
            "sensor_id": sensor_id,
            "room_id": room_id,
            "temperature": round(temperature, 1),
            "unit": "°C",
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "temperature",
            "heating_active": self.room_states[room_id].get("heating_active", False),
            "cooling_active": self.room_states[room_id].get("cooling_active", False),
            "outdoor_temp": round(outdoor_temp, 1),
        }
        
        return reading
    
    async def write_to_influxdb(self, reading: Dict):
        """Write temperature reading to InfluxDB."""
        try:
            tags = {
                "room_id": reading["room_id"],
                "sensor_id": reading["sensor_id"],
                "sensor_type": "temperature"
            }
            
            fields = {
                "value": reading["temperature"],
                "unit": reading["unit"],
                "heating_active": reading["heating_active"],
                "cooling_active": reading["cooling_active"],
                "outdoor_temp": reading["outdoor_temp"]
            }
            
            await self.influx_client.write_sensor_data("temperature", tags, fields)
            logger.debug(f"Temperature reading written to InfluxDB: {reading['room_id']} = {reading['temperature']}°C")
            
        except Exception as e:
            logger.error(f"Error writing temperature to InfluxDB: {e}")
    
    async def broadcast_reading(self, reading: Dict):
        """Broadcast temperature reading via WebSocket."""
        try:
            message = {
                "type": "temperature_update",
                "data": reading
            }
            await websocket_manager.broadcast_message(message)
            logger.debug(f"Temperature reading broadcast: {reading['room_id']} = {reading['temperature']}°C")
            
        except Exception as e:
            logger.error(f"Error broadcasting temperature reading: {e}")
    
    async def run_sensor_loop(self):
        """Main sensor loop that generates and processes temperature readings."""
        logger.info("Starting temperature sensor worker...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Generate readings for all rooms
                for room_id in self.room_configs.keys():
                    sensor_id = f"temp_{room_id}_001"
                    
                    # Generate temperature reading
                    reading = await self.generate_temperature_reading(room_id, sensor_id)
                    
                    # Write to InfluxDB
                    await self.write_to_influxdb(reading)
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_reading(reading)
                
                # Wait for next reading interval from config
                await asyncio.sleep(self.sim_config.temperature_interval)
                
            except Exception as e:
                logger.error(f"Error in temperature sensor loop: {e}")
                await asyncio.sleep(5)  # Short retry delay
    
    async def start(self):
        """Start the temperature sensor worker."""
        if not self.is_running:
            asyncio.create_task(self.run_sensor_loop())
    
    async def stop(self):
        """Stop the temperature sensor worker."""
        logger.info("Stopping temperature sensor worker...")
        self.is_running = False

# Global instance
temperature_worker = TemperatureWorker() 