# Location Update Feature Guide

## Overview

The **Update Location** button allows you to manually update a vehicle's position on the map in real-time. This is useful for:
- Testing GPS tracking without running a full simulation
- Correcting position data
- Manually moving vehicles for testing/demo purposes
- Integration with real GPS devices

---

## How to Use

### Step 1: Select a Vehicle
1. Click on a vehicle in the **Active Vehicles** sidebar
2. The vehicle will be highlighted (yellow background)
3. Its details appear in the **Vehicle Details** panel

### Step 2: Open Update Location Modal
1. Click the **"Update Location"** button in **Quick Actions**
2. A form will appear with pre-filled current location data

### Step 3: Update Coordinates
Fill in the new location information:

| Field | Purpose | Range | Example |
|-------|---------|-------|---------|
| **Vehicle** | Display current vehicle (read-only) | N/A | Van-01 |
| **Latitude** | North-South position | -90 to 90 | 40.7425 |
| **Longitude** | East-West position | -180 to 180 | -74.0033 |
| **Speed** | Current vehicle speed | 0-120 km/h | 50 |
| **Heading** | Direction of travel | 0-360° | 45.5 |

### Step 4: Submit
Click **"Update Location"** button to apply changes

---

## What Happens Behind the Scenes

### 1. Frontend Processing
```javascript
submitUpdateLocation()
  ├─ Validate coordinates
  │  ├─ Latitude: -90° to +90°
  │  └─ Longitude: -180° to +180°
  │
  ├─ Send via WebSocket:
  │  {
  │    type: 'location_update',
  │    latitude: 40.7425,
  │    longitude: -74.0033,
  │    speed: 50,
  │    heading: 45.5
  │  }
  │
  └─ Update local state immediately:
     ├─ Update currentVehicle object
     ├─ Update map marker
     └─ Refresh vehicle details panel
```

### 2. Backend Processing (WebSocket Consumer)
```python
TrackingConsumer.receive_json()
  │
  ├─ Parse incoming message
  │
  ├─ Call handle_location_update()
  │  │
  │  ├─ Extract: lat, lon, speed, heading
  │  │
  │  ├─ Call save_tracking_data()
  │  │  └─ Insert into VehicleTracking table (GPS history)
  │  │
  │  └─ Broadcast via WebSocket channel:
  │     {
  │       type: 'location_update',
  │       data: {
  │         vehicle_id: 1,
  │         latitude: 40.7425,
  │         longitude: -74.0033,
  │         speed: 50,
  │         heading: 45.5,
  │         timestamp: '2026-04-03T12:30:45Z'
  │       }
  │     }
  │
  └─ All WebSocket clients in group receive update
```

### 3. Map Update
```javascript
websocket.onmessage()
  │
  ├─ Parse location_update event
  │
  ├─ Call updateVehicleMarker()
  │  └─ Update Leaflet circle marker position on map
  │
  └─ Vehicle position appears on map immediately
```

### 4. Database State
```sql
-- VehicleTracking table records history
INSERT INTO vehicle_tracking
(vehicle_id, latitude, longitude, speed, heading, accuracy, timestamp)
VALUES
(1, 40.7425, -74.0033, 50.0, 45.5, 10.0, NOW());

-- Vehicle table gets updated
UPDATE vehicles
SET latitude = 40.7425, longitude = -74.0033
WHERE id = 1;
```

---

## Technical Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Update Location Modal                             │  │
│  │    - Input: lat, lon, speed, heading                 │  │
│  │    - Click: "Update Location"                        │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │ 2. Validation                                        │  │
│  │    ✓ Latitude: -90 to 90                             │  │
│  │    ✓ Longitude: -180 to 180                          │  │
│  │    ✓ Speed: 0 to 999                                 │  │
│  │    ✓ Heading: 0 to 360                               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │ 3. Send WebSocket Message                            │  │
│  │    type: 'location_update'                           │  │
│  │    data: {lat, lon, speed, heading}                  │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │ 4. Update UI Immediately                             │  │
│  │    - Move marker on map                              │  │
│  │    - Update vehicle details panel                    │  │
│  │    - Show success alert                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────┬──────────────────────────────────┘
                          │
                    WebSocket Channel
                          │
┌─────────────────────────▼──────────────────────────────────┐
│                        BACKEND                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 5. TrackingConsumer.receive()                        │  │
│  │    - Parse JSON from WebSocket                       │  │
│  │    - Route to handler                                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │ 6. handle_location_update()                          │  │
│  │    - Extract: lat, lon, speed, heading               │  │
│  │    - Validate range                                  │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │ 7. save_tracking_data()                              │  │
│  │    - Insert into VehicleTracking table                │  │
│  │    - Create GPS history record                       │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │ 8. Broadcast via group_send()                        │  │
│  │    - Send to all clients in tracking group           │  │
│  │    - Include timestamp                               │  │
│  │    - Include all tracking data                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────┬──────────────────────────────────┘
                          │
                 Channel Layer Broadcast
                          │
