import { Component, OnInit } from '@angular/core';

interface SimpleRoomData {
  room_id: string;
  temperature: number;
  humidity: number;
  status: string;
  timestamp: string;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  roomData: SimpleRoomData[] = [];
  isLoading = false;
  error: string | null = null;
  lastUpdate: Date = new Date();

  ngOnInit(): void {
    this.loadRoomData();
    // Update every 30 seconds
    setInterval(() => {
      this.loadRoomData();
    }, 30000);
  }

  private loadRoomData(): void {
    this.isLoading = true;
    this.error = null;
    
    // Generate mock data for now
    this.roomData = [
      {
        room_id: 'living_room',
        temperature: 22.5,
        humidity: 45,
        status: 'comfortable',
        timestamp: new Date().toISOString()
      },
      {
        room_id: 'bedroom',
        temperature: 20.0,
        humidity: 50,
        status: 'comfortable',
        timestamp: new Date().toISOString()
      },
      {
        room_id: 'kitchen',
        temperature: 23.0,
        humidity: 40,
        status: 'comfortable',
        timestamp: new Date().toISOString()
      },
      {
        room_id: 'bathroom',
        temperature: 24.0,
        humidity: 60,
        status: 'comfortable',
        timestamp: new Date().toISOString()
      },
      {
        room_id: 'basement',
        temperature: 18.0,
        humidity: 55,
        status: 'cool',
        timestamp: new Date().toISOString()
      },
      {
        room_id: 'outdoor',
        temperature: 15.0,
        humidity: 70,
        status: 'cool',
        timestamp: new Date().toISOString()
      }
    ];
    
    this.isLoading = false;
    this.lastUpdate = new Date();
  }

  refreshData(): void {
    this.loadRoomData();
  }

  getRoomDisplayName(roomId: string): string {
    const names: { [key: string]: string } = {
      'living_room': 'Living Room',
      'bedroom': 'Bedroom',
      'kitchen': 'Kitchen',
      'bathroom': 'Bathroom',
      'basement': 'Basement',
      'outdoor': 'Outdoor'
    };
    return names[roomId] || roomId;
  }

  getTemperatureColor(temperature: number): string {
    if (temperature < 18) return '#2196F3'; // Cold - Blue
    if (temperature < 20) return '#00BCD4'; // Cool - Cyan
    if (temperature < 25) return '#4CAF50'; // Comfortable - Green
    if (temperature < 28) return '#FF9800'; // Warm - Orange
    return '#F44336'; // Hot - Red
  }

  getStatusColor(status: string): string {
    const colors: { [key: string]: string } = {
      'comfortable': '#4CAF50',
      'cool': '#2196F3',
      'warm': '#FF9800',
      'hot': '#F44336',
      'cold': '#607D8B'
    };
    return colors[status] || '#757575';
  }
} 