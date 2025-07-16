import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <div class="container">
      <h1>Smart Home IoT Dashboard</h1>
      <p>✅ Angular is working!</p>
      
      <div class="dashboard-preview">
        <h2>Room Temperature Status</h2>
        <div class="rooms-simple">
          <div class="room-card" *ngFor="let room of rooms">
            <h3>{{ room.name }}</h3>
            <div class="temperature">🌡️ {{ room.temperature }}°C</div>
            <div class="humidity">💧 {{ room.humidity }}%</div>
            <div class="status" [style.color]="getStatusColor(room.status)">
              {{ room.status }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="system-info">
        <h3>System Status</h3>
        <p>Last Update: {{ lastUpdate | date:'short' }}</p>
        <p>Rooms Monitored: {{ rooms.length }}</p>
        <button (click)="refreshData()">Refresh Data</button>
      </div>
    </div>
  `,
  styles: [`
    .container {
      padding: 20px;
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      color: white;
    }
    
    .rooms-simple {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin: 20px 0;
    }
    
    .room-card {
      background: rgba(255, 255, 255, 0.1);
      padding: 20px;
      border-radius: 10px;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .temperature { font-size: 24px; margin: 10px 0; }
    .humidity { font-size: 18px; margin: 5px 0; }
    .status { font-size: 16px; font-weight: bold; margin: 5px 0; }
    
    button {
      background: #4CAF50;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
    }
    
    button:hover {
      background: #45a049;
    }
  `]
})
export class AppComponent {
  title = 'smart-home-iot-frontend';
  lastUpdate = new Date();
  
  rooms = [
    { name: 'Living Room', temperature: 22.5, humidity: 45, status: 'comfortable' },
    { name: 'Bedroom', temperature: 20.0, humidity: 50, status: 'comfortable' },
    { name: 'Kitchen', temperature: 23.0, humidity: 40, status: 'comfortable' },
    { name: 'Bathroom', temperature: 24.0, humidity: 60, status: 'comfortable' },
    { name: 'Basement', temperature: 18.0, humidity: 55, status: 'cool' },
    { name: 'Outdoor', temperature: 15.0, humidity: 70, status: 'cool' }
  ];
  
  constructor() {
    // Update data every 30 seconds
    setInterval(() => {
      this.refreshData();
    }, 30000);
  }
  
  refreshData() {
    // Add small random variation to simulate sensor updates
    this.rooms.forEach(room => {
      const variation = (Math.random() - 0.5) * 2;
      room.temperature = Math.round((room.temperature + variation) * 10) / 10;
      
      // Update status based on temperature
      if (room.temperature < 18) room.status = 'cold';
      else if (room.temperature < 20) room.status = 'cool';
      else if (room.temperature < 25) room.status = 'comfortable';
      else if (room.temperature < 28) room.status = 'warm';
      else room.status = 'hot';
    });
    
    this.lastUpdate = new Date();
  }
  
  getStatusColor(status: string): string {
    const colors: { [key: string]: string } = {
      'cold': '#64B5F6',
      'cool': '#81C784',
      'comfortable': '#A5D6A7',
      'warm': '#FFB74D',
      'hot': '#F06292'
    };
    return colors[status] || '#ffffff';
  }
} 