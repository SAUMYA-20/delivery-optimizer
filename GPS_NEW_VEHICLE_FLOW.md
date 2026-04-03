# GPS Device Connection Guide - New Vehicle Creation Flow

## New Flow: Create Vehicle via GPS Device

### Step 1: Open GPS Connection Modal
1. Click **"🔌 Connect GPS"** button in Quick Actions
2. No need to select a vehicle first!

### Step 2: Fill GPS Connection Form
- **Vehicle Name**: Enter the name for your vehicle (e.g., "Delivery Van 01")
- **Device ID**: Enter your GPS device identifier (e.g., "8881234567" or "GPS-TRUCK-001")
- **Polling Interval**: Select update frequency (5s, 10s, 15s, 30s, 60s)

### Step 3: Device Sends GPS Data

Your GPS device must send data to:
```
POST http://localhost:8000/api/gps/receive/
```

**Request Format** (Important: include `vehicle_id` and `vehicle_name`):
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Delivery Van 01",
  "latitude": 28.6315,
  "longitude": 77.2196,
  "speed": 45.5,
  "heading": 125.3,
  "accuracy": 5.0
}
```

**Fields Explained:**
| Field | Type | Description |
|-------|------|-------------|
| `vehicle_id` | integer | Unique vehicle ID (can be device IMEI) |
| `vehicle_name` | string | Custom name for the vehicle (optional, uses vehicle_id if not provided) |
| `latitude` | float | -90 to 90 degrees |
| `longitude` | float | -180 to 180 degrees |
| `speed` | float | km/h (default: 0.0) |
| `heading` | float | 0-360 degrees (default: 0.0) |
| `accuracy` | float | ±meters (default: 10.0) |

### Step 4: System Auto-Creates Vehicle

When the device sends its first GPS signal:
1. ✅ System creates vehicle with `vehicle_name`
2. ✅ Vehicle appears in Active Vehicles list
3. ✅ Vehicle marked on map with marker
4. ✅ Vehicle auto-selected (highlighted on map)
5. ✅ GPS status shows 🟢 Connected

### Step 5: Real-time Tracking & Route Optimization

Once vehicle is created and tracked:
1. 📍 Vehicle marker updates every N seconds
2. 🚗 Speed, heading, accuracy displayed live
3. 🛣️ Click "🚀 Optimize Route" to create delivery routes
4. 📊 View analytics and metrics

---

## Testing: Simulate GPS Device

### Option 1: cURL (One-time test)

```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 100,
    "vehicle_name": "Test Van",
    "latitude": 28.6315,
    "longitude": 77.2196,
    "speed": 45,
    "heading": 120,
    "accuracy": 5
  }'
```

Then in the GPS modal:
- Device ID: `100`
- Vehicle Name: `Test Van`
- Connect and watch vehicle appear!

### Option 2: Python Script (Continuous)

```python
#!/usr/bin/env python3
import requests
import time

API_URL = "http://localhost:8000/api/gps/receive/"
VEHICLE_ID = 999
VEHICLE_NAME = "My Delivery Vehicle"

# Starting location (Delhi)
base_lat = 28.6315
base_lon = 77.2196

print(f"Starting GPS simulation...")
print(f"Vehicle ID: {VEHICLE_ID}")
print(f"Vehicle Name: {VEHICLE_NAME}")
print(f"Sending to: {API_URL}\n")

for i in range(20):
    import random

    # Simulate movement
    latitude = base_lat + random.uniform(-0.01, 0.01)
    longitude = base_lon + random.uniform(-0.01, 0.01)
    speed = random.uniform(30, 60)
    heading = random.uniform(0, 360)

    payload = {
        "vehicle_id": VEHICLE_ID,
        "vehicle_name": VEHICLE_NAME,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "heading": heading,
        "accuracy": random.uniform(3, 8)
    }

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 201:
            print(f"✓ Signal {i+1}: Lat {latitude:.4f}, Lon {longitude:.4f}, Speed {speed:.1f} km/h")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ Connection error: {e}")

    time.sleep(5)  # Send every 5 seconds

print("\nGPS simulation complete!")
```

### Option 3: JavaScript (Browser Console)

```javascript
const API = 'http://localhost:8000/api/gps/receive/';
const VEHICLE_ID = 777;
const VEHICLE_NAME = 'Web Test Vehicle';

