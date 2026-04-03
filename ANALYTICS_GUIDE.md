# Delivery Analytics Maintenance Guide

## Overview
Your system collects delivery analytics through multiple data streams:
- **DeliveryEvent** - Route events (started, arrived, delivered, failed, completed)
- **RouteStop** - Individual delivery tracking (arrival, completion, status)
- **VehicleTracking** - Real-time GPS location history
- **Route** - Overall route performance metrics

---

## 1. Analytics Data Sources

### A. **Delivery Events** (Real-time tracking)
```
Event Types:
├── 'started'    → Route begins
├── 'arrived'    → Vehicle arrives at location
├── 'delivered'  → Package delivered
├── 'failed'     → Delivery failed
└── 'completed'  → Route finished
```

**Where data is stored:**
- Model: `routes.models.DeliveryEvent`
- Fields: `route`, `location`, `event_type`, `notes`, `timestamp`

### B. **Route Stops** (Delivery completion tracking)
```
Status fields:
├── was_delivered    → Boolean (True/False)
├── arrival_time     → DateTime
├── completed_at     → DateTime
└── order            → Sequence in route
```

### C. **Vehicle Tracking** (GPS history)
```
Data collected:
├── latitude         → GPS coordinate
├── longitude        → GPS coordinate
├── speed            → km/h
├── heading          → Direction (degrees)
├── accuracy         → GPS accuracy (meters)
└── timestamp        → When recorded
```

---

## 2. Available Analytics APIs

### A. **Fleet Total Statistics**
```bash
GET /api/analytics/fleet/
```
Returns:
```json
{
  "total_vehicles": 6,
  "active_vehicles": 2,
  "idle_vehicles": 4,
  "maintenance_vehicles": 0,
  "total_distance_km": 450.5,
  "total_deliveries": 45,
  "vehicle_stats": [...]
}
```

### B. **Individual Vehicle Stats**
```bash
GET /api/analytics/vehicles/<vehicle_id>/
```
Returns:
```json
{
  "vehicle_id": 1,
  "vehicle_name": "Van-01",
  "active_routes": 1,
  "completed_routes": 8,
  "total_distance_km": 125.3,
  "total_deliveries": 32,
  "utilization": 78.5
}
```

### C. **Delivery Metrics**
```bash
GET /api/analytics/deliveries/
```
Returns:
```json
{
  "total_deliveries": 45,
  "failed_deliveries": 2,
  "success_rate": 95.56,
  "average_delivery_time_minutes": 23.5,
  "timestamp": "2026-04-04T10:30:00"
}
```

---

## 3. How to Log Delivery Events

### Option A: Via Django Admin Interface
```
1. Go to http://localhost:8000/admin
2. Navigate to Routes > Delivery Events
3. Click "Add Delivery Event"
4. Fill in:
   - Route (select active route)
   - Location (delivery address)
   - Event Type (started/arrived/delivered/failed/completed)
   - Notes (optional - driver comments)
5. Save
```

### Option B: Via API (Programmatic)
```bash
# Mark delivery as completed
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "route_id": 1,
    "location_id": 5,
    "event_type": "delivered",
    "notes": "Package left with security"
  }'
```

### Option C: Via Django Shell
```bash
python manage.py shell

from routes.models import Route, DeliveryEvent, Location
from django.utils import timezone

# Create delivery event
route = Route.objects.get(id=1)
location = Location.objects.get(id=5)
event = DeliveryEvent.objects.create(
    route=route,
    location=location,
    event_type='delivered',
    notes='Delivered by John'
)
print(f"Event created: {event}")
```

---

## 4. How to Track Route Completion

### Update RouteStop When Delivery Made
```bash
python manage.py shell

from routes.models import RouteStop
from django.utils import timezone

# Mark specific stop as delivered
stop = RouteStop.objects.get(route_id=1, order=2)
stop.was_delivered = True
stop.arrival_time = timezone.now()  # When vehicle arrived
stop.completed_at = timezone.now()  # When delivery completed
stop.save()

print(f"Marked {stop.location.name} as delivered")
```

### Mark Entire Route as Complete
```bash
from routes.models import Route
from django.utils import timezone

route = Route.objects.get(id=1)
route.is_active = False
route.completed_at = timezone.now()
route.save()

# Log completion event
DeliveryEvent.objects.create(
    route=route,
    event_type='completed',
    notes='Route finished successfully'
)
```

