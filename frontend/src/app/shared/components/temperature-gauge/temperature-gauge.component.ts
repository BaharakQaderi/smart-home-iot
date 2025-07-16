import { Component, Input, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { getTemperatureConfig, TemperatureGaugeConfig } from '../../../config/app-config';

interface TemperatureReading {
  sensor_id: string;
  room_id: string;
  temperature: number;
  unit: string;
  timestamp: string;
  sensor_type: string;
  heating_active: boolean;
  cooling_active: boolean;
  outdoor_temp: number;
}

@Component({
  selector: 'app-temperature-gauge',
  templateUrl: './temperature-gauge.component.html',
  styleUrls: ['./temperature-gauge.component.scss']
})
export class TemperatureGaugeComponent implements OnInit, OnDestroy {
  @Input() reading: TemperatureReading | null = null;
  @Input() showDetails: boolean = true;
  @Input() size: 'small' | 'medium' | 'large' = 'medium';
  @Input() showTrend: boolean = true;

  // Component state
  displayTemperature: number = 0;
  animatedTemperature: number = 0;
  previousTemperature: number = 0;
  temperatureTrend: 'up' | 'down' | 'stable' = 'stable';
  comfortLevel: 'cold' | 'cool' | 'comfortable' | 'warm' | 'hot' = 'comfortable';
  alertLevel: 'none' | 'warning' | 'critical' = 'none';
  
  // Animation and styling
  gaugeRotation: number = 0;
  gaugeColor: string = '#4CAF50';
  backgroundColor: string = '#f5f5f5';
  
  // Configuration
  config: TemperatureGaugeConfig;
  minTemp: number;
  maxTemp: number;
  optimalMin: number;
  optimalMax: number;
  
  // Lifecycle
  private destroy$ = new Subject<void>();

  constructor(private cdr: ChangeDetectorRef) {
    this.config = getTemperatureConfig();
    this.minTemp = this.config.minTemp;
    this.maxTemp = this.config.maxTemp;
    this.optimalMin = this.config.comfortOptimalMin;
    this.optimalMax = this.config.comfortOptimalMax;
  }

  ngOnInit(): void {
    this.updateDisplay();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ngOnChanges(): void {
    this.updateDisplay();
  }

  private updateDisplay(): void {
    if (!this.reading) return;

    // Update previous temperature for trend calculation
    this.previousTemperature = this.displayTemperature;
    this.displayTemperature = this.reading.temperature;
    
    // Calculate trend
    this.calculateTrend();
    
    // Update comfort level
    this.updateComfortLevel();
    
    // Update alert level
    this.updateAlertLevel();
    
    // Update gauge visuals
    this.updateGaugeVisuals();
    
    // Animate temperature change
    this.animateTemperature();
    
    // Trigger change detection
    this.cdr.detectChanges();
  }

  private calculateTrend(): void {
    const diff = this.displayTemperature - this.previousTemperature;
    const threshold = 0.5; // 0.5°C threshold for trend detection
    
    if (Math.abs(diff) < threshold) {
      this.temperatureTrend = 'stable';
    } else if (diff > 0) {
      this.temperatureTrend = 'up';
    } else {
      this.temperatureTrend = 'down';
    }
  }

  private updateComfortLevel(): void {
    const temp = this.displayTemperature;
    
    if (temp < this.config.alertCriticalMin) {
      this.comfortLevel = 'cold';
    } else if (temp < this.config.comfortOptimalMin) {
      this.comfortLevel = 'cool';
    } else if (temp <= this.config.comfortOptimalMax) {
      this.comfortLevel = 'comfortable';
    } else if (temp <= this.config.alertWarningMax) {
      this.comfortLevel = 'warm';
    } else {
      this.comfortLevel = 'hot';
    }
  }

  private updateAlertLevel(): void {
    const temp = this.displayTemperature;
    
    if (temp < this.config.alertCriticalMin || temp > this.config.alertCriticalMax) {
      this.alertLevel = 'critical';
    } else if (temp < this.config.alertWarningMin || temp > this.config.alertWarningMax) {
      this.alertLevel = 'warning';
    } else {
      this.alertLevel = 'none';
    }
  }

  private updateGaugeVisuals(): void {
    const temp = this.displayTemperature;
    
    // Calculate gauge rotation (0-180 degrees)
    const normalizedTemp = (temp - this.minTemp) / (this.maxTemp - this.minTemp);
    this.gaugeRotation = Math.max(0, Math.min(180, normalizedTemp * 180));
    
    // Update gauge color based on comfort level using config
    switch (this.comfortLevel) {
      case 'cold':
        this.gaugeColor = this.config.colors.cold;
        this.backgroundColor = this.config.colors.background.cold;
        break;
      case 'cool':
        this.gaugeColor = this.config.colors.cool;
        this.backgroundColor = this.config.colors.background.cool;
        break;
      case 'comfortable':
        this.gaugeColor = this.config.colors.comfortable;
        this.backgroundColor = this.config.colors.background.comfortable;
        break;
      case 'warm':
        this.gaugeColor = this.config.colors.warm;
        this.backgroundColor = this.config.colors.background.warm;
        break;
      case 'hot':
        this.gaugeColor = this.config.colors.hot;
        this.backgroundColor = this.config.colors.background.hot;
        break;
    }
  }

  private animateTemperature(): void {
    const duration = 1000; // 1 second animation
    const startTime = performance.now();
    const startTemp = this.animatedTemperature;
    const endTemp = this.displayTemperature;
    
    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      
      this.animatedTemperature = startTemp + (endTemp - startTemp) * easeProgress;
      
      if (progress < 1) {
        requestAnimationFrame(animate);
        this.cdr.detectChanges();
      }
    };
    
    requestAnimationFrame(animate);
  }

  // Getter methods for template
  get temperatureDisplay(): string {
    return this.animatedTemperature.toFixed(1);
  }

  get roomName(): string {
    if (!this.reading) return '';
    return this.reading.room_id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  get lastUpdateTime(): string {
    if (!this.reading) return '';
    const date = new Date(this.reading.timestamp);
    return date.toLocaleTimeString();
  }

  get trendIcon(): string {
    switch (this.temperatureTrend) {
      case 'up': return 'trending_up';
      case 'down': return 'trending_down';
      case 'stable': return 'trending_flat';
      default: return 'trending_flat';
    }
  }

  get trendColor(): string {
    switch (this.temperatureTrend) {
      case 'up': return '#f44336';
      case 'down': return '#2196f3';
      case 'stable': return '#757575';
      default: return '#757575';
    }
  }

  get comfortLevelText(): string {
    switch (this.comfortLevel) {
      case 'cold': return 'Very Cold';
      case 'cool': return 'Cool';
      case 'comfortable': return 'Comfortable';
      case 'warm': return 'Warm';
      case 'hot': return 'Very Hot';
      default: return 'Unknown';
    }
  }

  get alertMessage(): string {
    switch (this.alertLevel) {
      case 'critical': return 'Critical temperature detected!';
      case 'warning': return 'Temperature outside comfort range';
      case 'none': return '';
      default: return '';
    }
  }

  get systemStatus(): string {
    if (!this.reading) return 'No data';
    
    const statuses = [];
    if (this.reading.heating_active) statuses.push('Heating');
    if (this.reading.cooling_active) statuses.push('Cooling');
    
    return statuses.length > 0 ? statuses.join(', ') : 'Idle';
  }

  get gaugeStyles(): any {
    return {
      'transform': `rotate(${this.gaugeRotation}deg)`,
      'background': `conic-gradient(from 0deg, ${this.gaugeColor} 0deg, ${this.gaugeColor} ${this.gaugeRotation}deg, #e0e0e0 ${this.gaugeRotation}deg, #e0e0e0 180deg)`
    };
  }

  get containerClasses(): string[] {
    const classes = ['temperature-gauge', `size-${this.size}`];
    
    if (this.alertLevel !== 'none') {
      classes.push(`alert-${this.alertLevel}`);
    }
    
    classes.push(`comfort-${this.comfortLevel}`);
    
    return classes;
  }

  getTemperatureArcPath(): string {
    const centerX = this.config.centerX;
    const centerY = this.config.centerY;
    const radius = this.config.gaugeRadius;
    const startAngle = 180; // degrees
    const endAngle = 180 - this.gaugeRotation; // degrees
    
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;
    
    const x1 = centerX + radius * Math.cos(startAngleRad);
    const y1 = centerY + radius * Math.sin(startAngleRad);
    const x2 = centerX + radius * Math.cos(endAngleRad);
    const y2 = centerY + radius * Math.sin(endAngleRad);
    
    const largeArcFlag = this.gaugeRotation > 90 ? 1 : 0;
    
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 0 ${x2} ${y2}`;
  }

  getNeedleStart(): {x: number, y: number} {
    return {x: this.config.centerX, y: this.config.centerY};
  }

  getNeedleEnd(): {x: number, y: number} {
    const centerX = this.config.centerX;
    const centerY = this.config.centerY;
    const length = this.config.needleLength;
    const angle = (180 - this.gaugeRotation) * Math.PI / 180;
    
    return {
      x: centerX + length * Math.cos(angle),
      y: centerY + length * Math.sin(angle)
    };
  }

  getNeedleAnimation(): string {
    const prevAngle = 180 - (this.previousTemperature - this.minTemp) / (this.maxTemp - this.minTemp) * 180;
    const currentAngle = 180 - this.gaugeRotation;
    
    return `${prevAngle} 100 100;${currentAngle} 100 100`;
  }

  getSystemStatusClass(): string {
    if (this.reading?.heating_active) return 'status-heating';
    if (this.reading?.cooling_active) return 'status-cooling';
    return 'status-idle';
  }
} 