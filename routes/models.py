from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    """Extended user profile with roles"""
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('customer', 'Customer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Location(models.Model):
    """Delivery location"""
    name = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Valid range: -90 to 90"
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Valid range: -180 to 180"
    )
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    """Vehicle for delivery tracking"""
    STATUS_CHOICES = (
        ('idle', 'Idle'),
        ('active', 'Active'),
        ('maintenance', 'Maintenance'),
    )

    device_id = models.BigIntegerField(unique=True, null=True, blank=True)  # GPS device ID (can be very large)
    name = models.CharField(max_length=100)
    driver = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  limit_choices_to={'profile__role': 'driver'})
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    color = models.CharField(max_length=7, default='#FFC107')  # Yellow theme
    speed = models.FloatField(default=50.0)  # km/h
    capacity = models.IntegerField(default=100)  # delivery units
    current_load = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Route(models.Model):
    """Optimized route for vehicle"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes')
    locations = models.ManyToManyField(Location, through='RouteStop')
    total_distance = models.FloatField(default=0.0)  # km
    estimated_time = models.FloatField(default=0.0)  # minutes
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Route for {self.vehicle.name} - {self.created_at.date()}"

class RouteStop(models.Model):
    """Individual stop in a route"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    order = models.IntegerField()  # sequence in route
    arrival_time = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    was_delivered = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ('route', 'location', 'order')

    def __str__(self):
        return f"Stop {self.order}: {self.location.name}"

class VehicleTracking(models.Model):
    """Real-time GPS tracking data"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='tracking_data')
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed = models.FloatField(default=0.0)  # km/h
    heading = models.FloatField(default=0.0)  # degrees
    timestamp = models.DateTimeField(auto_now_add=True)
    accuracy = models.FloatField(default=10.0)  # meters

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['vehicle', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.vehicle.name} - {self.timestamp}"

class DeliveryEvent(models.Model):
    """Track delivery events"""
    EVENT_TYPES = (
        ('started', 'Route Started'),
        ('arrived', 'Arrived at Location'),
        ('delivered', 'Delivery Completed'),
        ('failed', 'Delivery Failed'),
        ('completed', 'Route Completed'),
    )

    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='events')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} - {self.route.vehicle.name}"