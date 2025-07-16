# Configuration Management Guide

## Overview

This document describes the comprehensive configuration management system implemented to eliminate magic numbers and hardcoded values from the Smart Home IoT project. The system provides centralized, type-safe configuration management for both backend and frontend components.

## Key Benefits

- **Eliminates Magic Numbers**: All hardcoded values are extracted into configuration files
- **Type Safety**: Uses Pydantic (backend) and TypeScript interfaces (frontend) for validation
- **Environment Flexibility**: Supports different configurations for development, testing, and production
- **Hot Reload**: Configuration changes can be applied without restarting the application
- **Centralized Management**: Single source of truth for all configuration values
- **Documentation**: All configuration options are self-documenting with descriptions

## Backend Configuration System

### File Structure
```
backend/
├── app/
│   ├── config/
│   │   ├── sensor_config.py        # Sensor simulation configuration
│   │   └── sensor_config.json      # Generated configuration file
│   └── core/
│       └── config.py              # Core application configuration
```

### Sensor Configuration (`sensor_config.py`)

#### Main Configuration Classes

1. **TemperatureConfig**
   - Global temperature ranges (-30°C to 50°C)
   - Comfort zones (20-24°C optimal, 18-26°C acceptable)
   - Alert thresholds (critical: <10°C or >35°C, warning: <16°C or >28°C)
   - Seasonal and daily variation factors
   - Room-specific configurations

2. **HumidityConfig**
   - Global humidity ranges (20-95%)
   - Comfort zones (40-60% optimal, 35-65% acceptable)
   - Alert thresholds (critical: <25% or >80%, warning: <30% or >70%)
   - Room-specific moisture characteristics

3. **EnergyConfig**
   - Power consumption limits (10kW max, 5kW high alert, 8kW critical)
   - Energy pricing (peak: $0.28/kWh, off-peak: $0.12/kWh, standard: $0.18/kWh)
   - Peak hours configuration
   - Device-specific power ratings and usage patterns

4. **SimulationConfig**
   - Data generation intervals (temperature: 30s, humidity: 30s, energy: 60s)
   - Batch processing settings
   - Health check intervals
   - Data retention policies

### Usage Examples

```python
from app.config.sensor_config import get_temperature_config, get_energy_config

# Get temperature configuration
temp_config = get_temperature_config()
min_temp = temp_config.global_min_temp  # -30.0
max_temp = temp_config.global_max_temp  # 50.0

# Get room-specific configuration
room_config = temp_config.room_configs["living_room"]
base_temp = room_config["base_temp"]  # 22.0

# Get energy pricing
energy_config = get_energy_config()
peak_rate = energy_config.energy_rates["peak"]  # 0.28
```

### Configuration Management

The `ConfigManager` class provides:
- **Automatic Loading**: Loads configuration from JSON files or creates defaults
- **Validation**: Ensures all values are within acceptable ranges
- **Hot Reload**: Updates configuration without restart
- **Room-Specific Access**: Helper methods for room-based configuration

```python
from app.config.sensor_config import config_manager

# Update configuration
config_manager.update_config(
    temperature__global_min_temp=-25.0,
    energy__alert_high_power=4500.0
)

# Get room-specific device config
devices = config_manager.get_room_devices_config("kitchen")
```

## Frontend Configuration System

### File Structure
```
frontend/
├── src/
│   ├── app/
│   │   ├── config/
│   │   │   └── app-config.ts       # Frontend configuration
│   │   └── environments/
│   │       ├── environment.ts      # Development environment
│   │       └── environment.prod.ts # Production environment
```

### Frontend Configuration (`app-config.ts`)

#### Main Configuration Interfaces

1. **TemperatureGaugeConfig**
   - Temperature ranges and comfort zones
   - Visual configuration (gauge radius, needle length, center position)
   - Color schemes for different comfort levels
   - Animation settings

2. **HumidityConfig**
   - Humidity ranges and comfort zones
   - Alert thresholds
   - Color schemes for different humidity levels

3. **EnergyConfig**
   - Power thresholds and pricing
   - Chart configuration
   - Alert settings

4. **UIConfig**
   - Component sizes (small, medium, large)
   - Spacing and layout values
   - Animation timings
   - Responsive breakpoints
   - Theme colors

### Usage Examples

```typescript
import { getTemperatureConfig, getUIConfig } from './config/app-config';

// Get temperature configuration
const tempConfig = getTemperatureConfig();
const minTemp = tempConfig.minTemp;  // -20
const maxTemp = tempConfig.maxTemp;  // 50

// Get UI configuration
const uiConfig = getUIConfig();
const mediumSize = uiConfig.componentSizes.medium;  // {width: 200, height: 120, fontSize: 36}
```

