# Delivery Route Optimizer - API Examples and Testing Guide

## Quick Test Script (Optional)

Save as `test_api.py` and run: `python test_api.py`

```python
#!/usr/bin/env python
import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from routes.models import Vehicle, Location, Route
from routes.services import RoutingService, ETAService, AnalyticsService

# Test Routing Service
print("\n🧪 Testing Routing Services...")
print("=" * 50)

locations = Location.objects.all()[:4]
if locations.count() < 2:
    print("⚠️  Need at least 2 locations for testing")
    sys.exit(1)

vehicle = Vehicle.objects.first()
if not vehicle:
    print("⚠️  Need at least 1 vehicle for testing")
    sys.exit(1)

print(f"\n📍 Found {locations.count()} locations and {Vehicle.objects.count()} vehicles")

# Test TSP optimization
print("\n1️⃣  Testing Route Optimization...")
try:
    route = RoutingService.create_route(vehicle, list(locations.values_list('id', flat=True)))
    print(f"✅ Route created: ID={route.id}, Distance={route.total_distance:.2f}km")
except Exception as e:
    print(f"❌ Error: {e}")

# Test ETA calculation
print("\n2️⃣  Testing ETA Calculation...")
try:
    eta = ETAService.calculate_route_eta(route, vehicle)
    print(f"✅ ETA calculated: {eta['eta_minutes']:.0f} minutes")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Analytics
print("\n3️⃣  Testing Analytics...")
try:
    stats = AnalyticsService.get_vehicle_stats(vehicle)
    print(f"✅ Vehicle Stats: {stats['total_deliveries']} deliveries, {stats['total_distance_km']}km")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Fleet Analytics
print("\n4️⃣  Testing Fleet Analytics...")
try:
    fleet = AnalyticsService.get_fleet_stats()
    print(f"✅ Fleet Stats: {fleet['total_vehicles']} vehicles, {fleet['total_deliveries']} deliveries")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ All tests passed!")
```

## REST API Testing Examples

### Using curl

#### 1. Health Check
```bash
curl -i http://localhost:8000/api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Delivery Optimizer API is running",
  "timestamp": "2026-03-30T12:00:00Z"
}
```

#### 2. Authentication

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "driver_john",
    "email": "john@example.com",
    "password": "secure123",
    "role": "driver"
  }'
```

**Response:**
```json
{
  "id": 3,
  "username": "driver_john",
  "email": "john@example.com",
  "role": "driver"
}
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin@123"
  }'
```

#### 3. Location Management

**Get All Locations:**
```bash
curl http://localhost:8000/api/locations/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Customer A",
    "latitude": 51.515,
    "longitude": -0.1,
    "address": "123 Main St",
    "created_at": "2026-03-30T10:00:00Z"
  }
]
```

**Create Location:**
```bash
curl -X POST http://localhost:8000/api/locations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Hub",
    "address": "789 Central Ave",
    "latitude": 51.52,
    "longitude": -0.11
  }'
```

**Update Location:**
```bash
curl -X PUT http://localhost:8000/api/locations/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "address": "Updated Address"
  }'
```

**Delete Location:**
```bash
curl -X DELETE http://localhost:8000/api/locations/1/
```

#### 4. Vehicle Management

**List Vehicles:**
```bash
curl http://localhost:8000/api/vehicles/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Van-01",
    "driver": null,
    "driver_name": "",
    "latitude": 40.7128,
    "longitude": -74.006,
    "status": "idle",
    "color": "#FFC107",
    "speed": 50,
    "capacity": 50,
    "current_load": 0,
    "created_at": "2026-03-30T09:00:00Z",
    "updated_at": "2026-03-30T10:30:00Z"
  }
]
```

**Create Vehicle:**
```bash
curl -X POST http://localhost:8000/api/vehicles/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New-Van-02",
    "latitude": 40.7300,
    "longitude": -74.0100,
    "status": "active",
    "color": "#FF6B6B",
    "speed": 55,
    "capacity": 60,
    "current_load": 0
  }'
```

**Update Vehicle Position:**
```bash
curl -X POST http://localhost:8000/api/vehicles/position/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 40.7200,
    "longitude": -74.0050,
    "speed": 48.5,
    "heading": 90.0
  }'
```

#### 5. Route Optimization

**Optimize Route:**
```bash
curl -X POST http://localhost:8000/api/routes/optimize/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "location_ids": [1, 2, 3, 4]
  }'
```

**Response:**
```json
{
  "id": 5,
  "vehicle": 1,
  "vehicle_name": "Van-01",
  "stops": [
    {
      "id": 10,
      "order": 0,
      "location": 1,
      "location_name": "Customer A",
      "location_coords": {
        "latitude": 51.515,
        "longitude": -0.1
      },
      "arrival_time": null,
      "completed_at": null,
      "was_delivered": false
    }
  ],
  "total_distance": 12.45,
  "estimated_time": 42.3,
  "location_count": 4,
  "created_at": "2026-03-30T11:00:00Z",
  "completed_at": null,
  "is_active": true,
  "eta_info": {
    "eta_minutes": 42.30,
    "eta_datetime": "2026-03-30T11:42:30Z",
    "distance_km": 12.45
  }
}
```

**Get All Routes:**
```bash
curl http://localhost:8000/api/routes/
```

**Get Route Details:**
```bash
curl http://localhost:8000/api/routes/5/
```

#### 6. Tracking

**Get Vehicle Tracking History:**
```bash
curl "http://localhost:8000/api/tracking/vehicles/1/?limit=50"
```

**Response:**
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Van-01",
  "tracking_points": [
    {
      "id": 100,
      "vehicle": 1,
      "vehicle_name": "Van-01",
      "latitude": 40.7128,
      "longitude": -74.006,
      "speed": 45.2,
      "heading": 180.0,
      "accuracy": 10.0,
      "timestamp": "2026-03-30T11:05:00Z"
    }
  ]
}
```

