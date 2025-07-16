"""
Main sensor simulator that coordinates all sensor workers.
Provides centralized control and monitoring for all sensor types.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.workers.temperature import temperature_worker
from app.workers.humidity import humidity_worker
from app.workers.energy import energy_worker
from app.core.websocket import websocket_manager
from app.config.sensor_config import get_sensor_config

logger = logging.getLogger(__name__)

class SensorSimulator:
    """Main sensor simulator that coordinates all sensor workers."""
    
    def __init__(self):
        self.is_running = False
        self.workers = {
            "temperature": temperature_worker,
            "humidity": humidity_worker,
            "energy": energy_worker,
        }
        self.start_time = None
        self.status = "stopped"
        
        # Load configuration
        self.config = get_sensor_config()
        
        # System statistics
        self.stats = {
            "total_readings": 0,
            "readings_per_sensor": {
                "temperature": 0,
                "humidity": 0,
                "energy": 0,
            },
            "errors": 0,
            "uptime": 0,
            "last_reading": None,
        }
    
    async def start_all_workers(self):
        """Start all sensor workers."""
        logger.info("Starting all sensor workers...")
        self.is_running = True
        self.start_time = datetime.now()
        self.status = "running"
        
        try:
            # Start all workers concurrently
            await asyncio.gather(
                self.workers["temperature"].start(),
                self.workers["humidity"].start(),
                self.workers["energy"].start(),
            )
            
            logger.info("All sensor workers started successfully")
            
            # Broadcast system status
            await self.broadcast_system_status()
            
        except Exception as e:
            logger.error(f"Error starting sensor workers: {e}")
            self.status = "error"
            await self.broadcast_system_status()
    
    async def stop_all_workers(self):
        """Stop all sensor workers."""
        logger.info("Stopping all sensor workers...")
        self.is_running = False
        self.status = "stopped"
        
        try:
            # Stop all workers concurrently
            await asyncio.gather(
                self.workers["temperature"].stop(),
                self.workers["humidity"].stop(),
                self.workers["energy"].stop(),
            )
            
            logger.info("All sensor workers stopped successfully")
            
            # Broadcast system status
            await self.broadcast_system_status()
            
        except Exception as e:
            logger.error(f"Error stopping sensor workers: {e}")
            self.status = "error"
            await self.broadcast_system_status()
    
    async def restart_worker(self, worker_name: str) -> bool:
        """Restart a specific worker."""
        if worker_name not in self.workers:
            logger.error(f"Unknown worker: {worker_name}")
            return False
        
        try:
            logger.info(f"Restarting {worker_name} worker...")
            worker = self.workers[worker_name]
            
            # Stop the worker
            await worker.stop()
            await asyncio.sleep(1)  # Brief pause
            
            # Start the worker
            await worker.start()
            
            logger.info(f"{worker_name} worker restarted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restarting {worker_name} worker: {e}")
            return False
    
    async def get_system_status(self) -> Dict:
        """Get current system status."""
        uptime = 0
        if self.start_time:
            uptime = int((datetime.now() - self.start_time).total_seconds())
        
        worker_status = {}
        for name, worker in self.workers.items():
            worker_status[name] = {
                "running": worker.is_running,
                "last_reading": getattr(worker, "last_reading", None),
            }
        
        return {
            "system_status": self.status,
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "workers": worker_status,
            "statistics": self.stats,
            "timestamp": datetime.now().isoformat(),
        }
    
    async def get_all_latest_readings(self) -> Dict:
        """Get latest readings from all sensors."""
        readings = {}
        
        try:
            # Get temperature readings
            temp_readings = {}
            for room_id in temperature_worker.room_configs.keys():
                sensor_id = f"temp_{room_id}_001"
                reading = await temperature_worker.generate_temperature_reading(room_id, sensor_id)
                temp_readings[room_id] = reading
            readings["temperature"] = temp_readings
            
            # Get humidity readings
            humidity_readings = {}
            for room_id in humidity_worker.room_configs.keys():
                sensor_id = f"humid_{room_id}_001"
                reading = await humidity_worker.generate_humidity_reading(room_id, sensor_id)
                humidity_readings[room_id] = reading
            readings["humidity"] = humidity_readings
            
            # Get energy readings
            energy_readings = {}
            for room_id in energy_worker.device_configs.keys():
                reading = await energy_worker.generate_energy_reading(room_id)
                energy_readings[room_id] = reading
            readings["energy"] = energy_readings
            
            # Get total energy consumption
            readings["energy_total"] = await energy_worker.get_total_consumption()
            
        except Exception as e:
            logger.error(f"Error getting latest readings: {e}")
        
        return readings
    
    async def get_room_summary(self, room_id: str) -> Dict:
        """Get comprehensive summary for a specific room."""
        try:
            # Temperature data
            temp_sensor_id = f"temp_{room_id}_001"
            temp_reading = await temperature_worker.generate_temperature_reading(room_id, temp_sensor_id)
            
            # Humidity data
            humidity_sensor_id = f"humid_{room_id}_001"
            humidity_reading = await humidity_worker.generate_humidity_reading(room_id, humidity_sensor_id)
            
            # Energy data
            energy_reading = await energy_worker.generate_energy_reading(room_id)
            
            # Comfort analysis
            comfort_score = self.calculate_comfort_score(temp_reading, humidity_reading)
            
            return {
                "room_id": room_id,
                "timestamp": datetime.now().isoformat(),
                "temperature": temp_reading,
                "humidity": humidity_reading,
                "energy": energy_reading,
                "comfort_score": comfort_score,
                "alerts": self.check_room_alerts(temp_reading, humidity_reading, energy_reading),
            }
            
        except Exception as e:
            logger.error(f"Error getting room summary for {room_id}: {e}")
            return {"error": str(e)}
    
    def calculate_comfort_score(self, temp_reading: Dict, humidity_reading: Dict) -> Dict:
        """Calculate comfort score based on temperature and humidity."""
        temp = temp_reading["temperature"]
        humidity = humidity_reading["humidity"]
        
        temp_config = self.config.temperature
        humidity_config = self.config.humidity
        
        # Temperature comfort scoring using config
        if temp_config.comfort_optimal_min <= temp <= temp_config.comfort_optimal_max:
            temp_score = 100
        elif temp_config.comfort_acceptable_min <= temp <= temp_config.comfort_acceptable_max:
            temp_score = 80
        elif temp_config.alert_warning_min <= temp <= temp_config.alert_warning_max:
            temp_score = 60
        else:
            temp_score = 40
        
        # Humidity comfort scoring using config
        if humidity_config.comfort_optimal_min <= humidity <= humidity_config.comfort_optimal_max:
            humidity_score = 100
        elif humidity_config.comfort_acceptable_min <= humidity <= humidity_config.comfort_acceptable_max:
            humidity_score = 80
        elif humidity_config.alert_warning_min <= humidity <= humidity_config.alert_warning_max:
            humidity_score = 60
        else:
            humidity_score = 40
        
        # Overall comfort score (weighted average)
        overall_score = (temp_score * 0.6) + (humidity_score * 0.4)
        
        # Determine comfort level
        if overall_score >= 90:
            comfort_level = "excellent"
        elif overall_score >= 80:
            comfort_level = "good"
        elif overall_score >= 60:
            comfort_level = "acceptable"
        else:
            comfort_level = "poor"
        
        return {
            "overall_score": round(overall_score, 1),
            "comfort_level": comfort_level,
            "temperature_score": temp_score,
            "humidity_score": humidity_score,
            "recommendations": self.get_comfort_recommendations(temp, humidity),
        }
    
    def get_comfort_recommendations(self, temp: float, humidity: float) -> List[str]:
        """Get recommendations for improving comfort."""
        recommendations = []
        
        if temp < 18:
            recommendations.append("Consider increasing heating")
        elif temp > 26:
            recommendations.append("Consider increasing cooling")
        
        if humidity < 35:
            recommendations.append("Consider using a humidifier")
        elif humidity > 65:
            recommendations.append("Consider using a dehumidifier or improving ventilation")
        
        if temp > 24 and humidity > 60:
            recommendations.append("High temperature and humidity - consider air conditioning")
        
        if not recommendations:
            recommendations.append("Comfort conditions are optimal")
        
        return recommendations
    
    def check_room_alerts(self, temp_reading: Dict, humidity_reading: Dict, energy_reading: Dict) -> List[Dict]:
        """Check for alerts in room conditions."""
        alerts = []
        
        temp = temp_reading["temperature"]
        humidity = humidity_reading["humidity"]
        power = energy_reading["current_power"]
        
        temp_config = self.config.temperature
        humidity_config = self.config.humidity
        energy_config = self.config.energy
        
        # Temperature alerts using config
        if temp < temp_config.alert_critical_min:
            alerts.append({
                "type": "temperature",
                "severity": "critical",
                "message": f"Very low temperature: {temp}°C",
                "recommendation": "Check heating system immediately"
            })
        elif temp > temp_config.alert_critical_max:
            alerts.append({
                "type": "temperature",
                "severity": "critical",
                "message": f"Very high temperature: {temp}°C",
                "recommendation": "Check cooling system immediately"
            })
        elif temp < temp_config.alert_warning_min or temp > temp_config.alert_warning_max:
            alerts.append({
                "type": "temperature",
                "severity": "warning",
                "message": f"Temperature outside comfort range: {temp}°C",
                "recommendation": "Adjust thermostat"
            })
        
        # Humidity alerts using config
        if humidity < humidity_config.alert_critical_min:
            alerts.append({
                "type": "humidity",
                "severity": "warning",
                "message": f"Very low humidity: {humidity}%",
                "recommendation": "Consider using a humidifier"
            })
        elif humidity > humidity_config.alert_critical_max:
            alerts.append({
                "type": "humidity",
                "severity": "critical",
                "message": f"Very high humidity: {humidity}%",
                "recommendation": "Check for leaks and improve ventilation"
            })
        elif humidity > humidity_config.alert_warning_max:
            alerts.append({
                "type": "humidity",
                "severity": "warning",
                "message": f"High humidity: {humidity}%",
                "recommendation": "Consider dehumidifier or better ventilation"
            })
        
        # Energy alerts using config
        if power > energy_config.alert_high_power:
            alerts.append({
                "type": "energy",
                "severity": "warning",
                "message": f"High power consumption: {power}W",
                "recommendation": "Check for energy-intensive devices"
            })
        
        return alerts
    
    async def broadcast_system_status(self):
        """Broadcast system status to all WebSocket clients."""
        try:
            status = await self.get_system_status()
            message = {
                "type": "system_status",
                "data": status
            }
            await websocket_manager.broadcast_message(message)
            logger.debug("System status broadcast")
            
        except Exception as e:
            logger.error(f"Error broadcasting system status: {e}")
    
    async def broadcast_room_summary(self, room_id: str):
        """Broadcast room summary to WebSocket clients."""
        try:
            summary = await self.get_room_summary(room_id)
            message = {
                "type": "room_summary",
                "data": summary
            }
            await websocket_manager.broadcast_message(message)
            logger.debug(f"Room summary broadcast for {room_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting room summary: {e}")
    
    async def run_monitoring_loop(self):
        """Run monitoring loop for system health and alerts."""
        logger.info("Starting sensor monitoring loop...")
        
        while self.is_running:
            try:
                # Update statistics
                self.stats["total_readings"] += 1
                self.stats["last_reading"] = datetime.now().isoformat()
                
                # Broadcast system status periodically (every 5 minutes)
                if self.stats["total_readings"] % 10 == 0:  # Every 10 cycles (5 minutes)
                    await self.broadcast_system_status()
                
                # Check for system alerts
                await self.check_system_alerts()
                
                # Wait for next cycle
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(5)
    
    async def check_system_alerts(self):
        """Check for system-wide alerts."""
        try:
            # Check if any workers have stopped unexpectedly
            for name, worker in self.workers.items():
                if self.is_running and not worker.is_running:
                    logger.warning(f"{name} worker has stopped unexpectedly")
                    alert = {
                        "type": "system_alert",
                        "data": {
                            "severity": "critical",
                            "message": f"{name} sensor worker has stopped",
                            "recommendation": "Restart the sensor worker",
                            "timestamp": datetime.now().isoformat(),
                        }
                    }
                    await websocket_manager.broadcast_message(alert)
        
        except Exception as e:
            logger.error(f"Error checking system alerts: {e}")
    
    async def start(self):
        """Start the sensor simulator."""
        if not self.is_running:
            await self.start_all_workers()
            # Start monitoring loop
            asyncio.create_task(self.run_monitoring_loop())
    
    async def stop(self):
        """Stop the sensor simulator."""
        if self.is_running:
            await self.stop_all_workers()

# Global instance
sensor_simulator = SensorSimulator() 