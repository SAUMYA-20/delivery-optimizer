from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from datetime import datetime

from .models import (
    Location, Vehicle, Route, RouteStop, UserProfile,
    VehicleTracking, DeliveryEvent
)
from .serializers import (
    LocationSerializer, VehicleSerializer, RouteDetailedSerializer,
    VehicleTrackingSerializer, UserProfileSerializer,
    RouteOptimizationInputSerializer, DeliveryEventSerializer
)
from .services import (
    RoutingService, DistanceCalculator, ETAService,
    TrackingService, AnalyticsService, SimulationService
)


# ============= AUTHENTICATION APIs =============

@api_view(['POST'])
def register_user(request):
    """Register new user"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role', 'customer')

    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    UserProfile.objects.create(user=user, role=role)

    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def login_user(request):
    """Login user (JWT-ready)"""
    from django.contrib.auth import authenticate

    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user:
        profile = user.profile
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': profile.role,
            'message': 'Login successful'
        })

    return Response({
        'error': 'Invalid credentials'
    }, status=status.HTTP_401_UNAUTHORIZED)


# ============= LOCATION APIs =============

@api_view(['GET', 'POST'])
def locations(request):
    """Get all locations or create new"""
    if request.method == 'GET':
        locs = Location.objects.all()
        serializer = LocationSerializer(locs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def location_detail(request, pk):
    """Get, update, or delete location"""
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return Response({'error': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        location.delete()
        return Response({'message': 'Location deleted'}, status=status.HTTP_204_NO_CONTENT)


# ============= VEHICLE APIs =============

@api_view(['GET', 'POST'])
def vehicles(request):
    """Get all vehicles or create new"""
    if request.method == 'GET':
        vehs = Vehicle.objects.all()
        serializer = VehicleSerializer(vehs, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = VehicleSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def vehicle_detail(request, pk):
    """Get or update vehicle"""
    try:
        vehicle = Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def update_vehicle_position(request):
    """Update vehicle GPS position"""
    vehicle_id = request.data.get('vehicle_id')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    speed = request.data.get('speed', 0.0)
    heading = request.data.get('heading', 0.0)

    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    # Update vehicle position
    vehicle.latitude = latitude
    vehicle.longitude = longitude
    vehicle.save()

    # Record tracking data
    tracking = TrackingService.record_tracking_data(
        vehicle=vehicle,
        latitude=latitude,
        longitude=longitude,
        speed=speed,
        heading=heading
    )

    serializer = VehicleTrackingSerializer(tracking)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ============= ROUTE APIs =============

@api_view(['POST'])
def optimize_route(request):
    """Optimize route for vehicle"""
    serializer = RouteOptimizationInputSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    vehicle_id = serializer.validated_data['vehicle_id']
    location_ids = serializer.validated_data['location_ids']

    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except Vehicle.DoesNotExist:
        return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        route = RoutingService.create_route(vehicle, location_ids)

        # Calculate ETA
        eta_info = ETAService.calculate_route_eta(route, vehicle)

        result_serializer = RouteDetailedSerializer(route)
        response = result_serializer.data
        response['eta_info'] = eta_info

        return Response(response, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_routes(request):
    """Get all routes"""
    routes = Route.objects.all()
    serializer = RouteDetailedSerializer(routes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def route_detail(request, pk):
    """Get route details"""
    try:
        route = Route.objects.get(pk=pk)
    except Route.DoesNotExist:
        return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = RouteDetailedSerializer(route)
    return Response(serializer.data)


@api_view(['POST'])
def complete_delivery(request):
    """Mark delivery as completed"""
    route_stop_id = request.data.get('route_stop_id')
    notes = request.data.get('notes', '')

    try:
        stop = RouteStop.objects.get(id=route_stop_id)
    except RouteStop.DoesNotExist:
        return Response({'error': 'Stop not found'}, status=status.HTTP_404_NOT_FOUND)

    stop.completed_at = datetime.now()
    stop.was_delivered = True
    stop.save()

    # Create event
    DeliveryEvent.objects.create(
        route=stop.route,
        location=stop.location,
        event_type='delivered',
        notes=notes
    )

    return Response({
        'message': 'Delivery completed',
        'stop_id': stop.id
    })


# ============= TRACKING APIs =============

@api_view(['GET'])
def get_vehicle_tracking(request, vehicle_id):
    """Get recent tracking data for vehicle"""
    try:
        vehicle = Vehicle.objects.get(device_id=vehicle_id)
    except Vehicle.DoesNotExist:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    limit = request.GET.get('limit', 100)
    tracking_data = VehicleTracking.objects.filter(vehicle=vehicle)[:int(limit)]
    serializer = VehicleTrackingSerializer(tracking_data, many=True)

    return Response({
        'vehicle_id': vehicle_id,
        'vehicle_name': vehicle.name,
        'tracking_points': serializer.data
    })


@api_view(['POST'])
def simulate_vehicle(request):
    """Simulate vehicle movement along route"""
    vehicle_id = request.data.get('vehicle_id')
    route_id = request.data.get('route_id')

    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
        route = Route.objects.get(id=route_id, vehicle=vehicle)
    except (Vehicle.DoesNotExist, Route.DoesNotExist):
        return Response({'error': 'Vehicle or Route not found'}, status=status.HTTP_404_NOT_FOUND)

    # Generate simulated points
    simulated_points = TrackingService.simulate_vehicle_movement(vehicle, route)

    return Response({
        'vehicle_id': vehicle_id,
        'route_id': route_id,
        'simulated_points': simulated_points,
        'total_points': len(simulated_points)
    })


# ============= ANALYTICS APIs =============

@api_view(['GET'])
def vehicle_stats(request, vehicle_id):
    """Get analytics for specific vehicle"""
    try:
        vehicle = Vehicle.objects.get(device_id=vehicle_id)
    except Vehicle.DoesNotExist:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found'}, status=status.HTTP_404_NOT_FOUND)

    stats = AnalyticsService.get_vehicle_stats(vehicle)
    return Response(stats)


@api_view(['GET'])
def fleet_stats(request):
    """Get analytics for entire fleet"""
    stats = AnalyticsService.get_fleet_stats()
    return Response(stats)


@api_view(['GET'])
def delivery_metrics(request):
    """Get delivery metrics"""
    from django.db.models import Count, Q

    total_deliveries = DeliveryEvent.objects.filter(event_type='delivered').count()
    failed_deliveries = DeliveryEvent.objects.filter(event_type='failed').count()
    avg_time = AnalyticsService.get_average_delivery_time()

    return Response({
        'total_deliveries': total_deliveries,
        'failed_deliveries': failed_deliveries,
        'success_rate': round((total_deliveries / (total_deliveries + failed_deliveries) * 100), 2) if (total_deliveries + failed_deliveries) > 0 else 0,
        'average_delivery_time_minutes': avg_time,
        'timestamp': datetime.now().isoformat()
    })


# ============= GPS DEVICE TRACKING API =============

@api_view(['POST'])
def receive_gps_data(request):
    """
    Receive GPS data from connected GPS devices/mobile apps

    Features:
    - Automatically creates vehicles if they don't exist
    - Updates vehicle position in real-time
    - Broadcasts updates via WebSocket

    Request Format:
    {
        "vehicle_id": 1,
        "latitude": 40.7425,
        "longitude": -74.0033,
        "speed": 45.5,
        "heading": 125.3,
        "accuracy": 5.0
    }

    Optional headers:
    - X-Device-Token: device authentication token
    - X-Device-ID: device identifier
    """
    try:
        vehicle_id = request.data.get('vehicle_id')
        vehicle_name = request.data.get('vehicle_name')  # Optional: custom name for new vehicles
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        speed = request.data.get('speed', 0.0)
        heading = request.data.get('heading', 0.0)
        accuracy = request.data.get('accuracy', 10.0)

        # Validate required fields
        if not all([vehicle_id, latitude, longitude]):
            return Response({
                'error': 'Missing required fields: vehicle_id, latitude, longitude'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate coordinate ranges
        if not (-90 <= latitude <= 90):
            return Response({
                'error': 'Latitude must be between -90 and 90'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not (-180 <= longitude <= 180):
            return Response({
                'error': 'Longitude must be between -180 and 180'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create vehicle by device_id
        vehicle, created = Vehicle.objects.get_or_create(
            device_id=vehicle_id,
            defaults={
                'name': vehicle_name or f'Vehicle-{vehicle_id}',
                'latitude': latitude,
                'longitude': longitude,
                'speed': speed,
                'status': 'active',
                'capacity': 100,
                'color': f'#{hash(str(vehicle_id)) & 0xFFFFFF:06x}'
            }
        )
        if created:
            print(f"✓ Auto-created vehicle: {vehicle.name} (Device ID: {vehicle_id})")

        # Always update vehicle position with latest GPS data
        vehicle.latitude = latitude
        vehicle.longitude = longitude
        vehicle.speed = speed
        vehicle.status = 'active'
        vehicle.save()

        # Save GPS tracking data
        tracking = TrackingService.record_tracking_data(
            vehicle=vehicle,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading,
            accuracy=accuracy
        )

        # Broadcast update via WebSocket (if consumer is available)
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        room_group_name = f'tracking_{vehicle_id}'

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'location_update',
                'data': {
                    'vehicle_id': vehicle_id,
                    'latitude': latitude,
                    'longitude': longitude,
                    'speed': speed,
                    'heading': heading,
                    'accuracy': accuracy,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'gps_device'
                }
            }
        )

        return Response({
            'status': 'success',
            'message': 'GPS data received and processed',
            'vehicle_id': vehicle_id,
            'tracking_id': tracking.id,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Error processing GPS data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def vehicle_gps_history(request, vehicle_id):
    """Get GPS tracking history for a vehicle"""
    try:
        vehicle = Vehicle.objects.get(device_id=vehicle_id)
    except Vehicle.DoesNotExist:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({
                'error': 'Vehicle not found'
            }, status=status.HTTP_404_NOT_FOUND)

    # Get last 100 tracking records
    tracking_data = VehicleTracking.objects.filter(
        vehicle=vehicle
    ).order_by('-timestamp')[:100]

    serializer = VehicleTrackingSerializer(tracking_data, many=True)

    return Response({
        'vehicle_id': vehicle_id,
        'vehicle_name': vehicle.name,
        'total_records': len(serializer.data),
        'tracking_history': serializer.data
    })


@api_view(['GET'])
def get_vehicle_current_location(request, vehicle_id):
    """Get current location of a vehicle"""
    # Try to find by device_id first (for GPS tracking), then by id (for normal vehicles)
    try:
        vehicle = Vehicle.objects.get(device_id=vehicle_id)
    except Vehicle.DoesNotExist:
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response({
                'error': 'Vehicle not found'
            }, status=status.HTTP_404_NOT_FOUND)

    # Get latest tracking data
    latest_tracking = VehicleTracking.objects.filter(
        vehicle=vehicle
    ).order_by('-timestamp').first()

    return Response({
        'vehicle_id': vehicle.id,
        'vehicle_name': vehicle.name,
        'latitude': vehicle.latitude,
        'longitude': vehicle.longitude,
        'speed': vehicle.speed,
        'status': vehicle.status,
        'timestamp': latest_tracking.timestamp.isoformat() if latest_tracking else None,
        'accuracy': latest_tracking.accuracy if latest_tracking else None
    })


# ============= HEALTH CHECK =============

@api_view(['GET'])
def health_check(request):
    """API health check"""
    return Response({
        'status': 'healthy',
        'message': 'Delivery Optimizer API is running',
        'timestamp': datetime.now().isoformat()
    })