setInterval(async () => {
    const lat = 28.6315 + Math.random() * 0.01;
    const lon = 77.2196 + Math.random() * 0.01;

    try {
        const res = await fetch(API, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                vehicle_id: VEHICLE_ID,
                vehicle_name: VEHICLE_NAME,
                latitude: lat,
                longitude: lon,
                speed: Math.random() * 50 + 20,
                heading: Math.random() * 360,
                accuracy: 5
            })
        });
        console.log('GPS sent:', res.status);
    } catch(e) {
        console.error('Error:', e);
    }
}, 3000);  // Every 3 seconds
```

---

## Complete Test Workflow

### 1. **Start Backend**
```bash
cd /home/saumya/delivery-optimizer
python manage.py runserver
```

### 2. **Browser: Open GPS Modal**
```
http://localhost:8000
Click "🔌 Connect GPS"
```

### 3. **Form: Enter Details**
- Vehicle Name: `Demo Truck 01`
- Device ID: `DEMO-001`
- Polling Interval: `10 seconds`
- Click "Connect Device"

### 4. **Terminal: Send GPS Data**
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "DEMO-001",
    "vehicle_name": "Demo Truck 01",
    "latitude": 28.6315,
    "longitude": 77.2196,
    "speed": 48,
    "heading": 180,
    "accuracy": 4.5
  }'
```

### 5. **Browser: Watch Magic Happen**
- ✅ Vehicle appears in Active Vehicles list
- ✅ Marker appears on map
- ✅ GPS status turns 🟢 green
- ✅ Shows coordinates, speed, accuracy
- ✅ Timestamp updates

### 6. **Optimize Route**
- Click vehicle if not auto-selected
- Click "🚀 Optimize Route"
- Select locations to deliver
- See optimized path on map

---

## Response Values

### Success Response (201 Created)
```json
{
  "status": "success",
  "tracking_id": 12345,
  "timestamp": "2026-04-03T10:30:45.123Z",
  "message": "GPS data received and broadcasted"
}
```

### Error Response (400 Bad Request)
```json
{
  "status": "error",
  "message": "Latitude must be between -90 and 90"
}
```

---

## Real GPS Device Integration

### Mobile App (React Native)
```javascript
import * as Location from 'expo-location';

const trackVehicle = async () => {
  const { status } = await Location.requestForegroundPermissionsAsync();

  if (status === 'granted') {
    await Location.watchPositionAsync(
      { accuracy: Location.Accuracy.High },
      async (loc) => {
        await fetch('http://your-server.com/api/gps/receive/', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            vehicle_id: deviceId,
            vehicle_name: "Mobile Vehicle",
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
            speed: loc.coords.speed || 0,
            heading: loc.coords.heading || 0,
            accuracy: loc.coords.accuracy
          })
        });
      }
    );
  }
};
```

### GPS Tracker Hardware
```python
import requests
import serial
import time

def parse_gps_data(gps_string):
    # Parse your GPS device format (NMEA, etc.)
    # Return: lat, lon, speed, heading
    pass

ser = serial.Serial('/dev/ttyUSB0', 9600)  # GPS hardware port

while True:
    gps_data = ser.readline()
    lat, lon, speed, heading = parse_gps_data(gps_data)

    requests.post('http://localhost:8000/api/gps/receive/', json={
        'vehicle_id': 'GPS-HW-001',
        'vehicle_name': 'Hardware Tracker',
        'latitude': lat,
        'longitude': lon,
        'speed': speed,
        'heading': heading,
        'accuracy': 5
    })

    time.sleep(30)
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Vehicle doesn't appear | Check GPS device sent data with correct `vehicle_id` and `vehicle_name` |
| 400 Bad Request error | Verify latitude (-90 to 90) and longitude (-180 to 180) |
| GPS status shows error | Check backend running, verify API URL |
| Vehicle name is empty | Device didn't send `vehicle_name` - provide in modal or request |
| Can't optimize route | Vehicle must be selected; click vehicle in sidebar first |

---

## Next Steps

1. ✅ Enter GPS device details in modal
2. ✅ Device sends GPS data with vehicle_name
3. ✅ Vehicle auto-created and mapped
4. ✅ Real-time tracking starts
5. ✅ Optimize delivery routes
6. ✅ Monitor in real-time on map

**Ready to track! 🚀📍**