---

## 5. Querying Analytics Data

### A. Get Today's Deliveries
```bash
python manage.py shell

from routes.models import DeliveryEvent
from django.utils import timezone
from datetime import timedelta

today = timezone.now().date()
deliveries = DeliveryEvent.objects.filter(
    event_type='delivered',
    timestamp__date=today
)
print(f"Deliveries today: {deliveries.count()}")
for d in deliveries:
    print(f"  - {d.route.vehicle.name} → {d.location.name}")
```

### B. Vehicle Performance This Week
```bash
from routes.models import Vehicle, DeliveryEvent
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
vehicle = Vehicle.objects.get(id=1)

delivered = DeliveryEvent.objects.filter(
    route__vehicle=vehicle,
    event_type='delivered',
    timestamp__gte=week_ago
).count()

distance = sum(r.total_distance for r in vehicle.routes.filter(
    created_at__gte=week_ago,
    is_active=False
)) or 0

print(f"{vehicle.name}:")
print(f"  Deliveries: {delivered}")
print(f"  Distance: {distance} km")
```

### C. Failed Deliveries Report
```bash
from routes.models import DeliveryEvent

failed = DeliveryEvent.objects.filter(event_type='failed')
print(f"Total failed: {failed.count()}\n")

for event in failed:
    print(f"Route: {event.route.id}")
    print(f"Vehicle: {event.route.vehicle.name}")
    print(f"Location: {event.location.name}")
    print(f"Time: {event.timestamp}")
    print(f"Notes: {event.notes}\n")
```

---

## 6. Maintenance Tasks

### Daily Tasks
```bash
# Check for incomplete routes
python manage.py shell

from routes.models import Route
from django.utils import timezone

incomplete = Route.objects.filter(is_active=True)
if incomplete.exists():
    print("⚠️  Active incomplete routes:")
    for r in incomplete:
        print(f"  - {r.vehicle.name}: {r.routestop_set.count()} stops")
```

### Weekly Tasks
```bash
# Generate weekly performance report
from routes.models import DeliveryEvent, Vehicle
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
vehicles = Vehicle.objects.all()

print("Weekly Performance Report\n")
for vehicle in vehicles:
    deliveries = DeliveryEvent.objects.filter(
        route__vehicle=vehicle,
        event_type='delivered',
        timestamp__gte=week_ago
    ).count()

    distance = sum(r.total_distance for r in vehicle.routes.filter(
        created_at__gte=week_ago,
        is_active=False
    )) or 0

    print(f"{vehicle.name}: {deliveries} deliveries, {distance:.1f} km")
```

### Monthly Tasks
```bash
# Archive old completed routes (older than 90 days)
from routes.models import Route
from django.utils import timezone
from datetime import timedelta

ninety_days_ago = timezone.now() - timedelta(days=90)
old_routes = Route.objects.filter(
    is_active=False,
    completed_at__lt=ninety_days_ago
)

count = old_routes.count()
print(f"Found {count} routes to archive")

# You can export to CSV before deleting:
# old_routes.values('id', 'vehicle__name', 'total_distance', 'completed_at')
```

---

## 7. Custom Reports via API

### Get Analytics and Export
```bash
# Fetch fleet statistics
curl http://localhost:8000/api/analytics/fleet/ | python -m json.tool > fleet_report.json

# Fetch vehicle stats
curl http://localhost:8000/api/analytics/vehicles/1/ | python -m json.tool > van_01_report.json

# Get delivery metrics
curl http://localhost:8000/api/analytics/deliveries/ | python -m json.tool > delivery_metrics.json
```

### Python Script to Generate CSV Report
```python
import csv
from routes.models import DeliveryEvent
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
events = DeliveryEvent.objects.filter(timestamp__gte=week_ago)

with open('delivery_report.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Route ID', 'Vehicle', 'Location', 'Event Type', 'Time', 'Notes'])

    for event in events:
        writer.writerow([
            event.route.id,
            event.route.vehicle.name,
            event.location.name if event.location else 'N/A',
            event.event_type,
            event.timestamp,
            event.notes
        ])

print("Report saved to delivery_report.csv")
```

---

## 8. Database Optimization