┌─────────────────────────▼──────────────────────────────────┐
│                    ALL CLIENTS                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 9. location_update handler                           │  │
│  │    - Receive broadcasted message                     │  │
│  │    - Update marker position                          │  │
│  │    - Refresh vehicle details                         │  │
│  │    - Display on map                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## WebSocket Protocol

### Client → Server
```json
{
  "type": "location_update",
  "latitude": 40.7425,
  "longitude": -74.0033,
  "speed": 50.5,
  "heading": 45.3
}
```

### Server → All Clients
```json
{
  "type": "location_update",
  "data": {
    "vehicle_id": 1,
    "latitude": 40.7425,
    "longitude": -74.0033,
    "speed": 50.5,
    "heading": 45.3,
    "timestamp": "2026-04-03T12:30:45.123456Z"
  }
}
```

---

## Database Changes

### VehicleTracking Table (New Record)
```sql
INSERT INTO vehicle_tracking (
  id,
  vehicle_id,
  latitude,
  longitude,
  speed,
  heading,
  accuracy,
  timestamp,
  created_at
) VALUES (
  NULL,
  1,
  40.7425,
  -74.0033,
  50.5,
  45.3,
  10.0,
  '2026-04-03T12:30:45.123456Z',
  NOW()
);
```

### Vehicles Table (Updated)
```sql
UPDATE vehicles
SET
  latitude = 40.7425,
  longitude = -74.0033,
  updated_at = NOW()
WHERE id = 1;
```

---

## Error Handling

### Coordinate Validation
```
✓ Latitude: -90 ≤ value ≤ 90
✓ Longitude: -180 ≤ value ≤ 180
✓ Speed: 0 ≤ value ≤ 999 (km/h)
✓ Heading: 0 ≤ value ≤ 360 (degrees)
```

**Error Cases:**
```
1. No vehicle selected
   → "Please select a vehicle first"

2. Invalid latitude
   → "Latitude must be between -90 and 90"

3. Invalid longitude
   → "Longitude must be between -180 and 180"

4. WebSocket not connected
   → "WebSocket not connected. Please select a vehicle."

5. Form submission error
   → "Error updating location: [error message]"
```

---

## Use Cases

### 1. Manual GPS Correction
- Driver reports incorrect position
- Admin updates location manually
- Changes reflect immediately on map

### 2. Testing & Demo
- Demo vehicle movement without simulation
- Test map updates
- Verify tracking functionality

### 3. Integration Testing
- Simulate real GPS device sending locations
- Verify location persistence
- Check map rendering

### 4. Manual Dispatch
- Adjust vehicle position for operational needs
- Reposition vehicles between routes
- Handle exceptional cases

---

## Complementary Features

### Simulation vs Manual Update

| Feature | Simulation | Manual Update |
|---------|-----------|---------------|
| **Use Case** | Full route testing | Single position update |
| **Automation** | Generates interpolated path | Manual entry |
| **Duration** | Continuous (2s intervals) | One-time |
| **Setup** | Requires optimized route | Just latitude/longitude |
| **Realism** | High (follows route) | Basic (direct update) |
| **Start/Stop** | Buttons in UI | Single action |

### Together They Provide:
- ✓ Full route simulation for realistic testing
- ✓ Manual updates for exceptions
- ✓ Real-time GPS history in database
- ✓ Live map visualization
- ✓ Complete testing coverage

---

## Hardware Integration

To connect real GPS devices:

1. **GPS Device sends HTTP/WebSocket**
2. **Backend processes location update**
3. **Uses same WebSocket handler** (`location_update`)
4. **Works with existing map system**

```python
# Example: GPS device integration
@database_sync_to_async
def handle_gps_device_data(self, gps_data):
    """Accept GPS data from external device"""
    latitude = gps_data['lat']
    longitude = gps_data['lon']
    speed = gps_data['spd']  # Speed in km/h
    heading = gps_data['heading']  # Direction

    # Same handler code as manual update
    await self.save_tracking_data(
        latitude, longitude, speed, heading
    )
```

---

## Performance Metrics

- **Update latency:** < 100ms (WebSocket)
- **Database write:** ~5ms per record
- **Map update:** Real-time (Leaflet)
- **Connection overhead:** Minimal (already connected for simulation)
- **Data size per update:** ~150 bytes

---

## Future Enhancements

1. **Batch Updates** - Update multiple vehicles at once
2. **Route Playback** - Upload CSV of GPS points
3. **Geofencing** - Alert when vehicle enters/exits zones
4. **Route History** - Replay past route movements
5. **Accuracy Metrics** - Show GPS accuracy radius
