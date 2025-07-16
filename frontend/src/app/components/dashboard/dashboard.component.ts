import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { SensorService } from '../../services/sensor.service';

Chart.register(...registerables);

interface RoomData {
  name: string;
  temperature: number;
  humidity: number;
  status: string;
  energyConsumption: number;
  energyCost: number;
  devices: any[];
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  @ViewChild('temperatureChart', { static: true }) temperatureChartRef!: ElementRef;
  @ViewChild('energyChart', { static: true }) energyChartRef!: ElementRef;

  rooms: RoomData[] = [];
  systemHealthy = false;
  lastUpdate = new Date();
  totalEnergyUsage = 0;
  totalDailyCost = 0;
  averageTemperature = 0;
  activeChart = 'temp';
  
  // New verification properties
  showDataVerification = false;
  rawApiData: any = null;
  dataUpdateCounter = 0;
  apiResponseTime = 0;

  private tempChart: Chart | null = null;
  private energyChartInstance: Chart | null = null;
  private refreshInterval: any;

  // Chart data storage
  private temperatureData: { [key: string]: number[] } = {};
  private humidityData: { [key: string]: number[] } = {};
  private energyData: { [key: string]: number[] } = {};
  public timeLabels: string[] = [];

  constructor(private sensorService: SensorService) {}

  ngOnInit(): void {
    this.initializeCharts();
    this.refreshData();
    this.startPeriodicUpdates();
    // Initialize with some historical-like data to make graphs meaningful
    this.generateInitialChartData();
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
    if (this.tempChart) {
      this.tempChart.destroy();
    }
    if (this.energyChartInstance) {
      this.energyChartInstance.destroy();
    }
  }

  private initializeCharts(): void {
    this.initTemperatureChart();
    this.initEnergyChart();
  }

