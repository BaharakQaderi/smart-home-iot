"""
Sensor Configuration Management
=============================

This module contains all configuration parameters for sensor simulation,
eliminating magic numbers and providing centralized configuration management.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
import json
import os
from pathlib import Path


class SensorType(str, Enum):
    """Sensor types enum."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    ENERGY = "energy"
    SECURITY = "security"
    AIR_QUALITY = "air_quality"


class UsagePattern(str, Enum):
    """Device usage patterns."""
    CONSTANT = "constant"
    EVENING = "evening"
    MORNING = "morning"
    MEAL_PREP = "meal_prep"
    MEAL_CLEANUP = "meal_cleanup"
    NIGHT = "night"
    BATHROOM_USE = "bathroom_use"
    HOT_WATER = "hot_water"
    SEASONAL = "seasonal"
    INTERMITTENT = "intermittent"
    HUMIDITY = "humidity"
    WEEKEND = "weekend"
    COMMUTE = "commute"
    SCHEDULED = "scheduled"
    OCCASIONAL = "occasional"
    RANDOM = "random"


class TemperatureConfig(BaseModel):
    """Temperature sensor configuration."""
    # Global temperature settings
    global_min_temp: float = Field(default=-30.0, description="Global minimum temperature (°C)")
    global_max_temp: float = Field(default=50.0, description="Global maximum temperature (°C)")
    
    # Comfort zones
    comfort_optimal_min: float = Field(default=20.0, description="Optimal comfort minimum (°C)")
    comfort_optimal_max: float = Field(default=24.0, description="Optimal comfort maximum (°C)")
    comfort_acceptable_min: float = Field(default=18.0, description="Acceptable comfort minimum (°C)")
    comfort_acceptable_max: float = Field(default=26.0, description="Acceptable comfort maximum (°C)")
    
    # Alert thresholds
    alert_critical_min: float = Field(default=10.0, description="Critical low temperature alert (°C)")
    alert_critical_max: float = Field(default=35.0, description="Critical high temperature alert (°C)")
    alert_warning_min: float = Field(default=16.0, description="Warning low temperature alert (°C)")
    alert_warning_max: float = Field(default=28.0, description="Warning high temperature alert (°C)")
    
    # Simulation parameters
    seasonal_variation: float = Field(default=8.0, description="Seasonal temperature variation (°C)")
    daily_variation: float = Field(default=5.0, description="Daily temperature variation (°C)")
    sensor_noise_factor: float = Field(default=0.1, description="Sensor noise factor")
    
    # Room-specific configurations
    room_configs: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "living_room": {
            "base_temp": 22.0,
            "temp_range": 3.0,
            "heating_efficiency": 0.8,
            "sensor_accuracy": 0.5,
            "thermal_mass": 0.7,
            "external_influence": 0.6,
        },
        "bedroom": {
            "base_temp": 20.0,
            "temp_range": 2.5,
            "heating_efficiency": 0.9,
            "sensor_accuracy": 0.4,
            "thermal_mass": 0.8,
            "external_influence": 0.4,
        },
        "kitchen": {
            "base_temp": 23.0,
            "temp_range": 4.0,
            "heating_efficiency": 0.6,
            "sensor_accuracy": 0.6,
            "thermal_mass": 0.5,
            "external_influence": 0.7,
        },
        "bathroom": {
            "base_temp": 24.0,
            "temp_range": 5.0,
            "heating_efficiency": 0.7,
            "sensor_accuracy": 0.5,
            "thermal_mass": 0.6,
            "external_influence": 0.3,
        },
        "basement": {
            "base_temp": 18.0,
            "temp_range": 2.0,
            "heating_efficiency": 0.5,
            "sensor_accuracy": 0.3,
            "thermal_mass": 0.9,
            "external_influence": 0.2,
        },
        "outdoor": {
            "base_temp": 15.0,
            "temp_range": 12.0,
            "heating_efficiency": 0.0,
            "sensor_accuracy": 0.8,
            "thermal_mass": 0.3,
            "external_influence": 1.0,
        }
    })


