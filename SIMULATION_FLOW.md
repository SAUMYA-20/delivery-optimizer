# Simulation Flow Explanation

## How the Simulation Works

The simulation allows you to test vehicle movement along an optimized route without real GPS hardware. Here's the complete flow:

### 1. **User Initiates Simulation**
```
UI: Click "Start Sim" button
  ↓
Frontend sends: {type: 'start_simulation', route_id: 123}
  ↓
WebSocket connects to: ws://localhost:8000/ws/tracking/vehicle/{vehicle_id}/
```

### 2. **Backend Receives Start SimulationRequest**
```
TrackingConsumer.handle_start_simulation()
  ↓
└─ Fetch route from database
  ├─ Get all stops in order (RouteStop)
  ├─ Get current vehicle
  └─ Call TrackingService.simulate_vehicle_movement()
```

### 3. **Simulated Points Generation**
The `simulate_vehicle_movement()` function:
- Takes all stops in the route (ordered)
- For each pair of consecutive stops:
  - **Interpolates** intermediate points between them
  - Calculates smooth path from Stop A → Stop B
  - Generates ~5 points per segment with:
    - Interpolated latitude/longitude
    - Vehicle's normal speed (from DB)
    - Heading angle (direction of travel)

**Example:**
```
Route: [Location A] → [Location B] → [Location C]

With num_points=5:
- A to B: 5 interpolated points
- B to C: 5 interpolated points
- Total: 10 simulated movement points
```

### 4. **Movement Simulation Loop**
```
simulate_movement(simulated_points)
  ↓
For each interpolated point:
  ├─ Update vehicle location in database
  ├─ Save VehicleTracking record
  ├─ Broadcast location_update via WebSocket
  ├─ Display on map in real-time
  └─ Wait 2 seconds before next point
```

### 5. **Real-Time Map Updates**
```
Frontend WebSocket receives:
{
  type: 'location_update',
  data: {
    vehicle_id: 1,
    latitude: 40.7425,
    longitude: -74.0033,
    speed: 50,
    heading: 45.3,
    timestamp: '2026-04-03T12:00:00'
  }
}
  ↓
updateVehicleMarker() - Update marker position on Leaflet map
  ↓
Display smooth vehicle movement animation
```

### 6. **Stop Simulation**
```
UI: Click "Stop Sim" button
  ↓
Frontend sends: {type: 'stop_simulation'}
  ↓
Backend sets: self.simulation_active = False
  ↓
Loop breaks and simulation stops
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (index.html)                    │
│  - Leaflet Map                                              │
│  - WebSocket client                                         │
│  - Vehicle marker updates                                   │
└────────────────┬────────────────────────────────────────────┘
                 │ WebSocket
                 │
┌────────────────▼────────────────────────────────────────────┐
│              BACKEND (Django Channels)                       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TrackingConsumer (WebSocket)                        │   │
│  │  - Handles receive_json() from client               │   │
│  │  - Manages simulation state                         │   │
│  │  - Broadcasts location updates                      │   │
│  └──────────────┬──────────────────────────────────────┘   │
│                 │                                            │
│  ┌──────────────▼──────────────────────────────────────┐   │
│  │  TrackingService (Business Logic)                   │   │
│  │  - simulate_vehicle_movement()      [Generate path] │   │
│  │  - record_tracking_data()           [Save to DB]    │   │
│  │  - get_closest_route_stop()         [Tracking]      │   │
│  └──────────────┬──────────────────────────────────────┘   │
│                 │                                            │
│  ┌──────────────▼──────────────────────────────────────┐   │
│  │  Models (Database)                                   │   │
│  │  - Route (with RouteStops)                          │   │
│  │  - Vehicle                                          │   │
│  │  - VehicleTracking (GPS history)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow During Simulation

```
START SIMULATION
  │
  ├──► Get Route: SELECT * FROM routes WHERE id = route_id
  ├──► Get Vehicle: SELECT * FROM vehicles WHERE id = vehicle_id
  ├──► Get Stops: SELECT * FROM route_stops WHERE route_id = route_id
  │
  ├──► GENERATE INTERPOLATED POINTS
  │    ├─ Stop A (40.7425, -74.0033)
  │    ├─ Intermediate Point 1 (40.7430, -74.0030)
  │    ├─ Intermediate Point 2 (40.7435, -74.0028)
  │    ├─ ... (num_points total)
  │    └─ Stop B (40.7450, -74.0020)
  │
  └──► FOR EACH POINT (every 2 seconds):
       ├─ Save: INSERT INTO vehicle_tracking (...)
       ├─ Broadcast:
       │  {
       │    type: 'location_update',
       │    data: {lat, lon, speed, heading, timestamp}
       │  }
       └─ Frontend receives and updates map marker
