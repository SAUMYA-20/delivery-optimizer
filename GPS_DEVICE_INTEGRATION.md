# GPS Device Integration Guide

## Overview

The Delivery Optimizer now supports real-time GPS device integration for live vehicle tracking. Connect any GPS-enabled device (smartphone, GPS tracker, IoT device) to track vehicles in real-time on the map.

## Features

- ✅ Real-time GPS data ingestion via REST API
- ✅ Automatic WebSocket broadcasting to connected clients
- ✅ Live map updates with accuracy indicators
- ✅ GPS history tracking (last 100 records)
- ✅ Device connection status monitoring
- ✅ Configurable polling intervals

## Architecture

```
┌─────────────────────────────────────────┐
│   GPS Device / Mobile App / Tracker     │
│  Phone, IoT Device, GPS Tracker, etc.   │
└─────────────────────────────────────────┘
                    │
                    │ HTTP POST
                    │ GPS Data (lat, lon, speed, heading)
                    ▼
┌─────────────────────────────────────────┐
│   POST /api/gps/receive/                │
│   Backend API Endpoint                  │
│   - Validate coordinates                │
│   - Save to VehicleTracking table       │
│   - Broadcast via WebSocket             │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────────┐  ┌──────────────────┐
│   Database       │  │  WebSocket       │
│   (GPS History)  │  │  (Real-time UI)  │
└──────────────────┘  └──────────────────┘
        │                       │
        │                       ▼
        │            ┌──────────────────────┐
        │            │  Frontend Browser    │
        │            │  - Map Updates       │
        │            │  - GPS Status Badge  │
        └────────────│  - History Display   │
                     └──────────────────────┘
```

## Frontend Setup (Browser)

### 1. Connect GPS Device

1. **Open the application** in your browser
2. **Select a vehicle** from the "Active Vehicles" list on the left sidebar
3. **Click the "Connect GPS" button** in Quick Actions
4. **Fill in the modal:**
   - **Device ID**: Enter the device's unique identifier (e.g., IMEI number)
   - **Polling Interval**: Select how often to check for new GPS data (5s, 10s, 15s, 30s, 60s)
5. **Click "Connect Device"**

### 2. Monitor GPS Status

The GPS status indicator shows:
- 🟢 **Green**: Connected and receiving data
- 🔴 **Red**: Connection error
- 🟡 **Yellow**: Connecting...

Real-time data displayed:
- Current latitude/longitude
- Vehicle speed
- GPS accuracy
- Last update timestamp

### 3. Disconnect GPS

Click the **"Disconnect GPS"** button to stop polling and remove the device connection.

## Backend API Endpoints

### 1. Receive GPS Data

**Endpoint:** `POST /api/gps/receive/`

**Purpose:** Primary endpoint for GPS devices to send location data

**Request:**
```json
{
  "vehicle_id": 1,
  "latitude": 40.7425,
  "longitude": -74.0033,
  "speed": 45.5,
  "heading": 125.3,
  "accuracy": 5.0
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "tracking_id": 1234,
  "timestamp": "2024-01-15T10:30:45Z",
  "message": "GPS data received and broadcasted"
}
```

**Validation Rules:**
- `vehicle_id`: Must exist in database
- `latitude`: -90 to +90 degrees
- `longitude`: -180 to +180 degrees
- `speed`: 0 to unlimited (km/h)
- `heading`: 0 to 360 degrees
- `accuracy`: Positive number (meters)

**Error Response (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Invalid latitude: 91.5 (must be between -90 and 90)"
}
```

### 2. Get Vehicle Location History

**Endpoint:** `GET /api/tracking/vehicles/<vehicle_id>/history/`

**Purpose:** Retrieve GPS tracking history for a vehicle

**Response (200 OK):**
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Vehicle-1",
  "total_records": 42,
  "tracking_history": [
    {
      "id": 1234,
      "latitude": 40.7425,
      "longitude": -74.0033,
      "speed": 45.5,
      "heading": 125.3,
      "accuracy": 5.0,
      "timestamp": "2024-01-15T10:30:45Z"
    },
    ...
  ]
}
```

### 3. Get Current Vehicle Location

**Endpoint:** `GET /api/vehicles/<vehicle_id>/current-location/`

**Purpose:** Get the latest GPS position and metadata

**Response (200 OK):**
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Vehicle-1",
  "latitude": 40.7425,
  "longitude": -74.0033,
  "speed": 45.5,
  "heading": 125.3,
  "accuracy": 5.0,
  "timestamp": "2024-01-15T10:30:45Z"
}
```

## Device Implementation Examples

### Example 1: Python Script (GPS Tracker)

```python
import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/gps/receive/"
VEHICLE_ID = 1
DEVICE_ID = "8881234567"
POLL_INTERVAL = 10  # seconds

