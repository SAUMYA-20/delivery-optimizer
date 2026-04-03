# GPS Device Integration - Quick Test Guide

## Step-by-Step Testing

### Step 1: Verify Backend is Running

```bash
# Terminal 1: Start Django server
cd /home/saumya/delivery-optimizer
python manage.py runserver
```

Expected output:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 2: Open Application

1. Open browser: `http://localhost:8000`
2. You should see the delivery map with vehicles and locations

### Step 3: Test GPS API Endpoint (Manual)

In a new terminal:

```bash
# Terminal 2: Test GPS data ingestion
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 40.7425,
    "longitude": -74.0033,
    "speed": 45.5,
    "heading": 125.3,
    "accuracy": 5.0
  }'
```

Expected response:
```json
{
  "status": "success",
  "tracking_id": 1,
  "timestamp": "2024-01-15T10:30:45.123Z",
  "message": "GPS data received and broadcasted"
}
```

### Step 4: Test GPS History Endpoint

```bash
# Get tracking history for vehicle 1
curl -X GET http://localhost:8000/api/tracking/vehicles/1/history/ \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Vehicle-1",
  "total_records": 1,
  "tracking_history": [
    {
      "id": 1,
      "latitude": 40.7425,
      "longitude": -74.0033,
      "speed": 45.5,
      "heading": 125.3,
      "accuracy": 5.0,
      "timestamp": "2024-01-15T10:30:45.123Z"
    }
  ]
}
```

### Step 5: Test Current Location Endpoint

```bash
# Get current location for vehicle 1
curl -X GET http://localhost:8000/api/vehicles/1/current-location/ \
  -H "Content-Type: application/json"
```

Expected response:
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Vehicle-1",
  "latitude": 40.7425,
  "longitude": -74.0033,
  "speed": 45.5,
  "heading": 125.3,
  "accuracy": 5.0,
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

### Step 6: Test Frontend GPS Connection

1. **Select a vehicle** from the left sidebar under "Active Vehicles"
2. **Click "Connect GPS" button** in Quick Actions
3. **Fill the modal:**
   - Device ID: `GPS-TEST-DEVICE-001`
   - Polling Interval: `10 seconds`
4. **Click "Connect Device"**

Expected result:
- GPS status indicator appears (yellow, then green when data arrives)
- "Connect GPS" button changes to "Disconnect GPS"
- Status shows: GPS: Connected (GPS-TEST-DEVICE-001)

### Step 7: Send Real GPS Data from Terminal

Keep the GPS connection active in the browser, then in terminal:

```bash
# Send GPS data update
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 40.7450,
    "longitude": -74.0060,
    "speed": 52.3,
    "heading": 145.5,
    "accuracy": 4.5
  }'
```

Expected result in browser:
- Vehicle marker moves to new location on map
- GPS status updates with new coordinates
- Speed shows 52.3 km/h
- Timestamp updates to current time

### Step 8: Test GPS Polling Loop (Python)

```bash
# Terminal 3: Run continuous GPS simulation
python3 << 'EOF'
import requests
import time
import random

API_URL = "http://localhost:8000/api/gps/receive/"
VEHICLE_ID = 1

print("Starting GPS polling simulation...")
print("Watch the map update in real-time!\n")

base_lat, base_lon = 40.7425, -74.0033

for i in range(10):  # Send 10 updates
    try:
        # Simulate moving vehicle
        lat = base_lat + 0.001 * random.random()
        lon = base_lon + 0.001 * random.random()
        speed = 30 + random.randint(0, 30)
        heading = random.randint(0, 360)

        payload = {
            "vehicle_id": VEHICLE_ID,
            "latitude": lat,
            "longitude": lon,
            "speed": speed,
            "heading": heading,
            "accuracy": random.uniform(3, 10)
        }

        response = requests.post(API_URL, json=payload)

        if response.status_code == 201:
            data = response.json()
            print(f"✓ Update {i+1}: Lat {lat:.4f}, Lon {lon:.4f}, Speed {speed} km/h")
        else:
            print(f"✗ Error: {response.status_code}")

        time.sleep(2)  # Wait 2 seconds between updates
    except Exception as e:
        print(f"✗ Connection error: {e}")
        break

print("\nGPS polling simulation complete!")
EOF
```

