import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface SensorData {
  sensor_id: string;
  sensor_type: string;
  room_id: string;
  name: string;
  status: string;
  last_reading: any;
  config: any;
}

export interface LatestReadings {
  temperature: { [key: string]: any };
  humidity: { [key: string]: any };
  energy: { [key: string]: any };
  energy_total: any;
}

export interface RoomData {
  name: string;
  temperature: number;
  humidity: number;
  status: string;
  energyConsumption: number;
  energyCost: number;
  devices: any[];
}

@Injectable({
  providedIn: 'root'
})
export class SensorService {
  private baseUrl = environment.apiUrl;
  private token: string | null = null;
  
  private roomsDataSubject = new BehaviorSubject<RoomData[]>([]);
  public roomsData$ = this.roomsDataSubject.asObservable();

  constructor(private http: HttpClient) {
    this.initializeToken();
    this.startPeriodicUpdates();
  }

  private initializeToken(): void {
    // For demo purposes, we'll use a basic auth approach
    // In production, this should be handled by an authentication service
    this.token = localStorage.getItem('access_token');
    if (!this.token) {
      // Try to get a token by logging in with default credentials
      this.login('admin', 'admin123');
    }
  }

  private async login(username: string, password: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.access_token;
        localStorage.setItem('access_token', this.token!);
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  }

  private getHeaders(): HttpHeaders {
    const headers: any = {
      'Content-Type': 'application/json'
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return new HttpHeaders(headers);
  }

  getLatestReadings(): Observable<LatestReadings> {
    return this.http.get<LatestReadings>(`${this.baseUrl}/sensors/latest`, {
      headers: this.getHeaders()
    });
  }

  getAllSensors(): Observable<SensorData[]> {
    return this.http.get<SensorData[]>(`${this.baseUrl}/sensors/`, {
      headers: this.getHeaders()
    });
  }

  getRoomData(): Observable<RoomData[]> {
    return this.getLatestReadings().pipe(
      map(readings => this.transformToRoomData(readings))
    );
  }

  private transformToRoomData(readings: LatestReadings): RoomData[] {
    const rooms: RoomData[] = [];
    
    // Process each room
    Object.keys(readings.temperature).forEach(roomId => {
      const tempData = readings.temperature[roomId];
      const humidData = readings.humidity[roomId];
      const energyData = readings.energy[roomId];
      
      const room: RoomData = {
        name: roomId.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        temperature: tempData.temperature,
        humidity: humidData.humidity,
        status: this.getTemperatureStatus(tempData.temperature),
        energyConsumption: energyData.current_power,
        energyCost: energyData.cost_today,
        devices: energyData.devices ? Object.keys(energyData.devices).map(deviceName => ({
          name: deviceName,
          power: energyData.devices[deviceName].power,
          isActive: energyData.devices[deviceName].is_active
        })) : []
      };
      
      rooms.push(room);
    });
    
    return rooms;
  }

  private getTemperatureStatus(temperature: number): string {
    if (temperature < 18) return 'cold';
    if (temperature < 20) return 'cool';
    if (temperature < 25) return 'comfortable';
    if (temperature < 28) return 'warm';
    return 'hot';
  }

  private startPeriodicUpdates(): void {
    // Update immediately
    this.updateRoomsData();
    
    // Update every 10 seconds
    setInterval(() => {
      this.updateRoomsData();
    }, 10000);
  }

  private updateRoomsData(): void {
    this.getRoomData().subscribe(
      rooms => {
        this.roomsDataSubject.next(rooms);
      },
      error => {
        console.error('Error fetching sensor data:', error);
      }
    );
  }
} 