class HumidityConfig(BaseModel):
    """Humidity sensor configuration."""
    # Global humidity settings
    global_min_humidity: float = Field(default=20.0, description="Global minimum humidity (%)")
    global_max_humidity: float = Field(default=95.0, description="Global maximum humidity (%)")
    
    # Comfort zones
    comfort_optimal_min: float = Field(default=40.0, description="Optimal comfort minimum (%)")
    comfort_optimal_max: float = Field(default=60.0, description="Optimal comfort maximum (%)")
    comfort_acceptable_min: float = Field(default=35.0, description="Acceptable comfort minimum (%)")
    comfort_acceptable_max: float = Field(default=65.0, description="Acceptable comfort maximum (%)")
    
    # Alert thresholds
    alert_critical_min: float = Field(default=25.0, description="Critical low humidity alert (%)")
    alert_critical_max: float = Field(default=80.0, description="Critical high humidity alert (%)")
    alert_warning_min: float = Field(default=30.0, description="Warning low humidity alert (%)")
    alert_warning_max: float = Field(default=70.0, description="Warning high humidity alert (%)")
    
    # Simulation parameters
    seasonal_variation: float = Field(default=15.0, description="Seasonal humidity variation (%)")
    daily_variation: float = Field(default=10.0, description="Daily humidity variation (%)")
    sensor_noise_factor: float = Field(default=0.1, description="Sensor noise factor")
    
    # Room-specific configurations
    room_configs: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "living_room": {
            "base_humidity": 45.0,
            "humidity_range": 15.0,
            "ventilation_rate": 0.6,
            "sensor_accuracy": 3.0,
            "moisture_sources": ["plants", "people"],
            "dehumidifier": False,
        },
        "bedroom": {
            "base_humidity": 50.0,
            "humidity_range": 20.0,
            "ventilation_rate": 0.4,
            "sensor_accuracy": 2.5,
            "moisture_sources": ["breathing", "plants"],
            "dehumidifier": False,
        },
        "kitchen": {
            "base_humidity": 55.0,
            "humidity_range": 25.0,
            "ventilation_rate": 0.8,
            "sensor_accuracy": 4.0,
            "moisture_sources": ["cooking", "dishwasher", "steam"],
            "dehumidifier": False,
        },
        "bathroom": {
            "base_humidity": 65.0,
            "humidity_range": 30.0,
            "ventilation_rate": 0.9,
            "sensor_accuracy": 3.5,
            "moisture_sources": ["shower", "bathtub", "steam"],
            "dehumidifier": False,
        },
        "basement": {
            "base_humidity": 60.0,
            "humidity_range": 20.0,
            "ventilation_rate": 0.2,
            "sensor_accuracy": 2.0,
            "moisture_sources": ["ground", "seepage"],
            "dehumidifier": True,
        },
        "outdoor": {
            "base_humidity": 70.0,
            "humidity_range": 40.0,
            "ventilation_rate": 1.0,
            "sensor_accuracy": 5.0,
            "moisture_sources": ["weather", "rain", "dew"],
            "dehumidifier": False,
        }
    })