```

---

## Key Components

### TrackingConsumer (Async WebSocket)
- **Runs on:** Django Channels (async)
- **Handles:** WebSocket connections per vehicle
- **Methods:**
  - `connect()` - Join WebSocket group
  - `receive()` - Parse incoming JSON messages
  - `handle_start_simulation()` - Initiate simulation
  - `simulate_movement()` - Loop through points with delays
  - `save_tracking_data()` - Write to database
  - `location_update()` - Broadcast to all listeners

### TrackingService (Sync Service)
- **Runs on:** Django main thread (database operations)
- **Methods:**
  - `simulate_vehicle_movement(vehicle, route, num_points=5)`
    - Interpolates path between all route stops
    - Returns list of movement points with: lat, lon, speed, heading
  - `record_tracking_data(vehicle, lat, lon, speed, heading)`
    - Saves location to VehicleTracking table

### Models
- **Route** - Contains multiple RouteStops
- **RouteStop** - Single delivery location in order
- **Vehicle** - Has current lat/lon
- **VehicleTracking** - GPS history (one record per update)

---

## Interpolation Algorithm

```
For each consecutive pair of stops:

  START = (stop_A.lat, stop_A.lon)
  END   = (stop_B.lat, stop_B.lon)

  For point_num in range(num_points):
    t = point_num / num_points   // 0 to 1 (0% to 100%)

    lat = START_LAT + t * (END_LAT - START_LAT)
    lon = START_LON + t * (END_LON - START_LON)

    heading = atan2(lon_delta, lat_delta)  // Direction angle

    result: {lat, lon, speed, heading}
```

**Example with num_points=5:**
- Point 0: 0% of the way (at Start)
- Point 1: 20% of the way
- Point 2: 40% of the way
- Point 3: 60% of the way
- Point 4: 80% of the way
- Point 5: 100% of the way (at End)

---

## WebSocket Messages

### Client → Server
```javascript
// Start simulation
{
  type: 'start_simulation',
  route_id: 123
}

// Update location manually
{
  type: 'location_update',
  latitude: 40.7425,
  longitude: -74.0033,
  speed: 50,
  heading: 45
}

// Stop simulation
{
  type: 'stop_simulation'
}

// Get current status
{
  type: 'get_status'
}
```

### Server → Client
```javascript
// Simulation started confirmation
{
  type: 'simulation_started',
  vehicle_id: 1,
  total_points: 10
}

// Location update (every 2 seconds during simulation)
{
  type: 'location_update',
  data: {
    vehicle_id: 1,
    latitude: 40.7430,
    longitude: -74.0030,
    speed: 50,
    heading: 45.3,
    timestamp: '2026-04-03T12:00:05Z'
  }
}

// Simulation stopped
{
  type: 'simulation_stopped',
  vehicle_id: 1
}

// Vehicle status
{
  type: 'vehicle_status',
  data: {
    id: 1,
    name: 'Van-01',
    latitude: 40.7425,
    longitude: -74.0033,
    status: 'active',
    speed: 50,
    capacity: 50,
    current_load: 15
  }
}

// Errors
{
  type: 'error',
  message: 'Simulation already running'
}
```

---

## Performance Notes

- **Update frequency:** 2 seconds (configurable in `simulate_movement()`)
- **Interpolation points:** 5 per stop pair (configurable in `get_simulated_points()`)
- **Async processing:** All WebSocket operations are non-blocking
- **Database writes:** Each update saves to VehicleTracking table
- **Broadcast:** Each update sent to all WebSocket clients subscribed to that vehicle

---

## Limitations & Improvements

**Current Limitations:**
- ✓ Fixed interpolation (could add curves/bezier for realism)
- ✓ Fixed speed (could vary speed based on turn angles)
- ✓ No traffic simulation
- ✓ No real-time road data

**Possible Improvements:**
- Add realistic movement curves using Catmull-Rom splines
- Vary speed based on angles/turns
- Add acceleration/deceleration phases
- Use real routing distances (from OSRM API)
- Simulate realistic GPS noise
