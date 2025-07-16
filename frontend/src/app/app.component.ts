import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <mat-toolbar color="primary">
      <mat-icon>home</mat-icon>
      <span>Smart Home IoT Dashboard</span>
    </mat-toolbar>
    
    <div class="container">
      <mat-card class="welcome-card">
        <mat-card-header>
          <mat-card-title>Welcome to Smart Home IoT</mat-card-title>
          <mat-card-subtitle>Phase 1 Complete - Ready for Phase 2 Development</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p>🎉 <strong>Phase 1 Foundation Complete!</strong></p>
          <ul>
            <li>✅ Backend API with JWT Authentication</li>
            <li>✅ InfluxDB Time-Series Database</li>
            <li>✅ WebSocket Real-time Communication</li>
            <li>✅ Docker Containerization</li>
            <li>✅ Nginx Reverse Proxy</li>
            <li>✅ Frontend Application Structure</li>
          </ul>
          <p><strong>Next:</strong> Phase 2 - Sensor Data Simulation & Visualization</p>
        </mat-card-content>
        <mat-card-actions>
          <button mat-raised-button color="primary" (click)="testBackend()">
            Test Backend Connection
          </button>
          <button mat-raised-button color="accent" (click)="testWebSocket()">
            Test WebSocket
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .container {
      max-width: 800px;
      margin: 20px auto;
      padding: 20px;
    }
    
    .welcome-card {
      margin: 20px 0;
    }
    
    ul {
      margin: 16px 0;
    }
    
    li {
      margin: 8px 0;
    }
    
    mat-card-actions {
      display: flex;
      gap: 12px;
    }
  `]
})
export class AppComponent {
  title = 'smart-home-iot-frontend';

  testBackend() {
    console.log('Testing backend connection...');
    // TODO: Implement backend connection test
  }

  testWebSocket() {
    console.log('Testing WebSocket connection...');
    // TODO: Implement WebSocket connection test
  }
} 