# Smart Home IoT - Development Agent Prompt

## 🎯 **PROJECT CONTEXT**

You are working on a **Smart Home IoT Monitoring System** - a practice project designed to master the same technology stack as the kitenergy-monorepo (FastAPI, Angular, InfluxDB, Docker). This is a learning project to build confidence with real-time monitoring systems.

## 📁 **CURRENT PROJECT STATE**

**Location**: `/Users/baharakqaderi/smart-home-iot/`

**What EXISTS:**
- ✅ Project specification document (`SmartHome_IoT_Project_Specification.md`)
- ✅ Basic directory structure (backend/, frontend/, infrastructure/, data/, docs/)
- ✅ Environment configuration template (`env.example`)
- ✅ Partial backend structure (some directories exist but missing key files)
- ✅ Partial infrastructure configuration

**What's MISSING/INCOMPLETE:**
- ❌ Backend `requirements.txt` and `Dockerfile`
- ❌ Backend Python files (main.py, core modules, models, etc.)
- ❌ Docker Compose configuration  
- ❌ Frontend Angular application
- ❌ Complete infrastructure setup

## 🎯 **YOUR MISSION**

Build a **production-ready Smart Home IoT Monitoring System** following the specification document. This system should demonstrate mastery of:

1. **FastAPI Backend** with WebSocket real-time communication
2. **Angular Frontend** with Material Design and real-time updates
3. **InfluxDB** time-series database for sensor data
4. **Docker** containerized development environment
5. **Real-time Architecture** for IoT sensor monitoring

## 📋 **DEVELOPMENT PHASES**

### **Phase 1: Foundation (Current Priority)**
**Goal**: Set up working development environment

**Tasks**:
1. **Backend Setup**:
   - Create `backend/requirements.txt` with all necessary Python dependencies
   - Create `backend/Dockerfile` for containerization
   - Implement `backend/app/main.py` (FastAPI application entry point)
   - Create core modules: config, database (InfluxDB), WebSocket manager
   - Set up basic API endpoints and health checks

2. **Infrastructure**:
   - Create proper `docker-compose.yml` in project root
   - Configure InfluxDB, Redis, Grafana services
   - Set up Nginx reverse proxy configuration

3. **Frontend Setup**:
   - Create Angular project with TypeScript
   - Set up Angular Material UI framework
   - Create basic routing and layout structure

4. **Verification**:
   - `docker-compose up` should start all services
   - Backend API accessible at http://localhost:8000
   - Frontend accessible at http://localhost:4200
   - InfluxDB UI at http://localhost:8086
   - Grafana at http://localhost:3000

### **Phase 2: Core Sensors (Next)**
- Implement sensor data simulation (temperature, humidity, energy)
- Create real-time WebSocket communication
- Build dashboard components with live data visualization

### **Phase 3: Advanced Features (Later)**
- Security monitoring, alerts system
- Analytics and historical data views
- Mobile-responsive design

### **Phase 4: Production Ready (Final)**
- Performance optimization, testing
- Grafana dashboards, monitoring
- Complete documentation

## 🛠️ **TECHNICAL REQUIREMENTS**

**Backend Stack**:
- FastAPI with automatic OpenAPI documentation
- WebSocket support for real-time communication
- InfluxDB client for time-series data
- Pydantic for data validation
- JWT authentication
- Background task workers for sensor simulation

**Frontend Stack**:
- Angular 15+ with TypeScript
- Angular Material for UI components
- Chart.js for data visualization
- WebSocket client for real-time updates
- Responsive design (mobile-first)

**Infrastructure**:
- Docker & Docker Compose for development
- InfluxDB 2.x for time-series database
- Redis for caching and session management
- Grafana for advanced monitoring dashboards
- Nginx for reverse proxy (production)

## 📊 **SUCCESS CRITERIA**

**Phase 1 Complete When**:
- ✅ `docker-compose up` starts all services successfully
- ✅ Backend API returns health check at `/health`
- ✅ Frontend loads and displays basic dashboard
- ✅ InfluxDB connection established
- ✅ WebSocket connection works (basic echo test)
- ✅ All services can communicate with each other

## 🚀 **GETTING STARTED**

1. **Read the specification**: Start with `SmartHome_IoT_Project_Specification.md`
2. **Set up environment**: Copy `env.example` to `.env` and configure
3. **Begin with backend**: Create missing files in `backend/` directory
4. **Test incrementally**: Ensure each component works before moving to next
5. **Follow the phases**: Complete Phase 1 before moving to sensors

## 💡 **KEY PRINCIPLES**

- **Real-world ready**: Build as if this will go to production
- **Best practices**: Follow industry standards for each technology
- **Documentation**: Document decisions and configurations
- **Testing**: Include tests for critical functionality
- **Scalability**: Design for future expansion and multiple sensors

## 📚 **REFERENCE ARCHITECTURE**

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

## 🎯 **IMMEDIATE NEXT STEPS**

1. Create `backend/requirements.txt` with FastAPI, InfluxDB, WebSocket dependencies
2. Create `backend/Dockerfile` for Python application
3. Implement `backend/app/main.py` with basic FastAPI setup
4. Create `docker-compose.yml` in project root
5. Test that containers start and communicate

**Remember**: This project is about learning and mastering the tech stack. Take time to understand each component deeply, not just make it work! 