**Get Simulated Movement Points:**
```bash
curl -X POST http://localhost:8000/api/tracking/simulate/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "route_id": 5
  }'
```

#### 7. Delivery Operations

**Mark Delivery as Completed:**
```bash
curl -X POST http://localhost:8000/api/routes/delivery/complete/ \
  -H "Content-Type: application/json" \
  -d '{
    "route_stop_id": 10,
    "notes": "Delivered successfully, customer present"
  }'
```

#### 8. Analytics

**Get Vehicle Analytics:**
```bash
curl http://localhost:8000/api/analytics/vehicles/1/
```

**Response:**
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Van-01",
  "active_routes": 1,
  "completed_routes": 2,
  "total_distance_km": 145.67,
  "total_deliveries": 23,
  "utilization": 45.5
}
```

**Get Fleet Analytics:**
```bash
curl http://localhost:8000/api/analytics/fleet/
```

**Response:**
```json
{
  "total_vehicles": 3,
  "active_vehicles": 1,
  "idle_vehicles": 2,
  "maintenance_vehicles": 0,
  "total_distance_km": 425.30,
  "total_deliveries": 68,
  "vehicle_stats": [
    {
      "vehicle_id": 1,
      "vehicle_name": "Van-01",
      "active_routes": 1,
      "completed_routes": 2,
      "total_distance_km": 145.67,
      "total_deliveries": 23,
      "utilization": 45.5
    }
  ]
}
```

**Get Delivery Metrics:**
```bash
curl http://localhost:8000/api/analytics/deliveries/
```

**Response:**
```json
{
  "total_deliveries": 68,
  "failed_deliveries": 2,
  "success_rate": 97.14,
  "average_delivery_time_minutes": 28.5,
  "timestamp": "2026-03-30T12:00:00Z"
}
```

## WebSocket Examples

### JavaScript Client

```javascript
// Connect to WebSocket
const vehicleId = 1;
const ws = new WebSocket(`ws://localhost:8000/ws/tracking/vehicle/${vehicleId}/`);

ws.onopen = (event) => {
  console.log('WebSocket connected');

  // Get vehicle status
  ws.send(JSON.stringify({
    type: 'get_status'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'location_update') {
    console.log('📍 Location update:', data.data);
    // Update map marker
  } else if (data.type === 'vehicle_status') {
    console.log('🚗 Vehicle status:', data.data);
  } else if (data.type === 'error') {
    console.error('❌ Error:', data.message);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('WebSocket disconnected');
};

// Send location update
function updateLocation(lat, lon, speed, heading) {
  ws.send(JSON.stringify({
    type: 'location_update',
    latitude: lat,
    longitude: lon,
    speed: speed,
    heading: heading
  }));
}

// Start simulation
function startSimulation(routeId) {
  ws.send(JSON.stringify({
    type: 'start_simulation',
    route_id: routeId
  }));
}

// Stop simulation
function stopSimulation() {
  ws.send(JSON.stringify({
    type: 'stop_simulation'
  }));
}
```

## Performance Benchmarks

### Expected Response Times

| Endpoint | Method | Time (ms) |
|----------|--------|-----------|
| GET /api/locations/ | GET | 10-20 |
| POST /api/routes/optimize/ | POST | 50-150 |
| GET /api/analytics/fleet/ | GET | 30-50 |
| WebSocket connection | - | 5-15 |
| Location update (WS) | - | 10-30 |

## Error Handling

### Common HTTP Status Codes

```
200 OK             - Successful GET/PUT
201 CREATED        - Successful POST
204 NO CONTENT     - Successful DELETE
400 BAD REQUEST    - Invalid input data
401 UNAUTHORIZED   - Missing/invalid authentication
404 NOT FOUND      - Resource not found
500 SERVER ERROR   - Internal server error
```

### Error Response Example

```json
{
  "error": "Need at least 2 locations to compute route",
  "status": 400
}
```

## Testing with Python requests

```python
import requests
import json

BASE_URL = 'http://localhost:8000/api'

# Health check
response = requests.get(f'{BASE_URL}/health/')
print(response.json())

# Create location
payload = {
    'name': 'Test Location',
    'latitude': 40.7128,
    'longitude': -74.0060,
    'address': 'Test Address'
}
response = requests.post(f'{BASE_URL}/locations/', json=payload)
print(f"Created location: {response.status_code}")

# Optimize route
payload = {
    'vehicle_id': 1,
    'location_ids': [1, 2, 3]
}
response = requests.post(f'{BASE_URL}/routes/optimize/', json=payload)
route_data = response.json()
print(f"Optimized route: {route_data['id']}")

# Get analytics
response = requests.get(f'{BASE_URL}/analytics/fleet/')
analytics = response.json()
print(f"Total deliveries: {analytics['total_deliveries']}")
```

## Pagination

All list endpoints support pagination:

```bash
curl "http://localhost:8000/api/locations/?page=1&limit=10"
```

Default page size: 100 items

## Monitoring

Monitor API usage and performance:

```bash
# Check active connections
curl http://localhost:8000/api/health/

# Monitor in real-time
watch -n 5 'curl -s http://localhost:8000/api/fleet/stats/ | jq'
```

---

**API Version**: 1.0.0
**Last Updated**: March 2026
