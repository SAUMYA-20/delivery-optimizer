from django.urls import path
from .views import (
    # Auth
    register_user, login_user,
    # Locations
    locations, location_detail,
    # Vehicles
    vehicles, vehicle_detail, update_vehicle_position,
    # Routes
    optimize_route, get_routes, route_detail, complete_delivery,
    # Tracking
    get_vehicle_tracking, simulate_vehicle,
    # GPS Device
    receive_gps_data, vehicle_gps_history, get_vehicle_current_location,
    # Analytics
    vehicle_stats, fleet_stats, delivery_metrics,
    # Health
    health_check
)

urlpatterns = [
    # Auth
    path('auth/register/', register_user, name='register'),
    path('auth/login/', login_user, name='login'),

    # Locations
    path('locations/', locations, name='locations'),
    path('locations/<int:pk>/', location_detail, name='location-detail'),

    # Vehicles
    path('vehicles/', vehicles, name='vehicles'),
    path('vehicles/<int:pk>/', vehicle_detail, name='vehicle-detail'),
    path('vehicles/position/update/', update_vehicle_position, name='update-position'),

    # Routes
    path('routes/', get_routes, name='routes'),
    path('routes/<int:pk>/', route_detail, name='route-detail'),
    path('routes/optimize/', optimize_route, name='optimize-route'),
    path('routes/delivery/complete/', complete_delivery, name='complete-delivery'),

    # Tracking
    path('tracking/vehicles/<int:vehicle_id>/', get_vehicle_tracking, name='vehicle-tracking'),
    path('tracking/simulate/', simulate_vehicle, name='simulate-vehicle'),

    # GPS Device
    path('gps/receive/', receive_gps_data, name='receive-gps-data'),
    path('tracking/vehicles/<int:vehicle_id>/history/', vehicle_gps_history, name='vehicle-gps-history'),
    path('vehicles/<int:vehicle_id>/current-location/', get_vehicle_current_location, name='current-location'),

    # Analytics
    path('analytics/vehicles/<int:vehicle_id>/', vehicle_stats, name='vehicle-stats'),
    path('analytics/fleet/', fleet_stats, name='fleet-stats'),
    path('analytics/deliveries/', delivery_metrics, name='delivery-metrics'),

    # Health
    path('health/', health_check, name='health-check'),
]