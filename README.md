# Smart Home IoT Monitoring System

A comprehensive Smart Home IoT monitoring system built with **FastAPI**, **Angular**, **InfluxDB**, and **Docker**. This project demonstrates real-time sensor data collection, monitoring, and visualization for home automation systems.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Angular SPA   │◄──►│   FastAPI API   │◄──►│   InfluxDB      │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Background    │    │   Grafana       │
│   Connection    │    │   Workers       │    │   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **WebSockets** - Real-time bidirectional communication
- **InfluxDB** - Time series database for sensor data
- **Redis** - Session management and caching
- **JWT** - Authentication and authorization

### Frontend
- **Angular 15+** - TypeScript-based frontend framework
- **Angular Material** - UI component library
- **Chart.js** - Data visualization
- **WebSockets** - Real-time updates

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Grafana** - Advanced monitoring dashboards
- **Nginx** - Reverse proxy

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **Node.js** (v18+) for frontend development
- **Python** (v3.11+) for backend development
- **Git** for version control

## 🏃 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd smart-home-iot
```

### 2. Setup Environment Variables
```bash
cp env.example .env
# Edit .env with your settings if needed
```

### 3. Start the Development Environment
```bash
docker-compose up -d
```

### 4. Verify Services are Running
```bash
docker-compose ps
```

You should see all services running:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:4200
- **InfluxDB**: http://localhost:8086
- **Grafana**: http://localhost:3000
- **Redis**: localhost:6379

## 🔧 Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
ng serve --host 0.0.0.0 --port 4200
```

## 📊 Available Endpoints

### 🔐 Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user profile

### 📡 Sensors
- `GET /api/v1/sensors/` - Get all sensors
- `GET /api/v1/sensors/{sensor_id}` - Get specific sensor
- `GET /api/v1/sensors/{sensor_id}/data` - Get sensor data
- `GET /api/v1/sensors/type/{sensor_type}` - Get sensors by type

### 🏠 Rooms
- `GET /api/v1/rooms/` - Get all rooms
- `GET /api/v1/rooms/{room_id}` - Get specific room

### 📈 Dashboard
- `GET /api/v1/dashboard/summary` - Get dashboard summary
- `GET /api/v1/dashboard/system-status` - Get system status

### 🚨 Alerts
- `GET /api/v1/alerts/` - Get all alerts
- `GET /api/v1/alerts/active` - Get active alerts

### 🔍 System
- `GET /health` - Health check endpoint
- `GET /docs` - API documentation (Swagger)
- `GET /redoc` - Alternative API documentation

## 🌐 WebSocket Connection

Connect to the WebSocket endpoint for real-time updates:
```
ws://localhost:8000/ws
```

### WebSocket Message Types
- `sensor_data` - Real-time sensor readings
- `connection_confirmed` - Connection establishment
- `subscribe_room` - Subscribe to room updates
- `subscribe_sensor` - Subscribe to sensor updates

## 🧪 Testing the API

### Default Users
- **Admin**: username: `admin`, password: `admin123`
- **User**: username: `user`, password: `user123`

### Example API Calls
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Get sensors (requires authentication)
curl -X GET http://localhost:8000/api/v1/sensors/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Health check
curl http://localhost:8000/health
```

## 📱 Frontend Features

### Dashboard
- Real-time sensor monitoring
- System status overview
- Room-based organization
- Historical data visualization

### Sensor Management
- Sensor status monitoring
- Data visualization
- Alert management

### User Interface
- Responsive design
- Material Design components
- Real-time updates via WebSockets

## 🛠️ Project Structure

```
smart-home-iot/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── models/            # Data models
│   │   ├── services/          # Business logic
│   │   └── main.py           # Application entry point
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container config
├── frontend/                  # Angular frontend
│   ├── src/
│   │   ├── app/              # Angular application
│   │   ├── assets/           # Static assets
│   │   └── environments/     # Environment configs
│   └── package.json          # Node.js dependencies
├── infrastructure/           # Infrastructure configs
│   └── docker/              # Docker configurations
├── data/                    # Persistent data
│   ├── influxdb/           # InfluxDB data
│   ├── grafana/            # Grafana data
│   └── logs/               # Application logs
├── docker-compose.yml      # Multi-container setup
├── .env                   # Environment variables
└── README.md             # This file
```

## 🔍 Monitoring with Grafana

Access Grafana at http://localhost:3000
- **Username**: admin
- **Password**: admin123

Pre-configured dashboards for:
- System overview
- Sensor data visualization
- Performance metrics
- Alert management

## 🧹 Cleanup

To stop all services:
```bash
docker-compose down
```

To remove all data and start fresh:
```bash
docker-compose down -v
rm -rf data/
```

## 📚 Development Phases

### ✅ Phase 1: Foundation (Current)
- [x] Backend API setup
- [x] Authentication system
- [x] WebSocket support
- [x] Docker environment
- [x] Basic API endpoints

### 🔄 Phase 2: Core Sensors (Next)
- [ ] Sensor data simulation
- [ ] Real-time data streaming
- [ ] Frontend dashboard
- [ ] Data visualization

### 🔄 Phase 3: Advanced Features
- [ ] Security monitoring
- [ ] Alert system
- [ ] User management
- [ ] Mobile support

### 🔄 Phase 4: Production Ready
- [ ] Performance optimization
- [ ] Complete testing
- [ ] Deployment automation
- [ ] Comprehensive documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the logs: `docker-compose logs`
2. Verify all services are running: `docker-compose ps`
3. Check the health endpoints
4. Review the documentation

## 📧 Contact

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using FastAPI, Angular, InfluxDB, and Docker** 