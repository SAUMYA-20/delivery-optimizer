# Delivery Analytics - Complete Maintenance Guide

## 📋 Quick Start

### Running Analytics Commands

```bash
# View quick summary
python manage.py analytics

# Full detailed report
python manage.py analytics --report

# Fleet statistics only
python manage.py analytics --fleet

# Specific vehicle
python manage.py analytics --vehicle 1

# Daily report
python manage.py analytics --daily

# Weekly report
python manage.py analytics --weekly

# Export to JSON
python manage.py analytics --export fleet_stats.json

# Cleanup old data
python manage.py analytics --cleanup
```

### Running Maintenance Dashboard

```bash
python manage.py shell < analytics_maintenance.py
```

---

## 📊 Available Analytics Metrics

### 1. Fleet-Wide Metrics
- **Total Vehicles** - Count of all vehicles
- **Active Vehicles** - Vehicles in delivery
- **Idle Vehicles** - Available for deployment
- **Total Distance** - Sum of all completed routes (km)
- **Total Deliveries** - Number of successful deliveries
- **Vehicle Breakdown** - Individual performance stats

### 2. Vehicle-Specific Metrics
- **Active Routes** - Current assignments
- **Completed Routes** - Historical count
- **Total Distance** - Vehicle-specific mileage
- **Total Deliveries** - Deliveries by this vehicle
- **Utilization** - Load vs capacity percentage

### 3. Delivery Metrics
- **Total Deliveries** - All completed deliveries
- **Failed Deliveries** - Unsuccessful attempts
- **Success Rate** - Percentage success
- **Average Delivery Time** - Minutes per delivery
- **Timestamp** - When metrics were recorded

### 4. Tracking Data
- **GPS Records** - Total position tracking points
- **Date Range** - Oldest to newest tracking data
- **Vehicle Coverage** - Tracking per vehicle
- **Movement History** - Complete route traces

---

## 🔄 Tracking Data Flow

```
GPS Device/Mobile App
        ↓
receive_gps_data() endpoint
        ↓
VehicleTracking model (stores position history)
        ↓
DeliveryEvent model (when marked complete)
        ↓
AnalyticsService (aggregates data)
        ↓
API endpoints (/api/analytics/*)
        ↓
Reports/Dashboard/Export
```

---

## 🛠️ Maintenance Workflows

### Daily Operations

#### Log a Delivery
```bash
# Option 1: Django Admin
http://localhost:8000/admin/routes/deliveryevent/add/

# Option 2: API Call
curl -X POST http://localhost:8000/api/gps/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 28.6315,
    "longitude": 77.2196,
    "speed": 45,
    "heading": 90,
    "accuracy": 5
  }'

# Option 3: Django Shell
python manage.py shell
>>> from routes.models import DeliveryEvent, Route, Location
>>> route = Route.objects.get(id=1)
>>> location = Location.objects.get(id=5)
>>> DeliveryEvent.objects.create(
...     route=route,
...     location=location,
...     event_type='delivered'
... )
```

#### Mark Route Complete
```bash
python manage.py shell

from routes.models import Route, DeliveryEvent
from django.utils import timezone

route = Route.objects.get(id=1)
route.is_active = False
route.completed_at = timezone.now()
route.save()

# Log completion event
DeliveryEvent.objects.create(
    route=route,
    event_type='completed'
)
```

#### Update Route Stops
```bash
python manage.py shell

from routes.models import RouteStop
from django.utils import timezone

stop = RouteStop.objects.get(route_id=1, order=2)
stop.was_delivered = True
stop.arrival_time = timezone.now()
stop.completed_at = timezone.now()
stop.save()
```

### Weekly Reviews

#### Generate Weekly Report
```bash
python manage.py analytics --weekly
```

#### Check Failed Deliveries
```bash
python manage.py shell

from routes.models import DeliveryEvent
from django.utils import timezone
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)
failed = DeliveryEvent.objects.filter(
    event_type='failed',
    timestamp__gte=week_ago
)

for event in failed:
    print(f"{event.route.vehicle.name}: {event.location.name}")
    print(f"  Reason: {event.notes}\n")
```

#### Export Weekly Analytics
```bash
python manage.py analytics --export weekly_report_$(date +%Y%m%d).json
```

### Monthly Maintenance

#### Database Health Check
```bash
python manage.py shell < analytics_maintenance.py
```

#### Backup Database
```bash
# SQLite
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# PostgreSQL (if production)
pg_dump delivery_optimizer > backup_$(date +%Y%m%d).sql
```

#### Archive Old Data
```bash
python manage.py analytics --cleanup
```

#### Generate Monthly Report
```python
import json
from routes.services import AnalyticsService

stats = AnalyticsService.get_fleet_stats()
print(json.dumps(stats, indent=2, default=str))

# Save to file
with open(f'analytics_$(date +%Y%m).json', 'w') as f:
    json.dump(stats, f, indent=2, default=str)
```

---

## 📈 Using Analytics APIs

### Get Fleet Statistics
```bash
curl http://localhost:8000/api/analytics/fleet/ | python -m json.tool
```

**Response Fields:**
```json
{
  "total_vehicles": 7,
  "active_vehicles": 4,
  "idle_vehicles": 3,
  "maintenance_vehicles": 0,
  "total_distance_km": 450.5,
  "total_deliveries": 45,
  "vehicle_stats": [...]
}
```

### Get Vehicle Stats
```bash
curl http://localhost:8000/api/analytics/vehicles/1/
```

**Response Fields:**
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

### Get Delivery Metrics
```bash
curl http://localhost:8000/api/analytics/deliveries/
```

