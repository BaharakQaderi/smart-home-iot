/**
 * Frontend Application Configuration
 * ==================================
 * 
 * This file contains all configuration constants for the Angular frontend,
 * eliminating magic numbers and providing centralized configuration management.
 */

export interface ApiEndpoints {
  auth: string;
  sensors: string;
  websocket: string;
  health: string;
  users: string;
  dashboard: string;
}

export interface TemperatureGaugeConfig {
  // Temperature ranges
  minTemp: number;
  maxTemp: number;
  
  // Comfort zones
  comfortOptimalMin: number;
  comfortOptimalMax: number;
  comfortAcceptableMin: number;
  comfortAcceptableMax: number;
  
  // Alert thresholds
  alertCriticalMin: number;
  alertCriticalMax: number;
  alertWarningMin: number;
  alertWarningMax: number;
  
  // Visual configuration
  gaugeRadius: number;
  needleLength: number;
  centerX: number;
  centerY: number;
  
  // Animation settings
  animationDuration: number;
  transitionEasing: string;
  
  // Color scheme
  colors: {
    cold: string;
    cool: string;
    comfortable: string;
    warm: string;
    hot: string;
    background: {
      cold: string;
      cool: string;
      comfortable: string;
      warm: string;
      hot: string;
    };
    alert: {
      warning: string;
      critical: string;
    };
  };
}

export interface HumidityConfig {
  // Humidity ranges
  minHumidity: number;
  maxHumidity: number;
  
  // Comfort zones
  comfortOptimalMin: number;
  comfortOptimalMax: number;
  comfortAcceptableMin: number;
  comfortAcceptableMax: number;
  
  // Alert thresholds
  alertCriticalMin: number;
  alertCriticalMax: number;
  alertWarningMin: number;
  alertWarningMax: number;
  
  // Comfort level thresholds
  veryDryThreshold: number;
  dryThreshold: number;
  comfortableMax: number;
  humidThreshold: number;
  
  // Colors
  colors: {
    veryDry: string;
    dry: string;
    comfortable: string;
    humid: string;
    veryHumid: string;
  };
}

export interface EnergyConfig {
  // Power thresholds
  maxPower: number;
  alertHighPower: number;
  alertCriticalPower: number;
  
  // Energy pricing
  energyRates: {
    peak: number;
    offPeak: number;
    standard: number;
  };
  
  // Peak hours
  peakHours: number[];
  offPeakHours: number[];
  
  // Chart configuration
  chartColors: {
    consumption: string;
    cost: string;
    savings: string;
  };
}

export interface UIConfig {
  // Component sizes
  componentSizes: {
    small: {
      width: number;
      height: number;
      fontSize: number;
    };
    medium: {
      width: number;
      height: number;
      fontSize: number;
    };
    large: {
      width: number;
      height: number;
      fontSize: number;
    };
  };
  
  // Spacing and layout
  spacing: {
    small: number;
    medium: number;
    large: number;
  };
  
  // Animation timings
  animations: {
    fast: number;
    medium: number;
    slow: number;
  };
  
  // Breakpoints
  breakpoints: {
    mobile: number;
    tablet: number;
    desktop: number;
  };
  
  // Theme colors
  theme: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    info: string;
    background: string;
    surface: string;
    text: {
      primary: string;
      secondary: string;
      disabled: string;
    };
  };
}

export interface WebSocketConfig {
  // Connection settings
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
  
  // Message types
  messageTypes: {
    connect: string;
    disconnect: string;
    subscribe: string;
    unsubscribe: string;
    data: string;
    error: string;
    heartbeat: string;
  };
}

export interface NotificationConfig {
  // Display settings
  duration: number;
  position: string;
  
  // Alert levels
  alertLevels: {
    info: string;
    success: string;
    warning: string;
    error: string;
  };
  
  // Auto-dismiss settings
  autoDismiss: {
    info: number;
    success: number;
    warning: number;
    error: number;
  };
}

export interface AppConfig {
  // API configuration
  api: {
    baseUrl: string;
    timeout: number;
    retryAttempts: number;
    endpoints: ApiEndpoints;
  };
  
  // Feature flags
  features: {
    enableRealtimeUpdates: boolean;
    enableNotifications: boolean;
    enableDarkMode: boolean;
    enableAdvancedCharts: boolean;
    enableExportData: boolean;
  };
  