### Configuration Service

The `ConfigService` provides:
- **Environment Loading**: Loads from localStorage and environment variables
- **Runtime Updates**: Updates configuration during runtime
- **Type Safety**: Full TypeScript interface support
- **Feature Flags**: Enable/disable features based on configuration

```typescript
import { appConfig } from './config/app-config';

// Check if feature is enabled
if (appConfig.isFeatureEnabled('enableRealtimeUpdates')) {
  // Initialize real-time updates
}

// Update configuration
appConfig.updateConfig({
  sensors: {
    temperature: {
      minTemp: -25,
      maxTemp: 45
    }
  }
});
```

## Configuration Categories

### 1. Sensor Simulation Parameters

**Before (Hardcoded):**
```python
# Hardcoded values scattered throughout code
temperature = max(-30.0, min(50.0, temperature))
if temp < 10:
    alert_level = "critical"
seasonal_factor = math.sin(day_of_year * 2 * math.pi / 365) * 8.0
```

**After (Configured):**
```python
# Centralized configuration
temp_config = get_temperature_config()
temperature = max(temp_config.global_min_temp, min(temp_config.global_max_temp, temperature))
if temp < temp_config.alert_critical_min:
    alert_level = "critical"
seasonal_factor = math.sin(day_of_year * 2 * math.pi / 365) * temp_config.seasonal_variation
```

### 2. Alert Thresholds

**Temperature Alerts:**
- Critical: < 10°C or > 35°C
- Warning: < 16°C or > 28°C

**Humidity Alerts:**
- Critical: < 25% or > 80%
- Warning: < 30% or > 70%

**Energy Alerts:**
- High consumption: > 5000W
- Critical consumption: > 8000W

### 3. Device Configurations

All device power ratings and usage patterns are configured:

```python
DeviceConfig(
    base_power=1800,        # Dishwasher: 1800W
    standby_power=3,        # Standby: 3W
    usage_pattern=UsagePattern.MEAL_CLEANUP,
    efficiency_rating=0.85
)
```

### 4. UI Component Settings

**Component Sizes:**
```typescript
componentSizes: {
  small: {width: 120, height: 80, fontSize: 24},
  medium: {width: 200, height: 120, fontSize: 36},
  large: {width: 280, height: 160, fontSize: 48}
}
```

**Color Schemes:**
```typescript
colors: {
  cold: '#2196F3',
  cool: '#00BCD4',
  comfortable: '#4CAF50',
  warm: '#FF9800',
  hot: '#F44336'
}
```

## Environment Variables

### Backend Environment Variables

```bash
# Core application
SECRET_KEY=your_secret_key_here
DEBUG=true
HOST=0.0.0.0
PORT=8001

# Database
INFLUXDB_URL=http://localhost:8087
INFLUXDB_TOKEN=your_token_here
INFLUXDB_ORG=smart-home
INFLUXDB_BUCKET=sensors

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_password

# Sensor intervals (seconds)
TEMPERATURE_SENSOR_INTERVAL=30
HUMIDITY_SENSOR_INTERVAL=30
ENERGY_SENSOR_INTERVAL=60

# Alert thresholds
TEMPERATURE_ALERT_MIN=10.0
TEMPERATURE_ALERT_MAX=35.0
HUMIDITY_ALERT_MIN=30.0
HUMIDITY_ALERT_MAX=70.0
ENERGY_ALERT_THRESHOLD=5000.0
```

### Frontend Environment Variables

```bash
# API configuration
API_BASE_URL=http://localhost:8001
WEBSOCKET_URL=ws://localhost:8001/ws

# Feature flags
ENABLE_REALTIME_UPDATES=true
ENABLE_NOTIFICATIONS=true
ENABLE_DARK_MODE=true
ENABLE_ADVANCED_CHARTS=true
```

## Configuration Files

### Backend Configuration File (`sensor_config.json`)

```json
{
  "temperature": {
    "global_min_temp": -30.0,
    "global_max_temp": 50.0,
    "comfort_optimal_min": 20.0,
    "comfort_optimal_max": 24.0,
    "seasonal_variation": 8.0,
    "room_configs": {
      "living_room": {
        "base_temp": 22.0,
        "temp_range": 3.0,
        "heating_efficiency": 0.8
      }
    }
  },
  "energy": {
    "energy_rates": {
      "peak": 0.28,
      "off_peak": 0.12,
      "standard": 0.18
    },
    "alert_high_power": 5000.0
  }
}
```

### Frontend Configuration (localStorage)

