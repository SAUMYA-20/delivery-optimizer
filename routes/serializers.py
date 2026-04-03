from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Location, Vehicle, Route, RouteStop,
    VehicleTracking, DeliveryEvent
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'role', 'phone', 'created_at')
        read_only_fields = ('id', 'created_at')

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'name', 'latitude', 'longitude', 'address', 'created_at')
        read_only_fields = ('id', 'created_at')

class VehicleSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'name', 'driver', 'driver_name', 'latitude', 'longitude',
            'status', 'color', 'speed', 'capacity', 'current_load',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

class VehicleTrackingSerializer(serializers.ModelSerializer):
    vehicle_name = serializers.CharField(source='vehicle.name', read_only=True)

    class Meta:
        model = VehicleTracking
        fields = (
            'id', 'vehicle', 'vehicle_name', 'latitude', 'longitude',
            'speed', 'heading', 'accuracy', 'timestamp'
        )
        read_only_fields = ('id', 'timestamp')

class RouteStopSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)
    location_coords = serializers.SerializerMethodField()

    class Meta:
        model = RouteStop
        fields = (
            'id', 'order', 'location', 'location_name', 'location_coords',
            'arrival_time', 'completed_at', 'was_delivered'
        )
        read_only_fields = ('id', 'order')

    def get_location_coords(self, obj):
        """Return validated coordinates as floats"""
        lat = float(obj.location.latitude) if obj.location.latitude is not None else None
        lng = float(obj.location.longitude) if obj.location.longitude is not None else None

        coords = {
            'latitude': lat,
            'longitude': lng
        }

        # Validate coordinates
        if coords['latitude'] is None or coords['longitude'] is None:
            raise serializers.ValidationError(
                f"Location '{obj.location.name}' has missing coordinates"
            )
        if not (-90 <= coords['latitude'] <= 90):
            raise serializers.ValidationError(
                f"InvalidLatitude for {obj.location.name}: {coords['latitude']}"
            )
        if not (-180 <= coords['longitude'] <= 180):
            raise serializers.ValidationError(
                f"InvalidLongitude for {obj.location.name}: {coords['longitude']}"
            )

        return coords

class RouteDetailedSerializer(serializers.ModelSerializer):
    stops = RouteStopSerializer(source='routestop_set', many=True, read_only=True)
    vehicle_name = serializers.CharField(source='vehicle.name', read_only=True)
    location_count = serializers.SerializerMethodField()

    class Meta:
        model = Route
        fields = (
            'id', 'vehicle', 'vehicle_name', 'stops', 'total_distance',
            'estimated_time', 'location_count', 'created_at', 'completed_at',
            'is_active'
        )
        read_only_fields = ('id', 'created_at', 'stops')

    def get_location_count(self, obj):
        return obj.routestop_set.count()

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ('id', 'vehicle', 'total_distance', 'estimated_time', 'created_at', 'is_active')
        read_only_fields = ('id', 'created_at')

class DeliveryEventSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = DeliveryEvent
        fields = (
            'id', 'route', 'location', 'location_name', 'event_type',
            'notes', 'timestamp'
        )
        read_only_fields = ('id', 'timestamp')

class RouteOptimizationInputSerializer(serializers.Serializer):
    """Input validation for route optimization"""
    vehicle_id = serializers.IntegerField()
    location_ids = serializers.ListField(child=serializers.IntegerField())

    def validate_location_ids(self, value):
        from .models import Location

        if len(value) < 2:
            raise serializers.ValidationError("Need at least 2 locations")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate location IDs")

        # Validate that all locations exist and have valid coordinates
        locations = Location.objects.filter(id__in=value)
        if locations.count() != len(value):
            raise serializers.ValidationError("One or more locations not found")

        for location in locations:
            if location.latitude is None or location.longitude is None:
                raise serializers.ValidationError(
                    f"Location '{location.name}' has missing coordinates"
                )
            if not (-90 <= location.latitude <= 90):
                raise serializers.ValidationError(
                    f"Location '{location.name}' has invalid latitude: {location.latitude}"
                )
            if not (-180 <= location.longitude <= 180):
                raise serializers.ValidationError(
                    f"Location '{location.name}' has invalid longitude: {location.longitude}"
                )

        return value