  // Sensor configurations
  sensors: {
    temperature: TemperatureGaugeConfig;
    humidity: HumidityConfig;
    energy: EnergyConfig;
  };
  
  // UI configuration
  ui: UIConfig;
  
  // WebSocket configuration
  websocket: WebSocketConfig;
  
  // Notification configuration
  notifications: NotificationConfig;
  
  // Update intervals (milliseconds)
  updateIntervals: {
    temperature: number;
    humidity: number;
    energy: number;
    dashboard: number;
    healthCheck: number;
  };
}

// Default configuration
export const defaultConfig: AppConfig = {
  api: {
    baseUrl: 'http://localhost:8001',
    timeout: 10000,
    retryAttempts: 3,
    endpoints: {
      auth: '/api/v1/auth',
      sensors: '/api/v1/sensors',
      websocket: '/ws',
      health: '/health',
      users: '/api/v1/users',
      dashboard: '/api/v1/dashboard'
    }
  },
  
  features: {
    enableRealtimeUpdates: true,
    enableNotifications: true,
    enableDarkMode: true,
    enableAdvancedCharts: true,
    enableExportData: true
  },
  
  sensors: {
    temperature: {
      minTemp: -20,
      maxTemp: 50,
      comfortOptimalMin: 20,
      comfortOptimalMax: 24,
      comfortAcceptableMin: 18,
      comfortAcceptableMax: 26,
      alertCriticalMin: 10,
      alertCriticalMax: 35,
      alertWarningMin: 16,
      alertWarningMax: 28,
      gaugeRadius: 70,
      needleLength: 50,
      centerX: 100,
      centerY: 100,
      animationDuration: 1000,
      transitionEasing: 'cubic-bezier(0.4, 0, 0.2, 1)',
      colors: {
        cold: '#2196F3',
        cool: '#00BCD4',
        comfortable: '#4CAF50',
        warm: '#FF9800',
        hot: '#F44336',
        background: {
          cold: '#E3F2FD',
          cool: '#E0F2F1',
          comfortable: '#E8F5E8',
          warm: '#FFF3E0',
          hot: '#FFEBEE'
        },
        alert: {
          warning: '#FF9800',
          critical: '#F44336'
        }
      }
    },
    
    humidity: {
      minHumidity: 0,
      maxHumidity: 100,
      comfortOptimalMin: 40,
      comfortOptimalMax: 60,
      comfortAcceptableMin: 35,
      comfortAcceptableMax: 65,
      alertCriticalMin: 25,
      alertCriticalMax: 80,
      alertWarningMin: 30,
      alertWarningMax: 70,
      veryDryThreshold: 30,
      dryThreshold: 40,
      comfortableMax: 60,
      humidThreshold: 70,
      colors: {
        veryDry: '#F44336',
        dry: '#FF9800',
        comfortable: '#4CAF50',
        humid: '#2196F3',
        veryHumid: '#9C27B0'
      }
    },
    
    energy: {
      maxPower: 10000,
      alertHighPower: 5000,
      alertCriticalPower: 8000,
      energyRates: {
        peak: 0.28,
        offPeak: 0.12,
        standard: 0.18
      },
      peakHours: [18, 19, 20],
      offPeakHours: [23, 0, 1, 2, 3, 4, 5],
      chartColors: {
        consumption: '#2196F3',
        cost: '#FF9800',
        savings: '#4CAF50'
      }
    }
  },
  
  ui: {
    componentSizes: {
      small: {
        width: 120,
        height: 80,
        fontSize: 24
      },
      medium: {
        width: 200,
        height: 120,
        fontSize: 36
      },
      large: {
        width: 280,
        height: 160,
        fontSize: 48
      }
    },
    
    spacing: {
      small: 8,
      medium: 16,
      large: 24
    },
    
    animations: {
      fast: 200,
      medium: 300,
      slow: 500
    },
    
    breakpoints: {
      mobile: 768,
      tablet: 1024,
      desktop: 1200
    },
    
    theme: {
      primary: '#1976D2',
      secondary: '#424242',
      success: '#4CAF50',
      warning: '#FF9800',
      error: '#F44336',
      info: '#2196F3',
      background: '#FAFAFA',
      surface: '#FFFFFF',
      text: {
        primary: '#212121',
        secondary: '#757575',
        disabled: '#BDBDBD'
      }
    }
  },
  
  websocket: {
    reconnectInterval: 5000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000,
    messageTypes: {
      connect: 'connect',
      disconnect: 'disconnect',
      subscribe: 'subscribe',
      unsubscribe: 'unsubscribe',
      data: 'data',
      error: 'error',
      heartbeat: 'heartbeat'
    }
  },
  
  notifications: {
    duration: 4000,
    position: 'top-right',
    alertLevels: {
      info: 'info',
      success: 'success',
      warning: 'warning',
      error: 'error'
    },
    autoDismiss: {
      info: 4000,
      success: 3000,
      warning: 6000,
      error: 8000
    }
  },
  
  updateIntervals: {
    temperature: 30000,
    humidity: 30000,
    energy: 60000,
    dashboard: 5000,
    healthCheck: 30000
  }
};

