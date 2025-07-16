"""
Energy monitoring worker for realistic power consumption simulation.
Simulates smart meters, device-level monitoring, and energy cost calculations.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from app.core.database import influxdb_client
from app.core.websocket import websocket_manager

logger = logging.getLogger(__name__)

class EnergyWorker:
    """Energy monitoring sensor simulation worker."""
    
    def __init__(self):
        self.influx_client = influxdb_client
        self.bucket = "sensors"
        self.org = "smarthome"
        self.is_running = False
        
        # Energy pricing (per kWh)
        self.energy_rates = {
            "peak": 0.28,      # 6 PM - 9 PM
            "off_peak": 0.12,  # 11 PM - 6 AM
            "standard": 0.18,  # All other times
        }
        
        # Device configurations with power consumption patterns
        self.device_configs = {
            "living_room": {
                "tv": {"base_power": 150, "standby": 5, "usage_pattern": "evening"},
                "sound_system": {"base_power": 80, "standby": 2, "usage_pattern": "evening"},
                "lighting": {"base_power": 120, "standby": 0, "usage_pattern": "evening"},
                "air_conditioning": {"base_power": 2500, "standby": 0, "usage_pattern": "seasonal"},
                "smart_plugs": {"base_power": 50, "standby": 1, "usage_pattern": "random"},
            },
            "kitchen": {
                "refrigerator": {"base_power": 200, "standby": 150, "usage_pattern": "constant"},
                "dishwasher": {"base_power": 1800, "standby": 3, "usage_pattern": "meal_cleanup"},
                "microwave": {"base_power": 1200, "standby": 2, "usage_pattern": "meal_prep"},
                "oven": {"base_power": 3000, "standby": 0, "usage_pattern": "cooking"},
                "coffee_maker": {"base_power": 800, "standby": 5, "usage_pattern": "morning"},
                "lighting": {"base_power": 80, "standby": 0, "usage_pattern": "meal_times"},
            },
            "bedroom": {
                "lighting": {"base_power": 60, "standby": 0, "usage_pattern": "evening_morning"},
                "phone_charger": {"base_power": 12, "standby": 2, "usage_pattern": "night"},
                "laptop": {"base_power": 65, "standby": 3, "usage_pattern": "evening"},
                "fan": {"base_power": 75, "standby": 0, "usage_pattern": "night"},
                "air_purifier": {"base_power": 50, "standby": 5, "usage_pattern": "constant"},
            },
            "bathroom": {
                "lighting": {"base_power": 40, "standby": 0, "usage_pattern": "morning_evening"},
                "exhaust_fan": {"base_power": 30, "standby": 0, "usage_pattern": "bathroom_use"},
                "hair_dryer": {"base_power": 1500, "standby": 0, "usage_pattern": "morning"},
                "water_heater": {"base_power": 4000, "standby": 200, "usage_pattern": "hot_water"},
            },
            "basement": {
                "water_pump": {"base_power": 750, "standby": 0, "usage_pattern": "intermittent"},
                "dehumidifier": {"base_power": 300, "standby": 5, "usage_pattern": "humidity"},
                "storage_lighting": {"base_power": 25, "standby": 0, "usage_pattern": "occasional"},
                "workshop_tools": {"base_power": 500, "standby": 0, "usage_pattern": "weekend"},
            },
            "outdoor": {
                "security_lighting": {"base_power": 100, "standby": 10, "usage_pattern": "night"},
                "garage_door": {"base_power": 800, "standby": 5, "usage_pattern": "commute"},
                "garden_irrigation": {"base_power": 200, "standby": 0, "usage_pattern": "scheduled"},
                "pool_pump": {"base_power": 1200, "standby": 0, "usage_pattern": "seasonal"},
            }
        }
        
        # Initialize device states
        self.device_states = {}
        for room_id, devices in self.device_configs.items():
            self.device_states[room_id] = {}
            for device_id, config in devices.items():
                self.device_states[room_id][device_id] = {
                    "current_power": config["standby"],
                    "is_active": False,
                    "last_update": datetime.now(),
                    "daily_consumption": 0.0,
                    "monthly_consumption": 0.0,
                    "usage_hours": 0.0,
                    "efficiency_rating": random.uniform(0.8, 1.0),
                }
        
        # Room totals
        self.room_totals = {}
        for room_id in self.device_configs.keys():
            self.room_totals[room_id] = {
                "current_power": 0.0,
                "daily_consumption": 0.0,
                "monthly_consumption": 0.0,
                "peak_power": 0.0,
                "average_power": 0.0,
                "cost_today": 0.0,
                "cost_month": 0.0,
            }
    
    def get_energy_rate(self) -> Tuple[float, str]:
        """Get current energy rate based on time of day."""
        now = datetime.now()
        hour = now.hour
        
        if 18 <= hour <= 21:  # Peak hours
            return self.energy_rates["peak"], "peak"
        elif 23 <= hour or hour <= 6:  # Off-peak hours
            return self.energy_rates["off_peak"], "off_peak"
        else:  # Standard hours
            return self.energy_rates["standard"], "standard"
    
    def get_seasonal_factor(self) -> float:
        """Calculate seasonal energy usage factor."""
        now = datetime.now()
        day_of_year = now.timetuple().tm_yday
        
        # Higher usage in summer (AC) and winter (heating)
        seasonal_factor = 1.0 + 0.3 * abs(math.sin((day_of_year - 81) * 2 * math.pi / 365))
        return seasonal_factor
    
    def calculate_device_usage(self, room_id: str, device_id: str, config: Dict) -> float:
        """Calculate device power usage based on patterns and time."""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
        
        usage_pattern = config["usage_pattern"]
        base_power = config["base_power"]
        standby_power = config["standby"]
        
        # Default to standby power
        power_usage = standby_power
        is_active = False
        
        # Pattern-based usage calculation
        if usage_pattern == "constant":
            # Always on devices like refrigerator
            power_usage = base_power
            is_active = True
            
        elif usage_pattern == "evening":
            # TV, sound system, living room lighting
            if 18 <= hour <= 23:
                usage_probability = 0.7 + 0.3 * math.sin((hour - 18) * math.pi / 5)
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.6, 1.0)
                    is_active = True
            
        elif usage_pattern == "morning":
            # Coffee maker, hair dryer
            if 6 <= hour <= 9:
                usage_probability = 0.8 * math.exp(-((hour - 7.5) ** 2) / 2)
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.8, 1.0)
                    is_active = True
            
        elif usage_pattern == "meal_prep":
            # Microwave, oven during meal times
            if (7 <= hour <= 9) or (12 <= hour <= 14) or (17 <= hour <= 20):
                usage_probability = 0.4 * math.exp(-((hour - 12) ** 2) / 20)
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.7, 1.0)
                    is_active = True
            
        elif usage_pattern == "meal_cleanup":
            # Dishwasher after meals
            if (8 <= hour <= 10) or (13 <= hour <= 15) or (19 <= hour <= 22):
                usage_probability = 0.3
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.8, 1.0)
                    is_active = True
            
        elif usage_pattern == "cooking":
            # Oven for cooking
            if (11 <= hour <= 14) or (17 <= hour <= 20):
                usage_probability = 0.2
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.9, 1.0)
                    is_active = True
            
        elif usage_pattern == "meal_times":
            # Kitchen lighting during meals
            if (7 <= hour <= 9) or (12 <= hour <= 14) or (17 <= hour <= 21):
                usage_probability = 0.8
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.8, 1.0)
                    is_active = True
            
        elif usage_pattern == "evening_morning":
            # Bedroom lighting
            if (6 <= hour <= 8) or (19 <= hour <= 23):
                usage_probability = 0.6
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.5, 1.0)
                    is_active = True
            
        elif usage_pattern == "morning_evening":
            # Bathroom lighting
            if (6 <= hour <= 9) or (19 <= hour <= 23):
                usage_probability = 0.7
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.8, 1.0)
                    is_active = True
            
        elif usage_pattern == "night":
            # Phone charger, fan
            if 22 <= hour or hour <= 6:
                usage_probability = 0.8
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.6, 1.0)
                    is_active = True
            
        elif usage_pattern == "bathroom_use":
            # Exhaust fan
            if (6 <= hour <= 9) or (19 <= hour <= 23):
                usage_probability = 0.4
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.8, 1.0)
                    is_active = True
            
        elif usage_pattern == "hot_water":
            # Water heater
            if (6 <= hour <= 9) or (18 <= hour <= 22):
                usage_probability = 0.5
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.7, 1.0)
                    is_active = True
                else:
                    power_usage = standby_power
            
        elif usage_pattern == "seasonal":
            # Air conditioning, pool pump
            seasonal_factor = self.get_seasonal_factor()
            if seasonal_factor > 1.2:  # High seasonal usage
                if 10 <= hour <= 22:
                    usage_probability = 0.6 * seasonal_factor
                    if random.random() < usage_probability:
                        power_usage = base_power * random.uniform(0.8, 1.0)
                        is_active = True
            
        elif usage_pattern == "intermittent":
            # Water pump, intermittent devices
            usage_probability = 0.1
            if random.random() < usage_probability:
                power_usage = base_power * random.uniform(0.8, 1.0)
                is_active = True
            
        elif usage_pattern == "humidity":
            # Dehumidifier based on humidity (simplified)
            if random.random() < 0.3:  # 30% chance when humidity is high
                power_usage = base_power * random.uniform(0.7, 1.0)
                is_active = True
            
        elif usage_pattern == "weekend":
            # Workshop tools mainly on weekends
            if day_of_week >= 5:  # Saturday or Sunday
                if 9 <= hour <= 17:
                    usage_probability = 0.3
                    if random.random() < usage_probability:
                        power_usage = base_power * random.uniform(0.8, 1.0)
                        is_active = True
            
        elif usage_pattern == "commute":
            # Garage door during commute times
            if (7 <= hour <= 9) or (17 <= hour <= 19):
                usage_probability = 0.2
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.9, 1.0)
                    is_active = True
            
        elif usage_pattern == "scheduled":
            # Garden irrigation at specific times
            if hour in [6, 18]:  # 6 AM and 6 PM
                usage_probability = 0.8
                if random.random() < usage_probability:
                    power_usage = base_power * random.uniform(0.9, 1.0)
                    is_active = True
            
        elif usage_pattern == "occasional":
            # Storage lighting, occasional use
            usage_probability = 0.05
            if random.random() < usage_probability:
                power_usage = base_power * random.uniform(0.8, 1.0)
                is_active = True
            
        elif usage_pattern == "random":
            # Smart plugs, random usage
            usage_probability = 0.3
            if random.random() < usage_probability:
                power_usage = base_power * random.uniform(0.4, 1.0)
                is_active = True
        
        # Apply efficiency rating
        efficiency = self.device_states[room_id][device_id]["efficiency_rating"]
        power_usage = power_usage / efficiency
        
        # Update device state
        self.device_states[room_id][device_id]["current_power"] = power_usage
        self.device_states[room_id][device_id]["is_active"] = is_active
        self.device_states[room_id][device_id]["last_update"] = datetime.now()
        
        return power_usage
    
    def calculate_energy_cost(self, power_kw: float, hours: float) -> float:
        """Calculate energy cost based on current rate."""
        rate, rate_type = self.get_energy_rate()
        return power_kw * hours * rate
    
    async def generate_energy_reading(self, room_id: str) -> Dict:
        """Generate realistic energy reading for a room."""
        room_power = 0.0
        device_readings = {}
        
        # Calculate power for each device in the room
        for device_id, config in self.device_configs[room_id].items():
            device_power = self.calculate_device_usage(room_id, device_id, config)
            room_power += device_power
            
            device_readings[device_id] = {
                "power": round(device_power, 2),
                "is_active": self.device_states[room_id][device_id]["is_active"],
                "efficiency": round(self.device_states[room_id][device_id]["efficiency_rating"], 2),
            }
        
        # Update room totals
        self.room_totals[room_id]["current_power"] = room_power
        
        # Calculate daily consumption (assuming 30-second intervals)
        consumption_increment = room_power / 1000 * (30 / 3600)  # kWh
        self.room_totals[room_id]["daily_consumption"] += consumption_increment
        
        # Calculate costs
        rate, rate_type = self.get_energy_rate()
        cost_increment = consumption_increment * rate
        self.room_totals[room_id]["cost_today"] += cost_increment
        
        # Update peak power if necessary
        if room_power > self.room_totals[room_id]["peak_power"]:
            self.room_totals[room_id]["peak_power"] = room_power
        
        reading = {
            "room_id": room_id,
            "timestamp": datetime.now().isoformat(),
            "sensor_type": "energy",
            "current_power": round(room_power, 2),
            "unit": "W",
            "daily_consumption": round(self.room_totals[room_id]["daily_consumption"], 4),
            "consumption_unit": "kWh",
            "cost_today": round(self.room_totals[room_id]["cost_today"], 2),
            "cost_currency": "USD",
            "energy_rate": rate,
            "rate_type": rate_type,
            "peak_power": round(self.room_totals[room_id]["peak_power"], 2),
            "device_count": len(device_readings),
            "active_devices": sum(1 for d in device_readings.values() if d["is_active"]),
            "devices": device_readings,
        }
        
        return reading
    
    async def write_to_influxdb(self, reading: Dict):
        """Write energy reading to InfluxDB."""
        try:
            # Main room energy point
            tags = {
                "room_id": reading["room_id"],
                "sensor_type": "energy",
                "rate_type": reading["rate_type"]
            }
            
            fields = {
                "current_power": reading["current_power"],
                "daily_consumption": reading["daily_consumption"],
                "cost_today": reading["cost_today"],
                "energy_rate": reading["energy_rate"],
                "peak_power": reading["peak_power"],
                "device_count": reading["device_count"],
                "active_devices": reading["active_devices"]
            }
            
            await self.influx_client.write_sensor_data("energy_consumption", tags, fields)
            
            # Individual device points
            for device_id, device_data in reading["devices"].items():
                device_tags = {
                    "room_id": reading["room_id"],
                    "device_id": device_id,
                    "sensor_type": "energy"
                }
                
                device_fields = {
                    "power": device_data["power"],
                    "is_active": device_data["is_active"],
                    "efficiency": device_data["efficiency"]
                }
                
                await self.influx_client.write_sensor_data("device_energy", device_tags, device_fields)
            
            logger.debug(f"Energy reading written to InfluxDB: {reading['room_id']} = {reading['current_power']}W")
            
        except Exception as e:
            logger.error(f"Error writing energy to InfluxDB: {e}")
    
    async def broadcast_reading(self, reading: Dict):
        """Broadcast energy reading via WebSocket."""
        try:
            message = {
                "type": "energy_update",
                "data": reading
            }
            await websocket_manager.broadcast_message(message)
            logger.debug(f"Energy reading broadcast: {reading['room_id']} = {reading['current_power']}W")
            
        except Exception as e:
            logger.error(f"Error broadcasting energy reading: {e}")
    
    async def run_sensor_loop(self):
        """Main sensor loop that generates and processes energy readings."""
        logger.info("Starting energy sensor worker...")
        self.is_running = True
        
        while self.is_running:
            try:
                # Generate readings for all rooms
                for room_id in self.device_configs.keys():
                    # Generate energy reading
                    reading = await self.generate_energy_reading(room_id)
                    
                    # Write to InfluxDB
                    await self.write_to_influxdb(reading)
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_reading(reading)
                
                # Wait for next reading (30 seconds as per spec)
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in energy sensor loop: {e}")
                await asyncio.sleep(5)  # Short retry delay
    
    async def start(self):
        """Start the energy sensor worker."""
        if not self.is_running:
            asyncio.create_task(self.run_sensor_loop())
    
    async def stop(self):
        """Stop the energy sensor worker."""
        logger.info("Stopping energy sensor worker...")
        self.is_running = False
    
    async def get_total_consumption(self) -> Dict:
        """Get total home energy consumption."""
        total_power = sum(room["current_power"] for room in self.room_totals.values())
        total_daily = sum(room["daily_consumption"] for room in self.room_totals.values())
        total_cost = sum(room["cost_today"] for room in self.room_totals.values())
        peak_power = max(room["peak_power"] for room in self.room_totals.values())
        
        return {
            "total_power": round(total_power, 2),
            "total_daily_consumption": round(total_daily, 4),
            "total_cost_today": round(total_cost, 2),
            "peak_power": round(peak_power, 2),
            "room_breakdown": self.room_totals,
        }

# Global instance
energy_worker = EnergyWorker() 