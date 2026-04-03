"""
Django Channels routing configuration for WebSockets
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tracking/vehicle/(?P<vehicle_id>\w+)/$', consumers.TrackingConsumer.as_asgi()),
    re_path(r'ws/fleet/$', consumers.FleetConsumer.as_asgi()),
]