**Response Fields:**
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

## 🔍 Custom Queries

### Find Deliveries by Vehicle
```bash
python manage.py shell

from routes.models import DeliveryEvent
from django.utils import timezone
from datetime import timedelta

vehicle_id = 1
days = 7

events = DeliveryEvent.objects.filter(
    route__vehicle_id=vehicle_id,
    event_type='delivered',
    timestamp__gte=timezone.now() - timedelta(days=days)
)

print(f"Vehicle {vehicle_id}: {events.count()} deliveries in last {days} days")
```

### Calculate Distance Traveled
```bash
from routes.models import Route

vehicle_id = 1
distance = sum(
    r.total_distance
    for r in Route.objects.filter(
        vehicle_id=vehicle_id,
        is_active=False
    )
) or 0

print(f"Total distance: {distance:.2f} km")
```

### Get Performance Metrics
```bash
from routes.models import DeliveryEvent, Route
from django.utils import timezone
from datetime import timedelta

# Time range
start = timezone.now() - timedelta(days=7)
end = timezone.now()

# Deliveries
delivered = DeliveryEvent.objects.filter(
    event_type='delivered',
    timestamp__range=[start, end]
).count()

failed = DeliveryEvent.objects.filter(
    event_type='failed',
    timestamp__range=[start, end]
).count()

success_rate = (delivered / (delivered + failed) * 100) if (delivered + failed) > 0 else 0

print(f"Success Rate: {success_rate:.2f}%")
print(f"Delivered: {delivered}")
print(f"Failed: {failed}")
```

---

## 💾 Database Management

### View Data Volume
```bash
python manage.py shell

from routes.models import *
from django.db.models import Count

print("Data Volume:")
print(f"  Vehicles: {Vehicle.objects.count()}")
print(f"  Routes: {Route.objects.count()}")
print(f"  Delivery Events: {DeliveryEvent.objects.count()}")
print(f"  GPS Tracking: {VehicleTracking.objects.count()}")
```

### Optimize Queries
```bash
# Check slow queries (if logging enabled)
# Index important fields in models.py

# Admin list display optimization
admin.site.site_header = "Delivery Optimizer"
admin.site.index_title = "Analytics Management"
```

### Archive Old Tracking Data
```bash
import csv
from routes.models import VehicleTracking
from django.utils import timezone
from datetime import timedelta

# Export before deleting
old_date = timezone.now() - timedelta(days=180)
old_records = VehicleTracking.objects.filter(timestamp__lt=old_date)

# Export to CSV
with open('archive_tracking.csv', 'w') as f:
    writer = csv.writer(f)
    for record in old_records:
        writer.writerow([
            record.vehicle_id,
            record.latitude,
            record.longitude,
            record.timestamp
        ])

# Delete
deleted = old_records.delete()
print(f"Deleted {deleted[0]} records")
```

---

## 🎯 Key Metrics to Monitor

| Metric | What It Means | Target |
|--------|---------------|--------|
| Success Rate | % deliveries completed | >95% |
| Avg Delivery Time | Minutes per delivery | <30 mins |
| Vehicle Utilization | Load vs capacity | >70% |
| Route Efficiency | Distance vs time | Minimize |
| Failed Deliveries | Unsuccessful attempts | <5% |
| Fleet Utilization | Active vs idle vehicles | >60% |
| Average Distance | km per route | Optimize |

---

## 🚨 Alerts & Warnings

### Watch For These Issues

```bash
# 1. Incomplete routes without completion time
python manage.py shell
>>> from routes.models import Route
>>> Route.objects.filter(is_active=False, completed_at__isnull=True).count()

# 2. Missing delivery events
>>> from routes.models import RouteStop, DeliveryEvent
>>> stops = RouteStop.objects.filter(was_delivered=True)
>>> events = DeliveryEvent.objects.filter(event_type='delivered')
>>> if stops.count() != events.count():
...     print("MISMATCH: Stops completed but events not logged")

# 3. Failed deliveries
>>> failed = DeliveryEvent.objects.filter(event_type='failed')
>>> print(f"Review {failed.count()} failed deliveries")

# 4. Old unarchived data
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> old = VehicleTracking.objects.filter(
...     timestamp__lt=timezone.now() - timedelta(days=180)
... ).count()
>>> print(f"Archive {old} old GPS records")
```

---

## 📋 Checklist

### Daily
- [ ] Check GPS tracking data received
- [ ] Log delivery events
- [ ] Mark completed deliveries
- [ ] Monitor active vehicles

### Weekly
- [ ] Generate weekly report
- [ ] Review failed deliveries
- [ ] Check fleet utilization
- [ ] Export analytics

### Monthly
- [ ] Run maintenance dashboard
- [ ] Backup database
- [ ] Archive old data
- [ ] Performance review
- [ ] Update vehicle capacities

---

## 🔐 Best Practices

1. **Always Backup** - Run daily backups
2. **Log Events** - Record every delivery status
3. **Monitor Trends** - Watch for changes in metrics
4. **Archive Data** - Keep database lean (>180 days)
5. **Review Reports** - Weekly analytics review
6. **Maintain Quality** - Ensure 95%+ success rate
7. **Update Statuses** - Real-time route/stop updates
8. **Document Issues** - Log failures with reasons

---

## 📞 Support

For detailed analytics data model documentation, see:
- [ANALYTICS_GUIDE.md](ANALYTICS_GUIDE.md)
- [routes/models.py](routes/models.py)
- [routes/services.py](routes/services.py) - AnalyticsService class

Commands created:
- `analytics_maintenance.py` - Full dashboard
- `routes/management/commands/analytics.py` - Django management command
