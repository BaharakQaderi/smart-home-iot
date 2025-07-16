"""
Smart Home IoT Backend - Configuration Settings
=============================================

This module contains all configuration settings for the Smart Home IoT backend.
It uses Pydantic Settings to validate and manage environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # ===================
    # Application Settings
    # ===================
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    APP_NAME: str = Field(default="Smart Home IoT", description="Application name")
    HOST: str = Field(default="0.0.0.0", description="Host to bind to")
    PORT: int = Field(default=8000, description="Port to bind to")
    
    # ===================
    # Security Settings
    # ===================
    SECRET_KEY: str = Field(description="Secret key for JWT tokens")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration time")
    
    # ===================
    # Database Configuration
    # ===================
    # InfluxDB Settings
    INFLUXDB_URL: str = Field(default="http://localhost:8086", description="InfluxDB URL")
    INFLUXDB_TOKEN: str = Field(description="InfluxDB token")
    INFLUXDB_ORG: str = Field(default="smart-home", description="InfluxDB organization")
    INFLUXDB_BUCKET: str = Field(default="sensors", description="InfluxDB bucket")
    INFLUXDB_USERNAME: str = Field(default="admin", description="InfluxDB username")
    INFLUXDB_PASSWORD: str = Field(description="InfluxDB password")
    
    # ===================
    # Redis Configuration
    # ===================
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    
    # ===================
    # Frontend Settings
    # ===================
    FRONTEND_URL: str = Field(default="http://localhost:4200", description="Frontend URL")
    
    # ===================
    # WebSocket Configuration
    # ===================
    WEBSOCKET_URL: str = Field(default="ws://localhost:8000/ws", description="WebSocket URL")
    
    # ===================
    # Sensor Settings
    # ===================
    # Sensor data simulation intervals (in seconds)
    TEMPERATURE_SENSOR_INTERVAL: int = Field(default=30, description="Temperature sensor interval")
    HUMIDITY_SENSOR_INTERVAL: int = Field(default=30, description="Humidity sensor interval")
    ENERGY_SENSOR_INTERVAL: int = Field(default=60, description="Energy sensor interval")
    SECURITY_SENSOR_INTERVAL: int = Field(default=5, description="Security sensor interval")
    AIR_QUALITY_SENSOR_INTERVAL: int = Field(default=60, description="Air quality sensor interval")
    
    # Default sensor ranges
    TEMPERATURE_MIN: float = Field(default=-20.0, description="Minimum temperature")
    TEMPERATURE_MAX: float = Field(default=50.0, description="Maximum temperature")
    HUMIDITY_MIN: float = Field(default=0.0, description="Minimum humidity")
    HUMIDITY_MAX: float = Field(default=100.0, description="Maximum humidity")
    ENERGY_MAX_WATTS: float = Field(default=5000.0, description="Maximum energy consumption")
    
    # ===================
    # Logging Configuration
    # ===================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE_PATH: str = Field(default="./data/logs/smart-home.log", description="Log file path")
    LOG_MAX_SIZE: str = Field(default="10MB", description="Maximum log file size")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Number of backup log files")
    
    # ===================
    # Monitoring Settings
    # ===================
    # Grafana
    GRAFANA_URL: str = Field(default="http://localhost:3000", description="Grafana URL")
    GRAFANA_USERNAME: str = Field(default="admin", description="Grafana username")
    GRAFANA_PASSWORD: str = Field(default="admin123", description="Grafana password")
    
    # ===================
    # Email Notifications (Optional)
    # ===================
    EMAIL_ENABLED: bool = Field(default=False, description="Enable email notifications")
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    FROM_EMAIL: Optional[str] = Field(default=None, description="From email address")
    
    # ===================
    # Alert Settings
    # ===================
    ENABLE_TEMPERATURE_ALERTS: bool = Field(default=True, description="Enable temperature alerts")
    TEMPERATURE_ALERT_MIN: float = Field(default=10.0, description="Minimum temperature for alerts")
    TEMPERATURE_ALERT_MAX: float = Field(default=35.0, description="Maximum temperature for alerts")
    
    ENABLE_HUMIDITY_ALERTS: bool = Field(default=True, description="Enable humidity alerts")
    HUMIDITY_ALERT_MIN: float = Field(default=30.0, description="Minimum humidity for alerts")
    HUMIDITY_ALERT_MAX: float = Field(default=70.0, description="Maximum humidity for alerts")
    
    ENABLE_ENERGY_ALERTS: bool = Field(default=True, description="Enable energy alerts")
    ENERGY_ALERT_THRESHOLD: float = Field(default=4000.0, description="Energy consumption threshold")
    
    ENABLE_SECURITY_ALERTS: bool = Field(default=True, description="Enable security alerts")
    
    # ===================
    # Backup Settings
    # ===================
    BACKUP_ENABLED: bool = Field(default=True, description="Enable backups")
    BACKUP_INTERVAL_HOURS: int = Field(default=24, description="Backup interval in hours")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention in days")
    BACKUP_PATH: str = Field(default="./data/backups", description="Backup path")
    
    # ===================
    # Development Settings
    # ===================
    # Set to true for development mode
    DEV_MODE: bool = Field(default=True, description="Development mode")
    MOCK_SENSORS: bool = Field(default=True, description="Use mock sensor data")
    ENABLE_CORS: bool = Field(default=True, description="Enable CORS")
    
    # ===================
    # Production Settings
    # ===================
    # SSL Settings (for production)
    SSL_ENABLED: bool = Field(default=False, description="Enable SSL")
    SSL_CERT_PATH: str = Field(default="./infrastructure/docker/nginx/ssl/cert.pem", description="SSL certificate path")
    SSL_KEY_PATH: str = Field(default="./infrastructure/docker/nginx/ssl/key.pem", description="SSL key path")
    
    # Database connection pool settings
    DB_POOL_SIZE: int = Field(default=5, description="Database pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="Rate limit per minute")
    
    # ===================
    # External Services
    # ===================
    # Weather API (optional)
    WEATHER_API_ENABLED: bool = Field(default=False, description="Enable weather API")
    WEATHER_API_KEY: Optional[str] = Field(default=None, description="Weather API key")
    WEATHER_API_URL: str = Field(default="http://api.openweathermap.org/data/2.5/weather", description="Weather API URL")
    
    # ===================
    # Testing Settings
    # ===================
    TEST_DATABASE_URL: str = Field(default="sqlite:///./test.db", description="Test database URL")
    TEST_REDIS_URL: str = Field(default="redis://localhost:6379/1", description="Test Redis URL")
    
    # ===================
    # Computed Properties
    # ===================
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins as a list."""
        if self.ENABLE_CORS:
            return [
                self.FRONTEND_URL,
                "http://localhost:3000",
                "http://localhost:4200",
                "http://localhost:8080"
            ]
        return []
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Get allowed hosts as a list."""
        return [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "smart-home-backend",
            "smart-home-frontend"
        ]
    
    @property
    def DATABASE_URL(self) -> str:
        """Get the complete database URL."""
        return f"{self.INFLUXDB_URL}?org={self.INFLUXDB_ORG}&bucket={self.INFLUXDB_BUCKET}"
    
    @property
    def IS_PRODUCTION(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def LOG_DIR(self) -> Path:
        """Get the log directory path."""
        return Path(self.LOG_FILE_PATH).parent
    
    @property
    def BACKUP_DIR(self) -> Path:
        """Get the backup directory path."""
        return Path(self.BACKUP_PATH)
    
    # ===================
    # Validators
    # ===================
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validate that secret key is provided and sufficiently long."""
        if not v:
            raise ValueError('SECRET_KEY is required')
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('INFLUXDB_TOKEN')
    def validate_influxdb_token(cls, v):
        """Validate that InfluxDB token is provided."""
        if not v:
            raise ValueError('INFLUXDB_TOKEN is required')
        return v
    
    @validator('INFLUXDB_PASSWORD')
    def validate_influxdb_password(cls, v):
        """Validate that InfluxDB password is provided."""
        if not v:
            raise ValueError('INFLUXDB_PASSWORD is required')
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'LOG_LEVEL must be one of: {valid_levels}')
        return v.upper()
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        """Validate environment."""
        valid_environments = ['development', 'staging', 'production']
        if v.lower() not in valid_environments:
            raise ValueError(f'ENVIRONMENT must be one of: {valid_environments}')
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Create settings instance
settings = Settings()


# Create directories if they don't exist
def create_directories():
    """Create necessary directories."""
    directories = [
        settings.LOG_DIR,
        settings.BACKUP_DIR,
        Path("./data/logs"),
        Path("./data/backups"),
        Path("./data/influxdb"),
        Path("./data/grafana")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
create_directories() 