### Check Tracking Data Growth
```bash
python manage.py shell

from routes.models import VehicleTracking, DeliveryEvent, Route

print(f"Tracking records: {VehicleTracking.objects.count()}")
print(f"Delivery events: {DeliveryEvent.objects.count()}")
print(f"Routes: {Route.objects.count()}")

# Check oldest records
oldest_tracking = VehicleTracking.objects.order_by('timestamp').first()
print(f"Oldest tracking: {oldest_tracking.timestamp if oldest_tracking else 'None'}")
```

### Create Database Backup
```bash
# Backup database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# On PostgreSQL:
pg_dump delivery_optimizer > backup_$(date +%Y%m%d).sql
```

### Clean Old Data
```bash
from routes.models import VehicleTracking, DeliveryEvent
from django.utils import timezone
from datetime import timedelta

# Delete tracking data older than 6 months
six_months_ago = timezone.now() - timedelta(days=180)
old_tracking = VehicleTracking.objects.filter(timestamp__lt=six_months_ago)

count = old_tracking.count()
old_tracking.delete()
print(f"Deleted {count} old tracking records")
```

---

## 9. Monitoring Analytics Health

### Check Data Consistency
```bash
from routes.models import Route, RouteStop, DeliveryEvent

routes = Route.objects.filter(is_active=False)
for route in routes[:5]:
    route_stops = route.routestop_set.all()
    delivered_stops = route_stops.filter(was_delivered=True).count()
    completed_events = DeliveryEvent.objects.filter(
        route=route,
        event_type='delivered'
    ).count()

    print(f"Route {route.id}:")
    print(f"  Stops delivered: {delivered_stops}/{route_stops.count()}")
    print(f"  Events logged: {completed_events}")

    if completed_events != delivered_stops:
        print(f"  ⚠️  MISMATCH!")
```

---

## 10. Setting Up Analytics Dashboard (Alternative UI)

If you want analytics without Chart.js, create a simple HTML view:

```html
<!-- templates/analytics.html -->
<div class="analytics-container">
  <h2>Delivery Analytics</h2>

  <div class="metric-cards">
    <div class="card">
      <h3 id="total_deliveries">-</h3>
      <p>Total Deliveries</p>
    </div>
    <div class="card">
      <h3 id="success_rate">-</h3>
      <p>Success Rate</p>
    </div>
    <div class="card">
      <h3 id="avg_time">-</h3>
      <p>Avg Time (min)</p>
    </div>
    <div class="card">
      <h3 id="total_distance">-</h3>
      <p>Total Distance (km)</p>
    </div>
  </div>
</div>

<script>
// Load analytics on page load
async function loadAnalytics() {
  const fleet = await fetch('/api/analytics/fleet/').then(r => r.json());
  const metrics = await fetch('/api/analytics/deliveries/').then(r => r.json());

  document.getElementById('total_deliveries').textContent = metrics.total_deliveries;
  document.getElementById('success_rate').textContent = metrics.success_rate + '%';
  document.getElementById('avg_time').textContent = metrics.average_delivery_time_minutes;
  document.getElementById('total_distance').textContent = fleet.total_distance_km.toFixed(0);
}

window.addEventListener('load', loadAnalytics);
</script>
```

---

## Quick Reference Commands

```bash
# View all delivery events
python manage.py shell
>>> from routes.models import DeliveryEvent
>>> list(DeliveryEvent.objects.values_list('event_type').distinct())

# Count deliveries by vehicle this month
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> from routes.models import DeliveryEvent
>>> month_ago = timezone.now() - timedelta(days=30)
>>> DeliveryEvent.objects.filter(timestamp__gte=month_ago, event_type='delivered').count()

# Get all completed routes
>>> from routes.models import Route
>>> Route.objects.filter(is_active=False).count()

# Export analytics
>>> import json
>>> from routes.services import AnalyticsService
>>> stats = AnalyticsService.get_fleet_stats()
>>> print(json.dumps(stats, indent=2, default=str))
```

---

## Summary

| Task | Method | Frequency |
|------|--------|-----------|
| Log delivery events | Admin/API/Shell | Per delivery |
| Update route stops | Admin/Shell | Per stop |
| Check fleet stats | API/Dashboard | Daily |
| Generate reports | Shell script/CSV | Weekly |
| Clean old data | Shell script | Monthly |
| Backup database | bash script | Daily |
| Performance review | Analytics API | Weekly |

Your analytics system is fully operational. All data flows automatically when you track deliveries through APIs or mark them complete in the admin interface!