// Configuration service for managing app configuration
export class ConfigService {
  private config: AppConfig;
  
  constructor() {
    this.config = this.loadConfig();
  }
  
  private loadConfig(): AppConfig {
    // Try to load from localStorage first
    const storedConfig = localStorage.getItem('app-config');
    if (storedConfig) {
      try {
        const parsed = JSON.parse(storedConfig);
        return { ...defaultConfig, ...parsed };
      } catch (e) {
        console.warn('Failed to parse stored config, using defaults');
      }
    }
    
    // Load from environment variables
    const envConfig = this.loadFromEnvironment();
    return { ...defaultConfig, ...envConfig };
  }
  
  private loadFromEnvironment(): Partial<AppConfig> {
    const envConfig: Partial<AppConfig> = {};
    
    // API configuration from environment
    if (typeof window !== 'undefined' && (window as any).env) {
      const env = (window as any).env;
      
      if (env.API_BASE_URL) {
        envConfig.api = {
          ...defaultConfig.api,
          baseUrl: env.API_BASE_URL
        };
      }
      
      if (env.WEBSOCKET_URL) {
        envConfig.websocket = {
          ...defaultConfig.websocket
        };
      }
      
      // Feature flags from environment
      if (env.ENABLE_REALTIME_UPDATES !== undefined) {
        envConfig.features = {
          ...defaultConfig.features,
          enableRealtimeUpdates: env.ENABLE_REALTIME_UPDATES === 'true'
        };
      }
    }
    
    return envConfig;
  }
  
  public getConfig(): AppConfig {
    return this.config;
  }
  
  public updateConfig(updates: Partial<AppConfig>): void {
    this.config = { ...this.config, ...updates };
    this.saveConfig();
  }
  
  private saveConfig(): void {
    try {
      localStorage.setItem('app-config', JSON.stringify(this.config));
    } catch (e) {
      console.warn('Failed to save config to localStorage');
    }
  }
  
  // Convenience methods for commonly used config values
  public getApiBaseUrl(): string {
    return this.config.api.baseUrl;
  }
  
  public getWebSocketUrl(): string {
    return `${this.config.api.baseUrl.replace('http', 'ws')}${this.config.api.endpoints.websocket}`;
  }
  
  public getTemperatureConfig(): TemperatureGaugeConfig {
    return this.config.sensors.temperature;
  }
  
  public getHumidityConfig(): HumidityConfig {
    return this.config.sensors.humidity;
  }
  
  public getEnergyConfig(): EnergyConfig {
    return this.config.sensors.energy;
  }
  
  public getUIConfig(): UIConfig {
    return this.config.ui;
  }
  
  public isFeatureEnabled(feature: keyof AppConfig['features']): boolean {
    return this.config.features[feature];
  }
  
  public getUpdateInterval(sensor: keyof AppConfig['updateIntervals']): number {
    return this.config.updateIntervals[sensor];
  }
}

// Export singleton instance
export const appConfig = new ConfigService();

// Export individual configuration getters for convenience
// Function to get temperature configuration
export function getTemperatureConfig(): TemperatureGaugeConfig {
  return defaultConfig.sensors.temperature;
}

export const getHumidityConfig = () => appConfig.getHumidityConfig();
export const getEnergyConfig = () => appConfig.getEnergyConfig();
export const getUIConfig = () => appConfig.getUIConfig();

// Function to get API configuration
export function getApiConfig() {
  return defaultConfig.api;
}

export const getWebSocketConfig = () => appConfig.getConfig().websocket; 