def get_gps_coordinates():
    """
    Replace this with your actual GPS implementation
    Examples:
    - Read from serial GPS module
    - Query GPS hardware
    - Use geolocation API
    """
    # Mock GPS data (replace with real GPS reading)
    return {
        "latitude": 40.7425 + (0.001 * (time.time() % 10)),
        "longitude": -74.0033 + (0.001 * (time.time() % 10)),
        "speed": 45.5,
        "heading": 125.3,
        "accuracy": 5.0
    }

def send_gps_data():
    """Send GPS data to the backend API"""
    while True:
        try:
            gps_data = get_gps_coordinates()

            payload = {
                "vehicle_id": VEHICLE_ID,
                **gps_data
            }

            response = requests.post(API_URL, json=payload)

            if response.status_code == 201:
                data = response.json()
                print(f"✓ GPS data sent successfully (ID: {data['tracking_id']})")
                print(f"  Location: {gps_data['latitude']}, {gps_data['longitude']}")
            else:
                print(f"✗ Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"✗ Connection error: {e}")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    print(f"Starting GPS tracking for Vehicle {VEHICLE_ID}")
    print(f"Polling interval: {POLL_INTERVAL} seconds")
    print(f"Press Ctrl+C to stop\n")

    try:
        send_gps_data()
    except KeyboardInterrupt:
        print("\nGPS tracking stopped")
```

### Example 2: JavaScript / Node.js (GPS Device)

```javascript
const axios = require('axios');

// Configuration
const API_URL = 'http://localhost:8000/api/gps/receive/';
const VEHICLE_ID = 1;
const POLL_INTERVAL = 10000; // milliseconds

async function getGPSCoordinates() {
    /**
     * Replace this with your actual GPS implementation
     * Examples:
     * - Use react-geolocations (web)
     * - Read from hardware GPS module
     * - Parse NMEA data from serial port
     */
    return {
        latitude: 40.7425 + 0.001 * Math.random(),
        longitude: -74.0033 + 0.001 * Math.random(),
        speed: 45.5 + Math.random() * 10,
        heading: Math.random() * 360,
        accuracy: 5.0
    };
}

async function sendGPSData() {
    try {
        const gpsData = await getGPSCoordinates();

        const payload = {
            vehicle_id: VEHICLE_ID,
            ...gpsData
        };

        const response = await axios.post(API_URL, payload);

        if (response.status === 201) {
            console.log(`✓ GPS data sent (ID: ${response.data.tracking_id})`);
            console.log(`  Location: ${gpsData.latitude.toFixed(4)}, ${gpsData.longitude.toFixed(4)}`);
        }
    } catch (error) {
        console.error(`✗ Error: ${error.message}`);
    }
}

// Start polling
console.log(`Starting GPS tracking for Vehicle ${VEHICLE_ID}`);
console.log(`Polling interval: ${POLL_INTERVAL}ms\n`);

setInterval(sendGPSData, POLL_INTERVAL);
```

### Example 3: cURL (Manual Testing)

```bash
#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api/gps/receive/"
VEHICLE_ID=1

# Send GPS data
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": '${VEHICLE_ID}',
    "latitude": 40.7425,
    "longitude": -74.0033,
    "speed": 45.5,
    "heading": 125.3,
    "accuracy": 5.0
  }'

echo ""
```

### Example 4: Mobile App (React Native / Flutter)

**React Native:**
```javascript
import React, { useEffect, useState } from 'react';
import * as Location from 'expo-location';