Expected output:
```
Starting GPS polling simulation...
Watch the map update in real-time!

✓ Update 1: Lat 40.7431, Lon -74.0038, Speed 45 km/h
✓ Update 2: Lat 40.7433, Lon -74.0041, Speed 52 km/h
✓ Update 3: Lat 40.7438, Lon -74.0045, Speed 38 km/h
...
GPS polling simulation complete!
```

### Step 9: Verify Database Records

```bash
# Terminal 4: Check database
cd /home/saumya/delivery-optimizer
python manage.py dbshell
```

In SQLite console:
```sql
-- Check latest tracking records
SELECT id, vehicle_id, latitude, longitude, speed, heading, accuracy, source, timestamp
FROM routes_vehicletracking
WHERE vehicle_id = 1
ORDER BY created_at DESC
LIMIT 10;

-- Check total GPS records
SELECT COUNT(*) FROM routes_vehicletracking WHERE source = 'gps_device';
```

Expected: Shows all GPS records you sent

### Step 10: Test Error Cases

**Invalid Latitude:**
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 91.0,
    "longitude": -74.0033,
    "speed": 45.5,
    "heading": 125.3,
    "accuracy": 5.0
  }'
```

Expected: 400 Bad Request with error message

**Invalid Longitude:**
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 40.7425,
    "longitude": 181.0,
    "speed": 45.5,
    "heading": 125.3,
    "accuracy": 5.0
  }'
```

Expected: 400 Bad Request with error message

**Non-existent Vehicle:**
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 9999,
    "latitude": 40.7425,
    "longitude": -74.0033,
    "speed": 45.5,
    "heading": 125.3,
    "accuracy": 5.0
  }'
```

Expected: 400 Bad Request - Vehicle not found

## Monitoring

### Browser Console
Open Developer Tools (F12) and check Console tab for:
- WebSocket connection logs
- GPS polling interval messages
- Map update notifications

### Django Server Logs
Check the terminal where Django is running for:
- POST requests to `/api/gps/receive/`
- WebSocket broadcasts to tracking groups
- Any database errors

## Performance Checklist

- [ ] Vehicle marker updates within 1 second of GPS send
- [ ] GPS status shows green indicator when connected
- [ ] Browser doesn't lag with continuous data
- [ ] Multiple GPS updates stack correctly on polyline
- [ ] History shows all sent GPS points
- [ ] Disconnect button works and stops polling

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connect GPS" button is grayed out | Select a vehicle first from sidebar |
| GPS status shows "Error" | Check backend is running and API is accessible |
| Vehicle doesn't move on map | Check GPS data is being sent correctly with valid coordinates |
| WebSocket not connecting | Verify Django server is running and WS_BASE URL is correct |
| "Vehicle not found" error | Make sure vehicle_id matches an actual vehicle in database |

## Next: Real Device Integration

Once testing is complete, you can connect a real GPS device:

1. **Set up your device** to send HTTP POST requests to `/api/gps/receive/`
2. **Format GPS data** as shown in examples
3. **Click "Connect GPS"** in frontend with your device ID
4. **Monitor in real-time** on the map

See `GPS_DEVICE_INTEGRATION.md` for device implementation examples.

---

## Complete Test Scenario

**Estimated time: 5-10 minutes**

1. **Terminal 1**: Start Django server
2. **Terminal 2**: Run GPS polling Python script
3. **Browser**: Open http://localhost:8000
4. **Browser**: Select vehicle → Connect GPS → Watch updates
5. **Terminal 2**: Observe successful API responses
6. **Browser Console**: Observe WebSocket messages
7. **Database**: Verify GPS records saved

**Success Criteria:**
- ✅ GPS status shows "Connected"
- ✅ Vehicle moves on map with each GPS update
- ✅ Status shows lat/lon/speed/accuracy
- ✅ 10+ GPS records visible in history
- ✅ No errors in browser console or Django logs

Enjoy live GPS tracking! 🚀📍
