# Smart Home IoT Monitoring System

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/BaharakQaderi/smart-home-iot)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://github.com/BaharakQaderi/smart-home-iot)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)](https://github.com/BaharakQaderi/smart-home-iot)
[![Angular](https://img.shields.io/badge/Angular-Frontend-red?logo=angular)](https://github.com/BaharakQaderi/smart-home-iot)
[![InfluxDB](https://img.shields.io/badge/InfluxDB-Database-purple?logo=influxdb)](https://github.com/BaharakQaderi/smart-home-iot)

A comprehensive Smart Home IoT monitoring system built with **FastAPI**, **Angular**, **InfluxDB**, and **Docker**. This project serves as an **educational resource** and **best practice example** for students, demonstrating real-time sensor data collection, monitoring, and visualization for home automation systems.

**🔗 Repository**: https://github.com/BaharakQaderi/smart-home-iot

## 🎯 Project Purpose

This project is designed as an **educational resource** and **best practice example** for students learning modern web development technologies. It serves as a comprehensive sample project that demonstrates how to build a production-ready IoT monitoring system. Students can use this as a reference to:

- **Learn by Example**: Study well-structured, professional code organization
- **Master Modern Stack**: Gain hands-on experience with industry-standard technologies
- **Best Practices**: Understand proper authentication, API design, and system architecture
- **Real-world Application**: See how theoretical concepts apply to practical projects

### 🎓 **What Students Will Learn**

- **Real-time Systems**: WebSocket communication for live sensor data
- **Time-series Data**: InfluxDB for efficient sensor data storage
- **Modern APIs**: FastAPI with automatic documentation and validation
- **Containerization**: Docker for consistent development environments
- **Authentication**: JWT-based secure user management
- **Monitoring**: Grafana dashboards for system visualization
- **Project Structure**: Professional codebase organization and documentation

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

## 🎯 Current Status

**Phase 1: Foundation - ✅ COMPLETE**
- ✅ Backend API with FastAPI
- ✅ JWT Authentication system
- ✅ InfluxDB integration
- ✅ WebSocket real-time communication
- ✅ Docker containerization
- ✅ API documentation with Swagger
- ✅ Frontend dashboard with real-time data visualization
- ✅ Data verification system
- ✅ Responsive UI with Chart.js integration

**Next: Phase 2 - Core Sensors** (Ready for development)

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- **Node.js** (v18+) for frontend development
- **Python** (v3.11+) for backend development
- **Git** for version control

## 🏃 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/BaharakQaderi/smart-home-iot.git
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
- **Backend API**: http://localhost:8001
- **Frontend**: http://localhost:4201
- **InfluxDB**: http://localhost:8087
- **Grafana**: http://localhost:3001
- **Redis**: localhost:6379

### 5. Verify Data Pipeline (Optional)
```bash
./verify-data.sh
```

This script will:
- ✅ Check all services are running
- ✅ Test backend API authentication
- ✅ Verify real-time data is flowing
- ✅ Show sample sensor data

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
npm install --legacy-peer-deps
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
- `GET /api/v1/sensors/latest` - Get latest readings from all sensors

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
ws://localhost:8001/ws
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
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Get sensors (requires authentication)
curl -X GET http://localhost:8001/api/v1/sensors/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Health check
curl http://localhost:8001/health

# Get latest sensor data
curl -X GET http://localhost:8001/api/v1/sensors/latest \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📱 Frontend Features

### Dashboard
- Real-time sensor monitoring (updates every 5 seconds)
- System status overview with connection indicators
- Room-based organization (6 rooms monitored)
- Historical data visualization with Chart.js
- **Data verification panel** - Click "Show Data Verification" to see:
  - Real-time API connection status
  - Raw backend data display
  - Update counters and response times
  - Chart data inspection tools

### Sensor Management
- Temperature, humidity, and energy monitoring
- Device-level power consumption tracking
- Real-time status indicators
- Interactive chart switching

### User Interface
- Responsive design (mobile-friendly)
- Material Design components
- Real-time updates via WebSockets
- Professional dashboard layout

## 🔍 Data Verification

The frontend includes a built-in verification system to prove data authenticity:

1. **Open Dashboard**: http://localhost:4201
2. **Click "Show Data Verification"**: Shows real-time backend connection
3. **Watch Updates**: Counter increments every 5 seconds
4. **Compare Data**: Raw API data matches dashboard display
5. **Test Controls**: Use refresh/clear buttons to test functionality

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
├── verify-data.sh          # Data verification script
├── docker-compose.yml      # Multi-container setup
├── .env                   # Environment variables
└── README.md             # This file
```

## 🔍 Monitoring with Grafana

Access Grafana at http://localhost:3001
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

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**: If ports are already in use, modify `docker-compose.yml`
2. **Permission Errors**: Ensure Docker has proper permissions
3. **Frontend Build Issues**: Run `npm install --legacy-peer-deps` in frontend/
4. **API Connection Issues**: Check if backend is running on port 8001

### Verification Steps

1. **Check Services**: `docker-compose ps`
2. **View Logs**: `docker-compose logs [service-name]`
3. **Test API**: `curl http://localhost:8001/health`
4. **Run Verification**: `./verify-data.sh`

## 📚 Development Phases

### ✅ Phase 1: Foundation (COMPLETE)
- [x] Backend API setup with FastAPI
- [x] JWT Authentication system
- [x] InfluxDB integration for time-series data
- [x] WebSocket real-time communication
- [x] Docker containerization
- [x] Frontend dashboard with Angular
- [x] Real-time data visualization
- [x] Data verification system
- [x] Responsive UI design

### 🔄 Phase 2: Core Sensors (Next)
- [ ] Enhanced sensor simulation
- [ ] Advanced data analytics
- [ ] Alert system implementation
- [ ] Historical data analysis
- [ ] Mobile app development

### 🔄 Phase 3: Advanced Features
- [ ] Security monitoring
- [ ] Machine learning integration
- [ ] Advanced user management
- [ ] Third-party integrations

### 🔄 Phase 4: Production Ready
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Deployment automation
- [ ] Load balancing

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository: https://github.com/BaharakQaderi/smart-home-iot/fork
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### 🐛 Reporting Issues

Found a bug or have a suggestion? Please open an issue:
- **New Issue**: https://github.com/BaharakQaderi/smart-home-iot/issues/new
- **View Issues**: https://github.com/BaharakQaderi/smart-home-iot/issues/new

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the logs: `docker-compose logs`
2. Verify all services are running: `docker-compose ps`
3. Run the verification script: `./verify-data.sh`
4. Check the health endpoints: `curl http://localhost:8001/health`
5. Review the API documentation: http://localhost:8001/docs

## 📧 Contact

- **Repository**: https://github.com/BaharakQaderi/smart-home-iot
- **Issues**: https://github.com/BaharakQaderi/smart-home-iot/issues
- **Author**: [BaharakQaderi](https://github.com/BaharakQaderi)

For questions or support, please open an issue in the repository.

---

**Built with ❤️ using FastAPI, Angular, InfluxDB, and Docker** 