export const GPSTracker = ({ vehicleId }) => {
    useEffect(() => {
        let subscription;

        const startTracking = async () => {
            const { status } = await Location.requestForegroundPermissionsAsync();

            if (status === 'granted') {
                subscription = await Location.watchPositionAsync(
                    { accuracy: Location.Accuracy.High, distanceInterval: 10 },
                    async (location) => {
                        const { latitude, longitude } = location.coords;

                        try {
                            await fetch('http://localhost:8000/api/gps/receive/', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    vehicle_id: vehicleId,
                                    latitude,
                                    longitude,
                                    speed: location.coords.speed || 0,
                                    heading: location.coords.heading || 0,
                                    accuracy: location.coords.accuracy || 0
                                })
                            });
                        } catch (error) {
                            console.error('GPS upload error:', error);
                        }
                    }
                );
            }
        };

        startTracking();

        return () => {
            if (subscription) {
                subscription.remove();
            }
        };
    }, [vehicleId]);

    return null; // Background tracking
};
```

## Real-time WebSocket Broadcasting

When GPS data is received via the API, it's automatically broadcasted to all connected WebSocket clients in the tracking group.

**WebSocket Message Format:**
```javascript
{
    "type": "location_update",
    "source": "gps_device",  // Can also be "simulation" or "manual"
    "vehicle_id": 1,
    "latitude": 40.7425,
    "longitude": -74.0033,
    "speed": 45.5,
    "heading": 125.3,
    "timestamp": "2024-01-15T10:30:45Z"
}
```

The frontend automatically:
1. Updates the vehicle marker on the map
2. Refreshes the GPS status indicator
3. Adds point to the tracking polyline
4. Updates vehicle statistics

## Database Schema

### VehicleTracking Table
```sql
CREATE TABLE routes_vehicletracking (
    id INTEGER PRIMARY KEY,
    vehicle_id INTEGER,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    speed DECIMAL(8, 2),
    heading DECIMAL(6, 2),
    accuracy DECIMAL(8, 2),
    source VARCHAR(50),  -- 'gps_device', 'simulation', 'manual'
    timestamp DATETIME,
    created_at DATETIME,
    FOREIGN KEY (vehicle_id) REFERENCES routes_vehicle(id)
);
```

**Source Values:**
- `gps_device`: Raw GPS data from device
- `simulation`: Interpolated position from route simulation
- `manual`: Manually entered location update

## Troubleshooting

### GPS Device Not Showing on Map

1. **Check vehicle is selected** - Make sure you've selected a vehicle from the sidebar
2. **Check API connectivity** - Test endpoint manually with cURL
3. **Check coordinates** - Ensure latitude is -90 to 90 and longitude is -180 to 180
4. **Check WebSocket connection** - Open browser console and look for connection logs

### GPS Status Shows Error

1. **Network connectivity** - Check that backend is running (`python manage.py runserver`)
2. **URL configuration** - Verify `API_BASE` and `WS_BASE` in index.html match your setup
3. **CORS issues** - Check Django CORS settings if running on different domain
4. **Database issues** - Check VehicleTracking table has proper permissions

### Inaccurate GPS Data

1. **Validate coordinates** - Check latitude and longitude ranges
2. **Check accuracy field** - Ensure accuracy value is realistic
3. **Network lag** - Increase polling interval if network is slow
4. **Device limitations** - Some GPS modules have lower accuracy, use accuracy field

## Performance Considerations

### Database Impact
- Each GPS reading creates a new VehicleTracking record
- Last 100 records are kept in memory for quick access
- Consider archiving old records for large fleets

### Network Bandwidth
- Default payload: ~200 bytes per GPS reading
- At 10-second intervals: ~72 KB/hour per vehicle
- 100 vehicles: ~7.2 MB/hour total

### Recommended Configuration
- **Normal delivery**: 30-60 second intervals
- **High-load routes**: 60-120 second intervals
- **Emergency/priority**: 5-10 second intervals

## Integration with Other Features

### GPS Device + Route Simulation
- Run both simultaneously for comparison
- Simulation uses interpolation, GPS is actual location
- Different sources visible in database

### GPS Device + Manual Updates
- Manual updates override GPS for that reading
- Next GPS reading resumes automatic tracking
- Useful for manual corrections

### GPS Device + Notifications
- Integrate with delivery status updates
- Send alerts when GPS deviates from planned route
- Monitor speed violations

## Security Considerations

### Coordinate Validation
- Always validate latitude (-90 to 90) and longitude (-180 to 180)
- Check for NaN and Infinity values
- Reject unrealistic speed values (>500 km/h)

### Device Authentication
- Consider adding API key/token authentication
- Store Device ID securely
- Rate limit GPS updates to prevent spam

### Data Privacy
- Store GPS history with retention policies
- Anonymize old location data
- Ensure compliance with privacy regulations

## API Rate Limiting

Current implementation has no built-in rate limiting. For production:

```python
# Add to views.py
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(1), name='dispatch')
@api_view(['POST'])
def receive_gps_data(request):
    # Implementation
    pass
```

## Future Enhancements

- [ ] Device authentication with API keys
- [ ] Route deviation alerts
- [ ] Geofencing support
- [ ] Battery status monitoring
- [ ] Multi-device fleet management
- [ ] GPS accuracy filtering
- [ ] Historical route playback
- [ ] Mobile app for drivers

## Support and Troubleshooting

**Check Logs:**
```bash
# Terminal where Django server is running
python manage.py runserver

# Browser console (F12 → Console)
# Look for WebSocket connection messages
# Check for GPS polling interval messages
```

**Test API Directly:**
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id": 1, "latitude": 40.7425, "longitude": -74.0033, "speed": 45.5, "heading": 125.3, "accuracy": 5.0}'
```

**Check WebSocket:**
```javascript
// In browser console
console.log(websocket.readyState);  // 1 = connected
websocket.send(JSON.stringify({test: 'message'}));
```

## Next Steps

1. **Test with cURL** - Verify API works with manual requests
2. **Implement GPS script** - Use Python/JavaScript example for your device
3. **Connect device** - Click "Connect GPS" button and select polling interval
4. **Monitor on map** - Watch real-time updates and GPS status
5. **Compare with simulation** - Run both to verify consistency

Happy tracking! 🚀📍
