# QUICK REFERENCE - Delivery Analytics

## ⚡ Essential Commands

```bash
# Dashboard
python manage.py shell < analytics_maintenance.py

# Full Report
python manage.py analytics --report

# Fleet Stats
python manage.py analytics --fleet

# Vehicle Stats
python manage.py analytics --vehicle 1

# Daily Report
python manage.py analytics --daily

# Weekly Report
python manage.py analytics --weekly

# Export JSON
python manage.py analytics --export stats.json

# Cleanup Old Data
python manage.py analytics --cleanup
```

---

## 📊 API Endpoints

```bash
# Fleet Statistics
GET /api/analytics/fleet/

# Vehicle Statistics
GET /api/analytics/vehicles/<id>/

# Delivery Metrics
GET /api/analytics/deliveries/

# Vehicle Tracking History
GET /api/tracking/vehicles/<id>/history/

# GPS Data Submit
POST /api/gps/receive/
```

---

## 🚗 Log Delivery Event

### Via Admin UI
```
http://localhost:8000/admin/routes/deliveryevent/add/
```

### Via Django Shell
```bash
python manage.py shell

from routes.models import DeliveryEvent, Route, Location
from django.utils import timezone

route = Route.objects.get(id=1)
location = Location.objects.get(id=5)

DeliveryEvent.objects.create(
    route=route,
    location=location,
    event_type='delivered',  # started|arrived|delivered|failed|completed
    notes='Package left with security'
)
```

---

## ✅ Mark Route Complete

```bash
python manage.py shell

from routes.models import Route, DeliveryEvent, RouteStop
from django.utils import timezone

route = Route.objects.get(id=1)

# Update all stops as delivered
for stop in route.routestop_set.all():
    stop.was_delivered = True
    stop.completed_at = timezone.now()
    stop.save()

# Mark route complete
route.is_active = False
route.completed_at = timezone.now()
route.save()

# Log event
DeliveryEvent.objects.create(
    route=route,
    event_type='completed'
)
```

---

## 📈 Query Examples

### Today's Deliveries
```bash
python manage.py shell

from routes.models import DeliveryEvent
from django.utils import timezone

today = timezone.now().date()
DeliveryEvent.objects.filter(
    event_type='delivered',
    timestamp__date=today
).count()
```

### Vehicle Performance (7 days)
```bash
python manage.py shell

from routes.models import DeliveryEvent, Vehicle
from django.utils import timezone
from datetime import timedelta

vehicle = Vehicle.objects.get(id=1)
week_ago = timezone.now() - timedelta(days=7)

count = DeliveryEvent.objects.filter(
    route__vehicle=vehicle,
    event_type='delivered',
    timestamp__gte=week_ago
).count()

distance = sum(r.total_distance for r in vehicle.routes.filter(
    created_at__gte=week_ago,
    is_active=False
)) or 0

print(f"{vehicle.name}: {count} deliveries, {distance:.1f} km")
```

### Failed Deliveries
```bash
python manage.py shell

from routes.models import DeliveryEvent

failed = DeliveryEvent.objects.filter(event_type='failed')
for event in failed[:10]:
    print(f"{event.route.vehicle.name} → {event.location.name}")
    print(f"  {event.notes}\n")
```

### Success Rate
```bash
python manage.py shell

from routes.models import DeliveryEvent

delivered = DeliveryEvent.objects.filter(event_type='delivered').count()
failed = DeliveryEvent.objects.filter(event_type='failed').count()
total = delivered + failed

success_rate = (delivered / total * 100) if total > 0 else 0
print(f"Success Rate: {success_rate:.2f}%")
```

---

## 🔍 Data Models

```
Vehicle
  ├── name
  ├── device_id (GPS device ID)
  ├── latitude, longitude
  ├── speed, status
  └── speed, capacity

Route
  ├── vehicle (FK)
  ├── total_distance
  ├── estimated_time
  ├── is_active
  ├── created_at
  └── completed_at

RouteStop
  ├── route (FK)
  ├── location (FK)
  ├── order (sequence)
  ├── was_delivered (bool)
  ├── arrival_time
  └── completed_at

DeliveryEvent
  ├── route (FK)
  ├── location (FK)
  ├── event_type (5 types)
  ├── notes
  └── timestamp (auto)

VehicleTracking
  ├── vehicle (FK)
  ├── latitude, longitude
  ├── speed, heading
  ├── accuracy
  └── timestamp (auto)
```

---

## 🎯 Key Metrics

| Metric | Query |
|--------|-------|
| Total Vehicles | `Vehicle.objects.count()` |
| Active Vehicles | `Vehicle.objects.filter(status='active').count()` |
| Total Deliveries | `DeliveryEvent.objects.filter(event_type='delivered').count()` |
| Failed Deliveries | `DeliveryEvent.objects.filter(event_type='failed').count()` |
| Total Routes | `Route.objects.count()` |
| Completed Routes | `Route.objects.filter(is_active=False).count()` |
| Tracking Records | `VehicleTracking.objects.count()` |
| Success Rate | `(delivered/(delivered+failed)*100)` |
| Avg Delivery Time | `AnalyticsService.get_average_delivery_time()` |
| Fleet Stats | `AnalyticsService.get_fleet_stats()` |
| Vehicle Stats | `AnalyticsService.get_vehicle_stats(vehicle)` |

---

## 💾 Database Maintenance

```bash
# Check data volume
python manage.py shell
>>> from routes.models import *
>>> Vehicle.objects.count()
>>> Route.objects.count()
>>> DeliveryEvent.objects.count()
>>> VehicleTracking.objects.count()

# Backup
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Export analytics
python manage.py analytics --export fleet_$(date +%Y%m%d).json

# Clean old tracking data (>180 days)
python manage.py analytics --cleanup
```

---

## 🚨 Common Issues

| Problem | Solution |
|---------|----------|
| No deliveries showing | Log events in admin or API |
| Routes not marked complete | Use management command or admin |
| GPS not updating | Check `/api/gps/receive/` endpoint |
| High database size | Archive old VehicleTracking data |
| Slow analytics queries | Check database indexes |
| Missing vehicle data | Ensure Vehicle.device_id is set |

---

## 📞 Files Reference

- **ANALYTICS_GUIDE.md** - Detailed analytics documentation
- **ANALYTICS_MAINTENANCE.md** - Full maintenance workflows
- **analytics_maintenance.py** - Dashboard script
- **routes/management/commands/analytics.py** - Django command
- **routes/services.py** - AnalyticsService class
- **routes/models.py** - Database models

---

## ⏰ Maintenance Schedule

**Daily:**
- Check GPS tracking
- Log delivery events
- Monitor active routes

**Weekly:**
```bash
python manage.py analytics --weekly
```

**Monthly:**
```bash
python manage.py shell < analytics_maintenance.py
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)
python manage.py analytics --export monthly.json
```

---

## 🔐 Admin Access

```
http://localhost:8000/admin

Username: admin
Password: admin@123

Model Access:
- Vehicles
- Routes
- Delivery Events
- Vehicle Tracking
- Route Stops
```
