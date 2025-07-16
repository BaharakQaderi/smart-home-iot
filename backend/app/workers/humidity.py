"""
Humidity sensor worker for realistic humidity data simulation.
Generates humidity readings with daily patterns, seasonal variations, and room-specific characteristics.
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

logger = logging.getLogger(__name__)

class HumidityWorker:
    """Humidity sensor simulation worker."""
    
    def __init__(self):
        self.influx_client = influxdb_client
        self.bucket = "sensors"
        self.org = "smarthome"
        self.is_running = False
        
        # Room configurations with base humidity and characteristics
        self.room_configs = {
            "living_room": {
                "base_humidity": 45.0,
                "humidity_range": 15.0,
                "ventilation_rate": 0.6,
                "sensor_accuracy": 3.0,
                "moisture_sources": ["plants", "people"],
                "dehumidifier": False,
                "ventilation_active": False,
            },
            "bedroom": {
                "base_humidity": 50.0,
                "humidity_range": 20.0,
                "ventilation_rate": 0.4,
                "sensor_accuracy": 2.5,
                "moisture_sources": ["breathing", "plants"],
                "dehumidifier": False,
                "ventilation_active": False,
            },
            "kitchen": {
                "base_humidity": 55.0,
                "humidity_range": 25.0,
                "ventilation_rate": 0.8,
                "sensor_accuracy": 4.0,
                "moisture_sources": ["cooking", "dishwasher", "steam"],
                "dehumidifier": False,
                "ventilation_active": False,
            },
            "bathroom": {
                "base_humidity": 65.0,
                "humidity_range": 30.0,
                "ventilation_rate": 0.9,
                "sensor_accuracy": 3.5,
                "moisture_sources": ["shower", "bathtub", "steam"],
                "dehumidifier": False,
                "ventilation_active": False,
            },
            "basement": {
                "base_humidity": 60.0,
                "humidity_range": 20.0,
                "ventilation_rate": 0.2,
                "sensor_accuracy": 2.0,
                "moisture_sources": ["ground", "seepage"],
                "dehumidifier": True,
                "ventilation_active": False,
            },
            "outdoor": {
                "base_humidity": 70.0,
                "humidity_range": 40.0,
                "ventilation_rate": 1.0,
                "sensor_accuracy": 5.0,
                "moisture_sources": ["weather", "rain", "dew"],
                "dehumidifier": False,
                "ventilation_active": False,
            }
        }
        
        # Initialize room states
        self.room_states = {}
        for room_id, config in self.room_configs.items():
            self.room_states[room_id] = {
                "current_humidity": config["base_humidity"],
                "target_humidity": config["base_humidity"],
                "last_update": datetime.now(),
                "trend": 0.0,
                "ventilation_active": False,
                "dehumidifier_active": False,
                "moisture_event": False,
            }
    
    def get_seasonal_humidity_adjustment(self) -> float:
        """Calculate seasonal humidity adjustment based on current date."""
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        
        # Seasonal humidity pattern: higher in summer, lower in winter
        seasonal_factor = math.sin((day_of_year - 81) * 2 * math.pi / 365)
        return seasonal_factor * 15.0  # ±15% seasonal variation
    
    def get_daily_humidity_pattern(self, room_id: str) -> float:
        """Calculate daily humidity pattern based on time of day and room usage."""
        now = datetime.now()
        hour = now.hour + now.minute / 60.0
        
        # Different patterns for different rooms
        if room_id == "bedroom":
            # Higher at night due to breathing
            daily_factor = 5.0 * math.sin((hour - 18) * math.pi / 12)
        elif room_id == "kitchen":
            # Peaks during meal preparation times
            morning_peak = 8.0 * math.exp(-((hour - 8) ** 2) / 4)
            lunch_peak = 6.0 * math.exp(-((hour - 12) ** 2) / 4)
            evening_peak = 10.0 * math.exp(-((hour - 18) ** 2) / 6)
            daily_factor = morning_peak + lunch_peak + evening_peak
        elif room_id == "bathroom":
            # Peaks during morning and evening routines
            morning_peak = 15.0 * math.exp(-((hour - 7) ** 2) / 2)
            evening_peak = 12.0 * math.exp(-((hour - 20) ** 2) / 4)
            daily_factor = morning_peak + evening_peak
        elif room_id == "living_room":
            # Higher during active hours
            daily_factor = 3.0 * math.sin((hour - 12) * math.pi / 12)
        elif room_id == "outdoor":
            # Higher at night and early morning (dew)
            daily_factor = -8.0 * math.cos((hour - 6) * 2 * math.pi / 24)
        else:
            # Default gentle daily pattern
            daily_factor = 2.0 * math.sin((hour - 12) * math.pi / 12)
        
        return daily_factor
    
    def get_outdoor_humidity(self) -> float:
        """Get current outdoor humidity with realistic patterns."""
        seasonal_humidity = self.get_seasonal_humidity_adjustment()
        daily_pattern = self.get_daily_humidity_pattern("outdoor")
        
        # Base outdoor humidity with seasonal and daily variations
        base_humidity = self.room_configs["outdoor"]["base_humidity"]
        outdoor_humidity = base_humidity + seasonal_humidity + daily_pattern
        
        # Simulate weather events
        weather_effect = 0.0
        if random.random() < 0.1:  # 10% chance of weather event
            if random.random() < 0.7:  # 70% chance it's rain (increases humidity)
                weather_effect = random.uniform(10, 25)
            else:  # 30% chance it's dry/windy (decreases humidity)
                weather_effect = -random.uniform(5, 15)
        
        outdoor_humidity += weather_effect
        
        # Add some random variation
        outdoor_humidity += random.gauss(0, 5.0)
        
        # Ensure humidity is within realistic bounds
        outdoor_humidity = max(20.0, min(95.0, outdoor_humidity))
        
        return outdoor_humidity
    
    def simulate_moisture_events(self, room_id: str) -> float:
        """Simulate moisture-generating events in different rooms."""
        moisture_increase = 0.0
        
        now = datetime.now()
        hour = now.hour
        
        if room_id == "bathroom":
            # Simulate shower/bath usage
            if (6 <= hour <= 9) or (19 <= hour <= 22):  # Morning/evening routines
                if random.random() < 0.3:  # 30% chance during these hours
                    moisture_increase = random.uniform(20, 40)
                    self.room_states[room_id]["moisture_event"] = True
        
        elif room_id == "kitchen":
            # Simulate cooking activities
            if (7 <= hour <= 9) or (11 <= hour <= 13) or (17 <= hour <= 20):  # Meal times
                if random.random() < 0.4:  # 40% chance during meal times
                    moisture_increase = random.uniform(10, 25)
                    self.room_states[room_id]["moisture_event"] = True
        
        elif room_id == "bedroom":
            # Simulate breathing during sleep
            if (22 <= hour or hour <= 6):  # Night hours
                moisture_increase = random.uniform(2, 8)
        
        elif room_id == "living_room":
            # Simulate people activity and plants
            if random.random() < 0.1:  # 10% chance of activity
                moisture_increase = random.uniform(2, 6)
        
        elif room_id == "basement":
            # Simulate ground moisture seepage
            if random.random() < 0.05:  # 5% chance of seepage event
                moisture_increase = random.uniform(5, 15)
        
        return moisture_increase
    
    def update_room_humidity(self, room_id: str, outdoor_humidity: float) -> float:
        """Update room humidity based on various factors."""
        config = self.room_configs[room_id]
        state = self.room_states[room_id]
        
        if room_id == "outdoor":
            # Outdoor humidity is calculated separately
            new_humidity = outdoor_humidity
        else:
            # Calculate base humidity with patterns
            seasonal_adj = self.get_seasonal_humidity_adjustment() * 0.5  # Indoor is less affected
            daily_adj = self.get_daily_humidity_pattern(room_id)
            
            # Start with base humidity
            target_humidity = config["base_humidity"] + seasonal_adj + daily_adj
            
            # Outdoor influence (through ventilation)
            outdoor_influence = (outdoor_humidity - config["base_humidity"]) * config["ventilation_rate"] * 0.1
            target_humidity += outdoor_influence
            
            # Moisture events
            moisture_event = self.simulate_moisture_events(room_id)
            target_humidity += moisture_event
            
            # Current humidity change calculation
            humidity_diff = target_humidity - state["current_humidity"]
            
            # Ventilation system logic
            if state["current_humidity"] > 60 and config["ventilation_rate"] > 0.5:
                state["ventilation_active"] = True
            elif state["current_humidity"] < 45:
                state["ventilation_active"] = False
            
            # Dehumidifier logic (for basement and bathroom)
            if config["dehumidifier"] and state["current_humidity"] > 55:
                state["dehumidifier_active"] = True
            elif state["current_humidity"] < 50:
                state["dehumidifier_active"] = False
            
            # Apply ventilation effects
            if state["ventilation_active"]:
                # Ventilation moves humidity toward outdoor level
                ventilation_effect = (outdoor_humidity - state["current_humidity"]) * 0.1
                humidity_diff += ventilation_effect
            
            # Apply dehumidifier effects
            if state["dehumidifier_active"]:
                humidity_diff -= 5.0  # Dehumidifier reduces humidity
            
            # Natural humidity change rate (slower than temperature)
            change_rate = humidity_diff * 0.05
            
            # Apply the change
            new_humidity = state["current_humidity"] + change_rate
            
            # Add sensor noise
            noise = random.gauss(0, config["sensor_accuracy"] * 0.1)
            new_humidity += noise
        
        # Update state
        state["current_humidity"] = new_humidity
        state["last_update"] = datetime.now()
        
        # Reset moisture event flag
        if room_id != "outdoor":
            state["moisture_event"] = False
        
        # Ensure humidity is within bounds
        new_humidity = max(20.0, min(95.0, new_humidity))
        
        return new_humidity
    
    def get_comfort_level(self, humidity: float) -> str:
        """Determine comfort level based on humidity."""
        if humidity < 30:
            return "very_dry"
        elif humidity < 40:
            return "dry"
        elif humidity <= 60:
            return "comfortable"
        elif humidity <= 70:
            return "humid"
        else:
            return "very_humid"
    
    async def generate_humidity_reading(self, room_id: str, sensor_id: str) -> Dict:
        """Generate a realistic humidity reading for a room."""
        outdoor_humidity = self.get_outdoor_humidity()
        humidity = self.update_room_humidity(room_id, outdoor_humidity)
        
        # Ensure humidity is within realistic bounds
        humidity = max(20.0, min(95.0, humidity))
        
        reading = {
            "sensor_id": sensor_id,
            "room_id": room_id,
            "humidity": round(humidity, 1),
            "unit": "%",
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "humidity",
            "comfort_level": self.get_comfort_level(humidity),
            "ventilation_active": self.room_states[room_id].get("ventilation_active", False),
            "dehumidifier_active": self.room_states[room_id].get("dehumidifier_active", False),
            "moisture_event": self.room_states[room_id].get("moisture_event", False),
            "outdoor_humidity": round(outdoor_humidity, 1),
        }
        
        return reading
    
    async def write_to_influxdb(self, reading: Dict):
        """Write humidity reading to InfluxDB."""
        try:
            tags = {
                "room_id": reading["room_id"],
                "sensor_id": reading["sensor_id"],
                "sensor_type": "humidity",
                "comfort_level": reading["comfort_level"]
            }
            
            fields = {
                "value": reading["humidity"],
                "unit": reading["unit"],
                "ventilation_active": reading["ventilation_active"],
                "dehumidifier_active": reading["dehumidifier_active"],
                "moisture_event": reading["moisture_event"],
                "outdoor_humidity": reading["outdoor_humidity"]
            }
            
            await self.influx_client.write_sensor_data("humidity", tags, fields)
            logger.debug(f"Humidity reading written to InfluxDB: {reading['room_id']} = {reading['humidity']}%")
            
        except Exception as e:
            logger.error(f"Error writing humidity to InfluxDB: {e}")
    
    async def broadcast_reading(self, reading: Dict):
        """Broadcast humidity reading via WebSocket."""
        try:
            message = {
                "type": "humidity_update",
                "data": reading
            }
            await websocket_manager.broadcast_message(message)
            logger.debug(f"Humidity reading broadcast: {reading['room_id']} = {reading['humidity']}%")
            
        except Exception as e:
            logger.error(f"Error broadcasting humidity reading: {e}")
    
    async def run_sensor_loop(self):
        """Main sensor loop that generates and processes humidity readings."""
        logger.info("Starting humidity sensor worker...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Generate readings for all rooms
                for room_id in self.room_configs.keys():
                    sensor_id = f"humid_{room_id}_001"
                    
                    # Generate humidity reading
                    reading = await self.generate_humidity_reading(room_id, sensor_id)
                    
                    # Write to InfluxDB
                    await self.write_to_influxdb(reading)
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_reading(reading)
                
                # Wait for next reading (30 seconds as per spec)
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in humidity sensor loop: {e}")
                await asyncio.sleep(5)  # Short retry delay
    
    async def start(self):
        """Start the humidity sensor worker."""
        if not self.is_running:
            asyncio.create_task(self.run_sensor_loop())
    
    async def stop(self):
        """Stop the humidity sensor worker."""
        logger.info("Stopping humidity sensor worker...")
        self.is_running = False

# Global instance
humidity_worker = HumidityWorker() 