class DeviceConfig(BaseModel):
    """Device configuration for energy monitoring."""
    base_power: float = Field(description="Base power consumption (W)")
    standby_power: float = Field(description="Standby power consumption (W)")
    usage_pattern: UsagePattern = Field(description="Device usage pattern")
    efficiency_rating: float = Field(default=0.85, description="Device efficiency rating (0.0-1.0)")
    priority: int = Field(default=1, description="Device priority (1-5)")
    
    @validator('efficiency_rating')
    def validate_efficiency(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Efficiency rating must be between 0.0 and 1.0')
        return v


class EnergyConfig(BaseModel):
    """Energy monitoring configuration."""
    # Global energy settings
    global_max_power: float = Field(default=10000.0, description="Global maximum power consumption (W)")
    global_max_daily_kwh: float = Field(default=50.0, description="Global maximum daily consumption (kWh)")
    
    # Pricing configuration
    energy_rates: Dict[str, float] = Field(default_factory=lambda: {
        "peak": 0.28,      # 6 PM - 9 PM
        "off_peak": 0.12,  # 11 PM - 6 AM
        "standard": 0.18,  # All other times
    })
    
    # Peak hours configuration
    peak_hours: Dict[str, List[int]] = Field(default_factory=lambda: {
        "peak": [18, 19, 20],  # 6 PM - 9 PM
        "off_peak": [23, 0, 1, 2, 3, 4, 5],  # 11 PM - 6 AM
    })
    
    # Alert thresholds
    alert_high_power: float = Field(default=5000.0, description="High power consumption alert (W)")
    alert_critical_power: float = Field(default=8000.0, description="Critical power consumption alert (W)")
    alert_daily_kwh: float = Field(default=30.0, description="Daily consumption alert (kWh)")
    
    # Simulation parameters
    power_fluctuation_factor: float = Field(default=0.15, description="Power fluctuation factor")
    seasonal_factor_range: float = Field(default=0.5, description="Seasonal factor range")
    
    # Device configurations by room
    device_configs: Dict[str, Dict[str, DeviceConfig]] = Field(default_factory=lambda: {
        "living_room": {
            "tv": DeviceConfig(base_power=150, standby_power=5, usage_pattern=UsagePattern.EVENING),
            "sound_system": DeviceConfig(base_power=80, standby_power=2, usage_pattern=UsagePattern.EVENING),
            "lighting": DeviceConfig(base_power=120, standby_power=0, usage_pattern=UsagePattern.EVENING),
            "air_conditioning": DeviceConfig(base_power=2500, standby_power=0, usage_pattern=UsagePattern.SEASONAL),
            "smart_plugs": DeviceConfig(base_power=50, standby_power=1, usage_pattern=UsagePattern.RANDOM),
        },
        "kitchen": {
            "refrigerator": DeviceConfig(base_power=200, standby_power=150, usage_pattern=UsagePattern.CONSTANT),
            "dishwasher": DeviceConfig(base_power=1800, standby_power=3, usage_pattern=UsagePattern.MEAL_CLEANUP),
            "microwave": DeviceConfig(base_power=1200, standby_power=2, usage_pattern=UsagePattern.MEAL_PREP),
            "oven": DeviceConfig(base_power=3000, standby_power=0, usage_pattern=UsagePattern.MEAL_PREP),
            "coffee_maker": DeviceConfig(base_power=800, standby_power=5, usage_pattern=UsagePattern.MORNING),
            "lighting": DeviceConfig(base_power=80, standby_power=0, usage_pattern=UsagePattern.MEAL_PREP),
        },
        "bedroom": {
            "lighting": DeviceConfig(base_power=60, standby_power=0, usage_pattern=UsagePattern.EVENING),
            "phone_charger": DeviceConfig(base_power=12, standby_power=2, usage_pattern=UsagePattern.NIGHT),
            "laptop": DeviceConfig(base_power=65, standby_power=3, usage_pattern=UsagePattern.EVENING),
            "fan": DeviceConfig(base_power=75, standby_power=0, usage_pattern=UsagePattern.NIGHT),
            "air_purifier": DeviceConfig(base_power=50, standby_power=5, usage_pattern=UsagePattern.CONSTANT),
        },
        "bathroom": {
            "lighting": DeviceConfig(base_power=40, standby_power=0, usage_pattern=UsagePattern.MORNING),
            "exhaust_fan": DeviceConfig(base_power=30, standby_power=0, usage_pattern=UsagePattern.BATHROOM_USE),
            "hair_dryer": DeviceConfig(base_power=1500, standby_power=0, usage_pattern=UsagePattern.MORNING),
            "water_heater": DeviceConfig(base_power=4000, standby_power=200, usage_pattern=UsagePattern.HOT_WATER),
        },
        "basement": {
            "water_pump": DeviceConfig(base_power=750, standby_power=0, usage_pattern=UsagePattern.INTERMITTENT),
            "dehumidifier": DeviceConfig(base_power=300, standby_power=5, usage_pattern=UsagePattern.HUMIDITY),
            "storage_lighting": DeviceConfig(base_power=25, standby_power=0, usage_pattern=UsagePattern.OCCASIONAL),
            "workshop_tools": DeviceConfig(base_power=500, standby_power=0, usage_pattern=UsagePattern.WEEKEND),
        },
        "outdoor": {
            "security_lighting": DeviceConfig(base_power=100, standby_power=10, usage_pattern=UsagePattern.NIGHT),
            "garage_door": DeviceConfig(base_power=800, standby_power=5, usage_pattern=UsagePattern.COMMUTE),
            "garden_irrigation": DeviceConfig(base_power=200, standby_power=0, usage_pattern=UsagePattern.SCHEDULED),
            "pool_pump": DeviceConfig(base_power=1200, standby_power=0, usage_pattern=UsagePattern.SEASONAL),
        }
    })


class SimulationConfig(BaseModel):
    """Simulation timing and intervals configuration."""
    # Data generation intervals (seconds)
    temperature_interval: int = Field(default=30, description="Temperature data generation interval")
    humidity_interval: int = Field(default=30, description="Humidity data generation interval")
    energy_interval: int = Field(default=60, description="Energy data generation interval")
    security_interval: int = Field(default=5, description="Security data generation interval")
    air_quality_interval: int = Field(default=60, description="Air quality data generation interval")
    
    # Batch processing
    batch_size: int = Field(default=100, description="Batch size for data processing")
    batch_flush_interval: int = Field(default=5, description="Batch flush interval (seconds)")
    
    # Health check intervals
    health_check_interval: int = Field(default=60, description="Health check interval (seconds)")
    status_broadcast_interval: int = Field(default=30, description="Status broadcast interval (seconds)")
    
    # Data retention
    data_retention_hours: int = Field(default=24, description="Data retention in hours")
    cleanup_interval_hours: int = Field(default=6, description="Cleanup interval in hours")


class SensorSystemConfig(BaseModel):
    """Complete sensor system configuration."""
    temperature: TemperatureConfig = Field(default_factory=TemperatureConfig)
    humidity: HumidityConfig = Field(default_factory=HumidityConfig)
    energy: EnergyConfig = Field(default_factory=EnergyConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
    
    # System-wide settings
    enable_realistic_patterns: bool = Field(default=True, description="Enable realistic usage patterns")
    enable_seasonal_variations: bool = Field(default=True, description="Enable seasonal variations")
    enable_weather_influence: bool = Field(default=True, description="Enable weather influence")
    enable_smart_automation: bool = Field(default=True, description="Enable smart automation responses")
    
    # Logging and monitoring
    enable_debug_logging: bool = Field(default=False, description="Enable debug logging")
    enable_performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    enable_data_validation: bool = Field(default=True, description="Enable data validation")


class ConfigManager:
    """Configuration manager for loading and managing sensor configurations."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "sensor_config.json"
        self.config_path = Path(__file__).parent / self.config_file
        self._config: Optional[SensorSystemConfig] = None
    
    def load_config(self) -> SensorSystemConfig:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                self._config = SensorSystemConfig.parse_obj(config_data)
                return self._config
            except Exception as e:
                print(f"Error loading config file: {e}")
                print("Using default configuration...")
        
        # Create default configuration
        self._config = SensorSystemConfig()
        self.save_config()
        return self._config
    
    def save_config(self):
        """Save current configuration to file."""
        if self._config:
            # Ensure config directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(self._config.dict(), f, indent=2)
    
    def get_config(self) -> SensorSystemConfig:
        """Get current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def update_config(self, **kwargs):
        """Update configuration parameters."""
        if self._config is None:
            self.load_config()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self.save_config()
    
    def get_room_temperature_config(self, room_id: str) -> Dict[str, Any]:
        """Get temperature configuration for a specific room."""
        config = self.get_config()
        return config.temperature.room_configs.get(room_id, {})
    
    def get_room_humidity_config(self, room_id: str) -> Dict[str, Any]:
        """Get humidity configuration for a specific room."""
        config = self.get_config()
        return config.humidity.room_configs.get(room_id, {})
    
    def get_room_devices_config(self, room_id: str) -> Dict[str, DeviceConfig]:
        """Get device configurations for a specific room."""
        config = self.get_config()
        return config.energy.device_configs.get(room_id, {})
    
    def validate_config(self) -> bool:
        """Validate current configuration."""
        try:
            config = self.get_config()
            # Additional validation logic here
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigManager()

# Convenience functions for accessing configuration
def get_temperature_config() -> TemperatureConfig:
    """Get temperature configuration."""
    return config_manager.get_config().temperature

def get_humidity_config() -> HumidityConfig:
    """Get humidity configuration."""
    return config_manager.get_config().humidity

def get_energy_config() -> EnergyConfig:
    """Get energy configuration."""
    return config_manager.get_config().energy

def get_simulation_config() -> SimulationConfig:
    """Get simulation configuration."""
    return config_manager.get_config().simulation

def get_sensor_config() -> SensorSystemConfig:
    """Get complete sensor system configuration."""
    return config_manager.get_config() 