  private initTemperatureChart(): void {
    const ctx = this.temperatureChartRef.nativeElement.getContext('2d');
    this.tempChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: this.timeLabels,
        datasets: []
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: 'rgba(255, 255, 255, 0.8)' }
          },
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: 'rgba(255, 255, 255, 0.8)' }
          }
        },
        plugins: {
          legend: {
            labels: { color: 'rgba(255, 255, 255, 0.8)' }
          }
        }
      }
    });
  }

  private initEnergyChart(): void {
    const ctx = this.energyChartRef.nativeElement.getContext('2d');
    this.energyChartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [{
          label: 'Energy Consumption (W)',
          data: [],
          backgroundColor: 'rgba(255, 193, 7, 0.6)',
          borderColor: 'rgba(255, 193, 7, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: 'rgba(255, 255, 255, 0.8)' }
          },
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            ticks: { color: 'rgba(255, 255, 255, 0.8)' }
          }
        },
        plugins: {
          legend: {
            labels: { color: 'rgba(255, 255, 255, 0.8)' }
          }
        }
      }
    });
  }

  private async refreshData(): Promise<void> {
    const startTime = Date.now();
    
    try {
      this.sensorService.getLatestReadings().subscribe({
        next: (data) => {
          this.systemHealthy = true;
          this.rawApiData = data; // Store raw data for verification
          this.apiResponseTime = Date.now() - startTime;
          this.dataUpdateCounter++;
          this.transformSensorData(data);
          this.updateCharts();
          this.lastUpdate = new Date();
        },
        error: (error) => {
          console.error('Error fetching sensor data:', error);
          this.systemHealthy = false;
          this.loadMockData();
          this.lastUpdate = new Date();
        }
      });
    } catch (error) {
      console.error('Error fetching sensor data:', error);
      this.systemHealthy = false;
      this.loadMockData();
      this.lastUpdate = new Date();
    }
  }

  private generateInitialChartData(): void {
    // Generate some initial data points to make charts meaningful from the start
    const now = new Date();
    const rooms = ['living_room', 'bedroom', 'kitchen', 'bathroom', 'basement'];
    
    for (let i = 19; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 30000); // 30 seconds ago
      this.timeLabels.push(time.toLocaleTimeString());
      
      rooms.forEach(roomId => {
        if (!this.temperatureData[roomId]) {
          this.temperatureData[roomId] = [];
          this.humidityData[roomId] = [];
          this.energyData[roomId] = [];
        }
        
        // Generate realistic varying data
        const baseTemp = { living_room: 22, bedroom: 20, kitchen: 24, bathroom: 25, basement: 18 };
        const baseHumidity = { living_room: 45, bedroom: 50, kitchen: 60, bathroom: 70, basement: 65 };
        const baseEnergy = { living_room: 150, bedroom: 80, kitchen: 200, bathroom: 100, basement: 50 };
        
        this.temperatureData[roomId].push(
          baseTemp[roomId as keyof typeof baseTemp] + (Math.random() - 0.5) * 4
        );
        this.humidityData[roomId].push(
          baseHumidity[roomId as keyof typeof baseHumidity] + (Math.random() - 0.5) * 20
        );
        this.energyData[roomId].push(
          baseEnergy[roomId as keyof typeof baseEnergy] + (Math.random() - 0.5) * 100
        );
      });
    }
  }

  private transformSensorData(data: any): void {
    this.rooms = [];
    this.totalEnergyUsage = 0;
    this.totalDailyCost = 0;
    let totalTemp = 0;
    let indoorRoomCount = 0;

    // Update time labels
    const currentTime = new Date().toLocaleTimeString();
    this.timeLabels.push(currentTime);
    if (this.timeLabels.length > 20) {
      this.timeLabels.shift();
    }

    Object.keys(data.temperature).forEach(roomId => {
      const tempData = data.temperature[roomId];
      const humidData = data.humidity[roomId];
      const energyData = data.energy[roomId];

      const room: RoomData = {
        name: roomId.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        temperature: Math.round(tempData.temperature * 10) / 10,
        humidity: Math.round(humidData.humidity),
        status: this.getTemperatureStatus(tempData.temperature),
        energyConsumption: energyData.current_power,
        energyCost: energyData.cost_today,
        devices: energyData.devices ? Object.keys(energyData.devices).map(deviceName => ({
          name: deviceName.replace('_', ' '),
          power: energyData.devices[deviceName].power,
          isActive: energyData.devices[deviceName].is_active
        })) : []
      };

      this.totalEnergyUsage += energyData.current_power;
      this.totalDailyCost += energyData.cost_today;

      if (roomId !== 'outdoor') {
        totalTemp += tempData.temperature;
        indoorRoomCount++;
      }

      // Store chart data
      if (!this.temperatureData[roomId]) {
        this.temperatureData[roomId] = [];
      }
      if (!this.humidityData[roomId]) {
        this.humidityData[roomId] = [];
      }
      if (!this.energyData[roomId]) {
        this.energyData[roomId] = [];
      }

      this.temperatureData[roomId].push(tempData.temperature);
      this.humidityData[roomId].push(humidData.humidity);
      this.energyData[roomId].push(energyData.current_power);

      // Keep only last 20 data points
      if (this.temperatureData[roomId].length > 20) {
        this.temperatureData[roomId].shift();
        this.humidityData[roomId].shift();
        this.energyData[roomId].shift();
      }

      this.rooms.push(room);
    });

    this.averageTemperature = indoorRoomCount > 0 ? totalTemp / indoorRoomCount : 0;
  }

  private updateCharts(): void {
    this.updateTemperatureChart();
    this.updateEnergyChart();
  }

  private updateTemperatureChart(): void {
    if (!this.tempChart) return;

    const datasets = Object.keys(this.temperatureData).map((roomId, index) => {
      const colors = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 205, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
      ];

      let data: number[] = [];
      let label = '';
      
      if (this.activeChart === 'temp') {
        data = this.temperatureData[roomId];
        label = `${roomId.replace('_', ' ')} Temperature`;
      } else if (this.activeChart === 'humidity') {
        data = this.humidityData[roomId];
        label = `${roomId.replace('_', ' ')} Humidity`;
      } else if (this.activeChart === 'energy') {
        data = this.energyData[roomId];
        label = `${roomId.replace('_', ' ')} Energy`;
      }

      return {
        label: label,
        data: data,
        borderColor: colors[index % colors.length],
        backgroundColor: colors[index % colors.length].replace('1)', '0.1)'),
        tension: 0.4,
        fill: false
      };
    });

    this.tempChart.data.labels = this.timeLabels;
    this.tempChart.data.datasets = datasets;
    this.tempChart.update();
  }

  private updateEnergyChart(): void {
    if (!this.energyChartInstance) return;

    const roomLabels = this.rooms.map(room => room.name);
    const energyValues = this.rooms.map(room => room.energyConsumption);

    this.energyChartInstance.data.labels = roomLabels;
    this.energyChartInstance.data.datasets[0].data = energyValues;
    this.energyChartInstance.update();
  }

  private loadMockData(): void {
    // Fallback mock data for when API is unavailable
    this.rooms = [
      { name: 'Living Room', temperature: 22.5, humidity: 45, status: 'comfortable', energyConsumption: 120, energyCost: 0.08, devices: [] },
      { name: 'Bedroom', temperature: 20.0, humidity: 50, status: 'comfortable', energyConsumption: 80, energyCost: 0.05, devices: [] },
      { name: 'Kitchen', temperature: 23.0, humidity: 40, status: 'comfortable', energyConsumption: 200, energyCost: 0.12, devices: [] },
      { name: 'Bathroom', temperature: 24.0, humidity: 60, status: 'comfortable', energyConsumption: 150, energyCost: 0.09, devices: [] }
    ];

    this.totalEnergyUsage = 550;
    this.totalDailyCost = 0.34;
    this.averageTemperature = 22.4;
  }

  private getTemperatureStatus(temperature: number): string {
    if (temperature < 18) return 'cold';
    if (temperature < 20) return 'cool';
    if (temperature < 25) return 'comfortable';
    if (temperature < 28) return 'warm';
    return 'hot';
  }

  private startPeriodicUpdates(): void {
    this.refreshInterval = setInterval(() => {
      this.refreshData();
    }, 5000); // Update every 5 seconds for more real-time feel
  }

  toggleChartType(type: string): void {
    this.activeChart = type;
    this.updateTemperatureChart();
  }

  getActiveDeviceCount(devices: any[]): number {
    return devices.filter(device => device.isActive).length;
  }

  // New verification methods
  toggleDataVerification(): void {
    this.showDataVerification = !this.showDataVerification;
  }

  getRawDataForRoom(roomId: string): any {
    if (!this.rawApiData) return null;
    return {
      temperature: this.rawApiData.temperature[roomId],
      humidity: this.rawApiData.humidity[roomId],
      energy: this.rawApiData.energy[roomId]
    };
  }

  getChartDataForRoom(roomId: string): any {
    return {
      temperature: this.temperatureData[roomId] || [],
      humidity: this.humidityData[roomId] || [],
      energy: this.energyData[roomId] || []
    };
  }

  forceDataRefresh(): void {
    this.refreshData();
  }

  clearChartData(): void {
    this.temperatureData = {};
    this.humidityData = {};
    this.energyData = {};
    this.timeLabels = [];
    this.dataUpdateCounter = 0;
    this.generateInitialChartData();
    this.updateCharts();
  }
} 