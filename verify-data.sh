#!/bin/bash

# Smart Home IoT Data Verification Script
# This script helps verify that the frontend is displaying real backend data

echo "🔍 Smart Home IoT Data Verification"
echo "==================================="
echo

# Check if backend is running
echo "1. Checking backend health..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Backend is running on port 8001"
else
    echo "❌ Backend is not accessible on port 8001"
    exit 1
fi

# Check if frontend is running
echo "2. Checking frontend..."
if curl -s http://localhost:4201 > /dev/null; then
    echo "✅ Frontend is running on port 4201"
else
    echo "❌ Frontend is not accessible on port 4201"
    exit 1
fi

# Get auth token
echo "3. Getting authentication token..."
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo "✅ Authentication successful"
else
    echo "❌ Authentication failed"
    exit 1
fi

# Test sensor data endpoint
echo "4. Testing sensor data endpoint..."
SENSOR_DATA=$(curl -s -X GET http://localhost:8001/api/v1/sensors/latest \
    -H "Authorization: Bearer $TOKEN")

if echo "$SENSOR_DATA" | grep -q "temperature"; then
    echo "✅ Sensor data endpoint working"
else
    echo "❌ Sensor data endpoint not working"
    exit 1
fi

# Show sample data
echo "5. Sample sensor data from backend:"
echo "$SENSOR_DATA" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('📊 Temperature Data:')
    for room, temp_data in data['temperature'].items():
        print(f'  {room}: {temp_data[\"temperature\"]}°C')
    print('💧 Humidity Data:')
    for room, humid_data in data['humidity'].items():
        print(f'  {room}: {humid_data[\"humidity\"]}%')
    print('⚡ Energy Data:')
    for room, energy_data in data['energy'].items():
        print(f'  {room}: {energy_data[\"current_power\"]}W')
except Exception as e:
    print(f'Error parsing data: {e}')
"

echo
echo "6. Testing data changes over time..."
echo "Taking 3 samples 5 seconds apart to verify data is changing..."

for i in {1..3}; do
    echo "Sample $i:"
    curl -s -X GET http://localhost:8001/api/v1/sensors/latest \
        -H "Authorization: Bearer $TOKEN" | \
        python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    living_room = data['temperature']['living_room']
    print(f'  Living Room: {living_room[\"temperature\"]}°C, Kitchen Energy: {data[\"energy\"][\"kitchen\"][\"current_power\"]}W')
except Exception as e:
    print(f'  Error: {e}')
"
    if [ $i -lt 3 ]; then
        echo "  Waiting 5 seconds..."
        sleep 5
    fi
done

echo
echo "✅ Data Verification Complete!"
echo
echo "🎯 How to verify the frontend is showing real data:"
echo "1. Open http://localhost:4201 in your browser"
echo "2. Click 'Show Data Verification' button in the dashboard"
echo "3. Watch the 'Updates' counter increase every 5 seconds"
echo "4. Check the 'Latest Raw API Data' section matches the backend"
echo "5. Observe the graphs updating with new data points"
echo
echo "📈 What the graphs show:"
echo "- Temperature: Real-time temperature readings from all rooms"
echo "- Humidity: Real-time humidity levels from all rooms"
echo "- Energy: Real-time power consumption from all rooms"
echo "- Each data point represents a 5-second interval"
echo "- The graph shows the last 20 data points (about 1.5 minutes)"
echo
echo "🔄 If you want to see more dramatic changes:"
echo "- Click the 'Clear Charts' button to reset the graphs"
echo "- Use the 'Refresh' button to force an immediate update"
echo "- Switch between Temperature/Humidity/Energy using the buttons" 