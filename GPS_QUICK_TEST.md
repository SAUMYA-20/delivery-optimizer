# GPS Device - Quick Integration Guide

## ⚠️ Critical: Device Must Use Matching Vehicle ID

When connecting GPS device in the app, you enter:
- **Device ID**: `354382376771865` (or your device's unique ID)
- **Vehicle Name**: `Van 27` (or your vehicle name)

The GPS device **MUST** send GPS data with the **same device ID as vehicle_id**:

```json
{
  "vehicle_id": 354382376771865,
  "vehicle_name": "Van 27",
  "latitude": 28.6315,
  "longitude": 77.2196,
  "speed": 45,
  "heading": 120,
  "accuracy": 5
}
```

⚠️ **IMPORTANT**: The `vehicle_id` in GPS request must match the Device ID in the modal!

---

## How It Works

### Step 1: Connect GPS Device
```
App: Connect GPS Modal
├─ Vehicle Name: "Van 27"
├─ Device ID: "354382376771865"
└─ Polling Interval: "5 seconds"

⏳ Status shows: "GPS: Waiting for first signal (354382376771865)"
```

### Step 2: Device Sends GPS Data
```
GPS Device sends to: POST /api/gps/receive/

{
  "vehicle_id": 354382376771865,  ← MUST match Device ID from modal!
  "vehicle_name": "Van 27",
  "latitude": 28.6315,
  "longitude": 77.2196,
  "speed": 45,
  "heading": 120,
  "accuracy": 5
}
```

### Step 3: System Creates Vehicle
```
Backend:
✓ Receives GPS data
✓ Checks: does vehicle with id=354382376771865 exist?
✓ NO → Auto-creates: Vehicle(id=354382376771865, name="Van 27")
✓ Saves GPS tracking record
✓ Broadcasts via WebSocket
```

### Step 4: Frontend Detects Vehicle
```
Frontend polling (every 5s):
✓ GET /api/vehicles/354382376771865/current-location/
✓ Response: 200 OK with coordinates, speed, accuracy
✓ Updates status to: 🟢 "GPS: Connected"
✓ Shows: coordinates, speed, accuracy, timestamp
✓ Auto-selects vehicle
✓ Marks on map
```

---

## Testing: Send GPS Data

### Option 1: cURL (Immediate Test)

```bash
# Match the Device ID and Vehicle Name from your modal!
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 354382376771865,
    "vehicle_name": "Van 27",
    "latitude": 28.6315,
    "longitude": 77.2196,
    "speed": 45,
    "heading": 120,
    "accuracy": 5
  }'
```

**Expected Result**: 201 Created

### Option 2: Python Script

```python
#!/usr/bin/env python3
import requests
import time
import random

# ⚠️ IMPORTANT: Use same Device ID as in app modal!
DEVICE_ID = 354382376771865
VEHICLE_NAME = "Van 27"
API_URL = "http://localhost:8000/api/gps/receive/"

base_lat = 28.6315
base_lon = 77.2196

print(f"Sending GPS data for: {DEVICE_ID} ({VEHICLE_NAME})")
print(f"API: {API_URL}\n")

for i in range(10):
    lat = base_lat + random.uniform(-0.01, 0.01)
    lon = base_lon + random.uniform(-0.01, 0.01)
    speed = random.uniform(30, 60)

    payload = {
        "vehicle_id": DEVICE_ID,              # MUST match Device ID!
        "vehicle_name": VEHICLE_NAME,
        "latitude": lat,
        "longitude": lon,
        "speed": speed,
        "heading": random.uniform(0, 360),
        "accuracy": random.uniform(3, 8)
    }

    try:
        response = requests.post(API_URL, json=payload)
        print(f"✓ Signal {i+1}: {response.status_code} - Lat: {lat:.4f}, Speed: {speed:.1f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    time.sleep(2)

print("\nDone! Check app for real-time updates.")
```

### Option 3: Real GPS Device (Android App)

```javascript
import React, { useEffect } from 'react';
import * as Location from 'expo-location';

const GPSTracker = ({ deviceId, vehicleName }) => {
  useEffect(() => {
    const startTracking = async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();

      if (status === 'granted') {
        await Location.watchPositionAsync(
          { accuracy: Location.Accuracy.High },
          async (location) => {
            await fetch('http://your-server.com/api/gps/receive/', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                vehicle_id: deviceId,          // MUST match Device ID!
                vehicle_name: vehicleName,
                latitude: location.coords.latitude,
                longitude: location.coords.longitude,
                speed: location.coords.speed || 0,
                heading: location.coords.heading || 0,
                accuracy: location.coords.accuracy
              })
            });
          }
        );
      }
    };

    startTracking();
  }, [deviceId, vehicleName]);

  return null;
};

export default GPSTracker;
```

---

## Complete Workflow

### 1. Start Backend
```bash
cd /home/saumya/delivery-optimizer
python manage.py runserver
```

### 2. Open App
```
http://localhost:8000
```

### 3. Click "🔌 Connect GPS"
Fill the form:
```
Vehicle Name: Van 27
Device ID: 354382376771865
Polling Interval: 5 seconds
```

### 4. Status Shows
```
🟡 GPS: Waiting for first signal (354382376771865)
🏷️ Vehicle: Van 27
⏱ Polling every 5s...
```

### 5. Send GPS Data (from device or cURL)
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 354382376771865,
    "vehicle_name": "Van 27",
    "latitude": 28.6315,
    "longitude": 77.2196,
    "speed": 45,
    "heading": 120,
    "accuracy": 5
  }'
```

### 6. Watch Magic! ✨
- ✅ Status turns 🟢 GREEN
- ✅ Shows coordinates, speed, accuracy
- ✅ Vehicle marked on map
- ✅ Auto-selected for route optimization

### 7. Optimize Route
```
Click "🚀 Optimize Route"
→ Select delivery locations
→ See optimized path on map
→ Monitor real-time tracking!
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Status stuck on yellow "Waiting..." | Device hasn't sent GPS data yet. Make sure `vehicle_id` in request matches Device ID in modal! |
| 404 Vehicle Not Found | Device sent GPS data with wrong `vehicle_id`. Must match Device ID from modal. |
| 400 Bad Coordinates | Latitude not -90 to 90, or longitude not -180 to 180 |
| Status shows red "Error" | Backend not running or polling error. Check server logs. |
| Vehicle name wrong | Device sent different `vehicle_name` than modal. Names must match or use what device sends. |

---

## Key Points

✅ **Device ID in modal** = `vehicle_id` in GPS request
✅ **Vehicle Name in modal** = `vehicle_name` in GPS request
✅ **Polling starts immediately**, waiting for first GPS signal
✅ **Once device sends data**, vehicle auto-created and marked on map
✅ **Status changes from yellow** (waiting) **to green** (connected) when vehicle found

---

**Send GPS data with correct vehicle_id and you'll see real-time tracking! 🚀📍**
