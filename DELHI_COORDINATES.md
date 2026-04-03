# Delhi Delivery Optimization - Coordinates Reference

## Map Center & Zoom
- **Center**: 28.6139° N, 77.2090° E (Central Delhi)
- **Zoom Level**: 11 (Good for viewing entire delivery area)

---

## 🚗 Vehicle Starting Positions

| Vehicle | Name | Latitude | Longitude | Status | Capacity | Driver |
|---------|------|----------|-----------|--------|----------|--------|
| Van-01 | Central Delhi | 28.6315 | 77.2196 | Idle | 50 units | driver1 |
| Truck-01 | Gurugram/Cyber City | 28.4595 | 77.1046 | Active | 100 units | driver2 |
| Bike-01 | Hauz Khas | 28.5494 | 77.1906 | Idle | 20 units | — |
| Cargo-01 | Noida City Centre | 28.5921 | 77.3971 | Idle | 75 units | — |

---

## 📍 Delivery Locations

### 1. Connaught Place (Central Delhi Hub)
- **Latitude**: 28.6315
- **Longitude**: 77.2196
- **Address**: Connaught Place, New Delhi
- **Type**: Premium retail/commercial hub
- **Distance from center**: ~0 km (City center)

### 2. Cyber City Gurugram (Corporate Hub)
- **Latitude**: 28.4595
- **Longitude**: 77.1046
- **Address**: DLF Cyber City, Gurugram
- **Type**: IT/Corporate parks
- **Distance from center**: ~18 km SW

### 3. Noida City Centre (Eastern Hub)
- **Latitude**: 28.5921
- **Longitude**: 77.3971
- **Address**: Noida City Centre, Noida
- **Type**: Shopping & commercial center
- **Distance from center**: ~16 km E

### 4. Hauz Khas (South Delhi Hub)
- **Latitude**: 28.5494
- **Longitude**: 77.1906
- **Address**: Hauz Khas, South Delhi
- **Type**: Residential/retail area
- **Distance from center**: ~7 km S

### 5. Aerocity (Premium Commercial)
- **Latitude**: 28.5689
- **Longitude**: 77.1386
- **Address**: Aerocity, New Delhi
- **Type**: Hotels, offices, shopping
- **Distance from center**: ~6 km SE

### 6. Defence Colony (South Delhi Residential)
- **Latitude**: 28.5657
- **Longitude**: 77.2325
- **Address**: Defence Colony, South Delhi
- **Type**: Residential & retail
- **Distance from center**: ~7 km S

### 7. Chandni Chowk (Old Delhi)
- **Latitude**: 28.6505
- **Longitude**: 77.2303
- **Address**: Chandni Chowk, Old Delhi
- **Type**: Historic market/commercial
- **Distance from center**: ~3 km N

### 8. Lajpat Nagar (South Delhi Market)
- **Latitude**: 28.5681
- **Longitude**: 77.2500
- **Address**: Lajpat Nagar, South Delhi
- **Type**: Market & shopping district
- **Distance from center**: ~5 km S

---

## 📐 Approximate Distances Between Hubs

| From | To | Distance | Approx Time (30 km/h) |
|------|-----|----------|----------------------|
| Connaught Place | Hauz Khas | 8 km | 16 min |
| Connaught Place | Defence Colony | 8 km | 16 min |
| Connaught Place | Lajpat Nagar | 6 km | 12 min |
| Connaught Place | Chandni Chowk | 3 km | 6 min |
| Connaught Place | Aerocity | 6 km | 12 min |
| Hauz Khas | Defence Colony | 2 km | 4 min |
| Hauz Khas | Lajpat Nagar | 3 km | 6 min |
| Connaught Place | Gurugram (Cyber City) | 18 km | 30-45 min |
| Connaught Place | Noida | 16 km | 30-45 min |

---

## 🎯 Region Coverage

### South Delhi (Premium Area)
- Hauz Khas (28.5494, 77.1906)
- Defence Colony (28.5657, 77.2325)
- Lajpat Nagar (28.5681, 77.2500)
- ✅ Ideal for: High-value deliveries, retail
- 🚗 Best vehicle: Van-01, Bike-01

