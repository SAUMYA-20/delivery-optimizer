# OSRM API 400 Error - Fix Documentation

## Problem - Updated
The application was returning a 400 error when trying to fetch routes from OSRM:
```
Error: OSRM API error: 400
OSRM error response (400): {"message":"Query string malformed close to position 59","code":"InvalidQuery"}
```

This typically indicates the URL or coordinates being sent to OSRM are malformed.

## Root Causes
1. **Invalid or NULL coordinates** being sent to OSRM API
2. **Coordinate string formatting issues** (extra characters, wrong order, or incorrect precision)
3. **No validation** on latitude/longitude before API calls
4. **Missing error logging** to diagnose coordinate issues
5. **Coordinates extracted as strings instead of numbers**

## Solutions Implemented

### 1. Enhanced Frontend Validation (index.html)
Added comprehensive `validateCoordinates()` function that checks:
- Coordinates are not null/undefined/NaN
- Coordinates are finite numbers (not Infinity)
- Latitude is between -90 and 90
- Longitude is between -180 and 180
- At least 2 coordinate points exist
- Proper array structure

Also added detailed logging:
- Each stop's location_coords data
- Extracted coordinates as array
- Formatted coordinate string before sending
- Full OSRM URL with length
- Per-coordinate formatting output

**Key improvements:**
```javascript
// Now handles string-to-number conversion
if (typeof lat === 'string') lat = parseFloat(lat);

// Checks for Infinity (not just NaN)
if (!isFinite(lat) || !isFinite(lng)) { ... }

// Formats with limited precision (6 decimals)
const formattedCoord = `${lng.toFixed(6)},${lat.toFixed(6)}`;
```

### 2. Serializer Enhancements (routes/serializers.py)
- Explicitly converts coordinates to float
- Validates coordinates exist and are in valid ranges
- Clear error messages if coordinates are invalid

```python
def get_location_coords(self, obj):
    lat = float(obj.location.latitude) if obj.location.latitude is not None else None
    lng = float(obj.location.longitude) if obj.location.longitude is not None else None
    # ... validation ...
    return coords
```

### 3. Model Validation (routes/models.py)
Added Django validators to the `Location` model to prevent invalid coordinates from being stored.

## Debugging Steps

When you see the "Query string malformed" error:

1. **Open Browser Console (F12)** and look for these logs:
   - "Route data received:" → Full route object
   - "Route stops:" → Array of stops
   - "Stop X:" → Individual stop data
   - "location_coords:" → Coordinates for each stop
   - "Extracted coordinates:" → The [lat, lng] array
   - "Coord X: [lat, lng] -> formattedCoord" → Formatting details
   - "Full URL length:" → Check if URL is excessively long
   - "URL:" → Copy this and test in browser address bar

2. **Check for malformed data:**
   ```javascript
   // Look for these patterns in the console
   "Invalid coordinate at index X"
   "Invalid latitude at index X"
   "Invalid longitude at index X"
   "Non-finite coordinate at index X"
   "Duplicate coordinate at index X"
   ```

3. **Test coordinate formatting:**
   ```javascript
   // Paste in browser console to manually test
   const coords = [
     [40.7425, -74.0033],
     [40.7580, -73.9855]
   ];
   const coordString = coords.map(c =>
     `${parseFloat(c[1]).toFixed(6)},${parseFloat(c[0]).toFixed(6)}`
   ).join(';');
   console.log(coordString);
   // Should output: -74.003300,40.742500;-73.985500,40.758000

   // Test the full URL with correct parameters
   const url = `https://router.project-osrm.org/route/v1/driving/${coordString}?steps=false&geometries=geojson&overview=full&annotations=true`;
   console.log('Full test URL:', url);
   // Then fetch it: fetch(url).then(r => r.json()).then(d => console.log(d));
   ```

4. **Test OSRM directly:**
   - Use the URL from browser console logs
   - Paste in browser address bar
   - Should see JSON response with "code":"Ok" if successful
   - If error, check the error message for specific issue

## Common Issues & Solutions

### Issue: "Query string malformed close to position 59"
**Cause:** URL has invalid characters or format. Usually a coordinate is malformed.

**Solution:**
- Check console logs for "Coord X:" entries
- Look for NaN, Infinity, or very large numbers
- Verify coordinate precision (should be ~6 decimal places)
- Check if coordinates contain unexpected characters

### Issue: Coordinates showing as "NaN" in logs
**Cause:** Coordinates are null, undefined, or not numeric in database

**Solution:**
```bash
python3 manage.py shell
from routes.models import Location
# Check for NULL values
Location.objects.filter(latitude__isnull=True) | Location.objects.filter(longitude__isnull=True)

# Find locations with invalid values
Location.objects.all().values('name', 'latitude', 'longitude')
```

### Issue: "Invalid latitude" or "Invalid longitude" error
**Cause:** Coordinates outside valid ranges (-90 to 90 for lat, -180 to 180 for lon)

**Solution:**
```bash
python3 manage.py shell
from routes.models import Location

# Find invalid locations
for loc in Location.objects.all():
    if not (-90 <= loc.latitude <= 90) or not (-180 <= loc.longitude <= 180):
        print(f"Invalid: {loc.name} - lat={loc.latitude}, lon={loc.longitude}")
```

### Issue: "Duplicate coordinate at index X" warning
**Cause:** Multiple stops at same location - OSRM may have issues

**Solution:**
- This is a warning but might cause issues
- Try with different locations or reorder stops
- OSRM prefers distinct waypoints

### Issue: URL is too long (>2000 characters)
**Cause:** Too many stops or coordinates have too much precision

**Solution:** The code now uses `.toFixed(6)` which should keep URLs reasonable. If still too long, reduce decimal places:
```javascript
.toFixed(4)  // Less precision
```

## Files Modified
- `templates/index.html` - Enhanced validation and logging
- `routes/serializers.py` - Type conversion and validation
- `routes/models.py` - Django field validators

## OSRM API Reference
- **Endpoint:** `https://router.project-osrm.org/route/v1/{profile}/{coordinates}`
- **Profile:** `driving` (or `walking`, `cycling`)
- **Coordinate Format:** `longitude,latitude;longitude,latitude` (semicolon-separated)
- **Valid Query Parameters:**
  - `alternatives={true|false|number}` - Return alternative routes (default: false)
  - `steps={true|false}` - Return turn-by-turn instructions (default: false)
  - `geometries={polyline|polyline6|geojson}` - Coordinate format in response (default: polyline)
  - `overview={full|simplified|false}` - Route geometry detail level (default: full)
  - `annotations={true|false}` - Return annotations with route (default: false)

- **Valid Coordinate Ranges:**
  - Latitude: -90 to 90
  - Longitude: -180 to 180

- **Example URL (Fixed):**
  ```
  https://router.project-osrm.org/route/v1/driving/-74.003300,40.742500;-73.985500,40.758000?steps=false&geometries=geojson&overview=full&annotations=true
  ```

- **Response Format:**
  ```json
  {
    "code": "Ok",
    "routes": [
      {
        "distance": 1234,      // meters
        "duration": 567,       // seconds
        "geometry": {...},     // GeoJSON LineString
        "legs": [...]          // per-segment info
      }
    ],
    "waypoints": [...]
  }
  ```

See: http://project-osrm.org/docs/v5.5.1/api/services/route/
