#!/usr/bin/env python
"""
Analytics Maintenance Script for Delivery Route Optimizer
Usage: python manage.py shell < analytics_maintenance.py
"""

from routes.models import Route, RouteStop, DeliveryEvent, Vehicle, VehicleTracking
from django.utils import timezone
from datetime import timedelta
import json

print("\n" + "="*80)
print("🔍 ANALYTICS MAINTENANCE DASHBOARD")
print("="*80)

# 1. Fleet Overview
print("\n📊 FLEET OVERVIEW")
print("-" * 80)

vehicles = Vehicle.objects.all()
print(f"Total Vehicles: {vehicles.count()}")
print(f"  ✓ Active: {vehicles.filter(status='active').count()}")
print(f"  ○ Idle: {vehicles.filter(status='idle').count()}")
print(f"  ✗ Maintenance: {vehicles.filter(status='maintenance').count()}")

# 2. Route Status
print("\n📍 ROUTE STATUS")
print("-" * 80)

active_routes = Route.objects.filter(is_active=True)
completed_routes = Route.objects.filter(is_active=False, completed_at__isnull=False)

print(f"Active Routes: {active_routes.count()}")
print(f"Completed Routes: {completed_routes.count()}")
print(f"Total Distance (completed): {sum(r.total_distance for r in completed_routes) or 0:.2f} km")

# 3. Delivery Events
print("\n📦 DELIVERY EVENTS")
print("-" * 80)

all_events = DeliveryEvent.objects.all()
print(f"Total Events: {all_events.count()}")
print(f"  ✓ Delivered: {DeliveryEvent.objects.filter(event_type='delivered').count()}")
print(f"  ✗ Failed: {DeliveryEvent.objects.filter(event_type='failed').count()}")
print(f"  ▶ Started: {DeliveryEvent.objects.filter(event_type='started').count()}")
print(f"  □ Completed: {DeliveryEvent.objects.filter(event_type='completed').count()}")

# 4. Recent Activity (Last 24 hours)
print("\n⏰ RECENT ACTIVITY (Last 24 Hours)")
print("-" * 80)

yesterday = timezone.now() - timedelta(days=1)
recent_events = DeliveryEvent.objects.filter(timestamp__gte=yesterday)
recent_routes = Route.objects.filter(completed_at__gte=yesterday, is_active=False)

print(f"Routes completed: {recent_routes.count()}")
print(f"Delivery events: {recent_events.count()}")

if recent_events.exists():
    print(f"\nLast 5 events:")
    for event in recent_events[:5]:
        print(f"  [{event.timestamp.strftime('%H:%M')}] {event.event_type.upper()}: {event.route.vehicle.name} → {event.location.name if event.location else 'N/A'}")

# 5. Vehicle Performance
print("\n🚗 VEHICLE PERFORMANCE")
print("-" * 80)

for vehicle in vehicles[:5]:
    active_routes = vehicle.routes.filter(is_active=True).count()
    completed_routes = vehicle.routes.filter(is_active=False, completed_at__isnull=False)
    total_distance = sum(r.total_distance for r in completed_routes) or 0
    total_deliveries = DeliveryEvent.objects.filter(
        route__vehicle=vehicle,
        event_type='delivered'
    ).count()

    print(f"\n{vehicle.name}")
    print(f"  Status: {vehicle.status}")
    print(f"  Active routes: {active_routes}")
    print(f"  Completed routes: {completed_routes.count()}")
    print(f"  Total distance: {total_distance:.2f} km")
    print(f"  Deliveries: {total_deliveries}")

# 6. Data Health Check
print("\n✓ DATA HEALTH CHECK")
print("-" * 80)

tracking_count = VehicleTracking.objects.count()
oldest_tracking = VehicleTracking.objects.order_by('timestamp').first()
newest_tracking = VehicleTracking.objects.order_by('-timestamp').first()

print(f"Tracking records: {tracking_count}")
if oldest_tracking:
    print(f"  Oldest: {oldest_tracking.timestamp}")
if newest_tracking:
    print(f"  Newest: {newest_tracking.timestamp}")

# Check for data inconsistencies
incomplete_routes = Route.objects.filter(is_active=False, completed_at__isnull=True)
if incomplete_routes.count() > 0:
    print(f"\n⚠️  Warning: {incomplete_routes.count()} routes marked inactive but no completion time")

incomplete_events = RouteStop.objects.filter(was_delivered=False, completed_at__isnull=False)
if incomplete_events.count() > 0:
    print(f"⚠️  Warning: {incomplete_events.count()} stops marked incomplete but have completion time")

# 7. Statistics
print("\n📈 DELIVERY STATISTICS")
print("-" * 80)

total_delivered = DeliveryEvent.objects.filter(event_type='delivered').count()
total_failed = DeliveryEvent.objects.filter(event_type='failed').count()
total_all = total_delivered + total_failed

if total_all > 0:
    success_rate = round((total_delivered / total_all * 100), 2)
    print(f"Success Rate: {success_rate}%")
    print(f"Total Deliveries: {total_delivered}")
    print(f"Failed Deliveries: {total_failed}")
else:
    print("No delivery data available yet")

# 8. Database Size
print("\n💾 DATABASE SIZE")
print("-" * 80)

print(f"Delivery Events: {DeliveryEvent.objects.count()}")
print(f"Tracking Records: {VehicleTracking.objects.count()}")
print(f"Routes: {Route.objects.count()}")
print(f"Route Stops: {RouteStop.objects.count()}")

# 9. Cleanup Recommendations
print("\n🧹 MAINTENANCE RECOMMENDATIONS")
print("-" * 80)

old_tracking = VehicleTracking.objects.filter(timestamp__lt=timezone.now() - timedelta(days=180))
if old_tracking.count() > 0:
    print(f"• {old_tracking.count()} tracking records older than 180 days (consider archiving)")

old_routes = Route.objects.filter(
    is_active=False,
    completed_at__lt=timezone.now() - timedelta(days=90)
)
if old_routes.count() > 0:
    print(f"• {old_routes.count()} routes completed over 90 days ago (consider archiving)")

print("• Run backups regularly")
print("• Monitor database performance monthly")
print("• Review failed deliveries weekly")

print("\n" + "="*80)
print("✅ MAINTENANCE CHECK COMPLETE")
print("="*80 + "\n")

exit()