### Central Delhi (Core Business)
- Connaught Place (28.6315, 77.2196)
- Chandni Chowk (28.6505, 77.2303)
- ✅ Ideal for: Commercial, offices
- 🚗 Best vehicle: Van-01

### Airport & Premium
- Aerocity (28.5689, 77.1386)
- ✅ Ideal for: Corporate, hotels
- 🚗 Best vehicle: Van-01, Cargo-01

### Corporate Hub
- Cyber City, Gurugram (28.4595, 77.1046)
- ✅ Ideal for: IT companies, large orders
- 🚗 Best vehicle: Truck-01

### Eastern Hub
- Noida City Centre (28.5921, 77.3971)
- ✅ Ideal for: Retail, commercial
- 🚗 Best vehicle: Cargo-01

---

## 🗺️ Getting Started

### 1. Reset Database with New Coordinates
```bash
cd /home/saumya/delivery-optimizer

# Delete old data
python manage.py shell
>>> from routes.models import Vehicle, Location, Route, VehicleTracking
>>> Vehicle.objects.all().delete()
>>> Location.objects.all().delete()
>>> Route.objects.all().delete()
>>> VehicleTracking.objects.all().delete()
>>> exit()

# Reload seed data
python manage.py shell < seed_data.py
```

### 2. Start Server
```bash
python manage.py runserver
```

### 3. Open Map
```
http://localhost:8000
```
The map will now center on Delhi, showing all vehicles and locations!

---

## 💡 Coordinate Ranges

### Valid Latitude for Delhi
- **Min**: 28.40° (South boundary)
- **Max**: 28.70° (North boundary)
- **Current vehicles**: 28.46 - 28.63

### Valid Longitude for Delhi
- **Min**: 76.80° (West boundary)
- **Max**: 77.50° (East boundary)
- **Current vehicles**: 77.10 - 77.40

---

## 🔍 Quick Location Lookup

```bash
# From your browser:
curl http://localhost:8000/api/locations/

# Expected response:
{
  "results": [
    {
      "id": 1,
      "name": "Connaught Place",
      "latitude": 28.6315,
      "longitude": 77.2196,
      "address": "Connaught Place, New Delhi"
    },
    ...
  ]
}
```

---

## 🎮 Testing Routes

### Route 1: South Delhi Circuit
- Start: Connaught Place (28.6315, 77.2196)
- Stop 1: Hauz Khas (28.5494, 77.1906)
- Stop 2: Defence Colony (28.5657, 77.2325)
- Stop 3: Lajpat Nagar (28.5681, 77.2500)
- Total Distance: ~15-18 km
- Estimated Time: 45-60 minutes

### Route 2: Corporate Hub
- Start: Connaught Place (28.6315, 77.2196)
- Stop 1: Aerocity (28.5689, 77.1386)
- Stop 2: Cyber City, Gurugram (28.4595, 77.1046)
- Total Distance: ~20-25 km
- Estimated Time: 60-90 minutes

### Route 3: Old Delhi & North
- Start: Connaught Place (28.6315, 77.2196)
- Stop 1: Chandni Chowk (28.6505, 77.2303)
- Stop 2: Connaught Place (28.6315, 77.2196) [Back to center]
- Total Distance: ~5-6 km
- Estimated Time: 15-20 minutes

---

## 📱 Live GPS Testing

### Test with Manual Update
1. Select "Van-01" vehicle
2. Click "Update Location"
3. Enter: Lat 28.5494, Lon 77.1906 (Hauz Khas)
4. Watch marker move on map

### Test with GPS Device
1. Select any vehicle
2. Click "Connect GPS Device"
3. Enter Device ID: TEST-DELHI-001
4. Select 10 second interval
5. Send GPS data:
```bash
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 28.5494,
    "longitude": 77.1906,
    "speed": 45,
    "heading": 120,
    "accuracy": 5
  }'
```

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Map Center** | 28.6139°N, 77.2090°E |
| **Coverage Area** | ~35-40 km radius |
| **Vehicles** | 4 (Van, Truck, Bike, Cargo) |
| **Locations** | 8 major hubs |
| **City** | Delhi, India 🇮🇳 |
| **TimeZone** | IST (UTC+5:30) |

---

**All coordinates verified for Delhi, India delivery routes! Ready to optimize. 🚀📍**