```json
{
  "sensors": {
    "temperature": {
      "minTemp": -20,
      "maxTemp": 50,
      "colors": {
        "cold": "#2196F3",
        "comfortable": "#4CAF50",
        "hot": "#F44336"
      }
    }
  },
  "ui": {
    "theme": {
      "primary": "#1976D2",
      "success": "#4CAF50",
      "warning": "#FF9800",
      "error": "#F44336"
    }
  }
}
```

## Migration Guide

### Identifying Magic Numbers

1. **Search for hardcoded values:**
```bash
grep -r "temperature.*[0-9]" backend/app/
grep -r "humidity.*[0-9]" backend/app/
grep -r "power.*[0-9]" backend/app/
```

2. **Common patterns to look for:**
   - Numeric comparisons: `if temp > 25:`
   - Range checks: `max(10, min(50, value))`
   - Sleep intervals: `await asyncio.sleep(30)`
   - Color codes: `color = '#FF0000'`
   - Size values: `width: 200px`

### Refactoring Steps

1. **Extract to configuration:**
```python
# Before
if temperature > 35:
    alert = "critical"

# After
temp_config = get_temperature_config()
if temperature > temp_config.alert_critical_max:
    alert = "critical"
```

2. **Update component initialization:**
```typescript
// Before
minTemp = -20;
maxTemp = 50;

// After
constructor() {
  const config = getTemperatureConfig();
  this.minTemp = config.minTemp;
  this.maxTemp = config.maxTemp;
}
```

## Best Practices

### 1. Configuration Naming

- Use descriptive names: `alert_critical_min` instead of `min_alert`
- Include units in descriptions: `"Temperature in Celsius"`
- Group related settings: `comfort_optimal_min`, `comfort_optimal_max`

### 2. Default Values

- Provide sensible defaults for all configuration options
- Use industry standards where applicable
- Document the reasoning behind default values

### 3. Validation

- Validate ranges: `min_temp < max_temp`
- Check for required fields
- Provide helpful error messages

### 4. Documentation

- Include descriptions for all configuration options
- Provide examples of valid values
- Document dependencies between settings

## Testing Configuration

### Backend Tests

```python
def test_temperature_config():
    config = get_temperature_config()
    assert config.global_min_temp < config.global_max_temp
    assert config.comfort_optimal_min < config.comfort_optimal_max
    assert config.alert_critical_min < config.alert_warning_min

def test_room_config():
    config = get_temperature_config()
    assert "living_room" in config.room_configs
    room_config = config.room_configs["living_room"]
    assert room_config["base_temp"] > 0
```

### Frontend Tests

```typescript
describe('Temperature Configuration', () => {
  it('should have valid temperature ranges', () => {
    const config = getTemperatureConfig();
    expect(config.minTemp).toBeLessThan(config.maxTemp);
    expect(config.comfortOptimalMin).toBeLessThan(config.comfortOptimalMax);
  });
});
```

## Troubleshooting

### Common Issues

1. **Configuration not loading:**
   - Check file permissions
   - Verify JSON syntax
   - Ensure environment variables are set

2. **Validation errors:**
   - Check value ranges
   - Verify required fields
   - Review type compatibility

3. **Performance issues:**
   - Cache configuration objects
   - Avoid repeated file reads
   - Use singleton pattern for managers

### Debug Tools

```python
# Backend debugging
from app.config.sensor_config import config_manager
config_manager.validate_config()  # Check configuration validity

# Frontend debugging
import { appConfig } from './config/app-config';
console.log(appConfig.getConfig());  // View current configuration
```

## Future Enhancements

### Planned Features

1. **Configuration UI**: Web interface for updating configuration
2. **A/B Testing**: Support for configuration experiments
3. **Remote Configuration**: Load configuration from remote servers
4. **Configuration History**: Track changes over time
5. **Backup/Restore**: Export and import configuration sets

### Migration Path

1. **Phase 1**: ✅ Extract hardcoded values to configuration files
2. **Phase 2**: Add validation and error handling
3. **Phase 3**: Implement hot reload and runtime updates
4. **Phase 4**: Add configuration UI and management tools

## Conclusion

The configuration management system successfully eliminates magic numbers and hardcoded values throughout the Smart Home IoT project. This provides:

- **Better Maintainability**: Changes can be made in one place
- **Environment Flexibility**: Different settings for dev/test/prod
- **Type Safety**: Compile-time validation of configuration
- **Documentation**: Self-documenting configuration options
- **Scalability**: Easy to add new configuration options

All sensor simulation parameters, alert thresholds, device configurations, and UI constants are now centrally managed and easily configurable without code changes. 