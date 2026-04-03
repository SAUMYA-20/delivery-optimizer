"""
Django Channels WebSocket consumers for real-time vehicle tracking
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.serializers.json import DjangoJSONEncoder
from channels.db import database_sync_to_async
from datetime import datetime

from .models import Vehicle, VehicleTracking, Route
from .services import SimulationService, TrackingService


class TrackingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for vehicle tracking updates"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        self.vehicle_id = self.scope['url_route']['kwargs'].get('vehicle_id')
        self.room_group_name = f'tracking_{self.vehicle_id}'
        self.simulation_active = False
        self.current_route_id = None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket connected for vehicle {self.vehicle_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket disconnected for vehicle {self.vehicle_id}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'location_update':
                # Process location update
                await self.handle_location_update(data)

            elif message_type == 'start_simulation':
                # Start vehicle simulation
                await self.handle_start_simulation(data)

            elif message_type == 'stop_simulation':
                # Stop simulation
                await self.handle_stop_simulation()

            elif message_type == 'get_status':
                # Get current vehicle status
                await self.send_vehicle_status()

        except json.JSONDecodeError:
            await self.send_error("Invalid JSON")
        except Exception as e:
            await self.send_error(f"Error: {str(e)}")

    async def handle_location_update(self, data):
        """Handle GPS location update"""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        speed = data.get('speed', 0.0)
        heading = data.get('heading', 0.0)

        # Save tracking data to database
        await self.save_tracking_data(latitude, longitude, speed, heading)

        # Broadcast to all clients in group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'location_update',
                'data': {
                    'vehicle_id': self.vehicle_id,
                    'latitude': latitude,
                    'longitude': longitude,
                    'speed': speed,
                    'heading': heading,
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

    async def handle_start_simulation(self, data):
        """Start simulating vehicle movement"""
        route_id = data.get('route_id')

        try:
            if self.simulation_active:
                await self.send_error("Simulation already running")
                return

            self.current_route_id = route_id
            route = await self.get_route(route_id)
            vehicle = await self.get_vehicle()
            simulated_points = await self.get_simulated_points(route, vehicle)

            # Send confirmation
            await self.send_json({
                'type': 'simulation_started',
                'vehicle_id': self.vehicle_id,
                'total_points': len(simulated_points)
            })

            # Simulate movement
            await self.simulate_movement(simulated_points)

        except Exception as e:
            await self.send_error(f"Simulation error: {str(e)}")
            self.simulation_active = False

    async def handle_stop_simulation(self):
        """Stop simulation"""
        self.simulation_active = False
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'simulation_stopped',
                'vehicle_id': self.vehicle_id
            }
        )

    async def simulate_movement(self, points):
        """Simulate vehicle movement through points"""
        self.simulation_active = True
        update_interval = 2  # Send update every 2 seconds

        for point in points:
            if not self.simulation_active:
                break

            # Save and broadcast location
            await self.save_tracking_data(
                point['latitude'],
                point['longitude'],
                point['speed'],
                point['heading']
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'location_update',
                    'data': {
                        'vehicle_id': self.vehicle_id,
                        'latitude': point['latitude'],
                        'longitude': point['longitude'],
                        'speed': point['speed'],
                        'heading': point['heading'],
                        'timestamp': datetime.now().isoformat()
                    }
                }
            )

            await asyncio.sleep(update_interval)

    async def send_vehicle_status(self):
        """Send current vehicle status"""
        vehicle = await self.get_vehicle()
        status_data = {
            'id': vehicle.id,
            'name': vehicle.name,
            'latitude': vehicle.latitude,
            'longitude': vehicle.longitude,
            'status': vehicle.status,
            'speed': vehicle.speed,
            'capacity': vehicle.capacity,
            'current_load': vehicle.current_load,
        }

        await self.send_json({
            'type': 'vehicle_status',
            'data': status_data
        })

    # Event handlers
    async def location_update(self, event):
        """Send location update to client"""
        await self.send_json({
            'type': 'location_update',
            'data': event['data']
        })

    async def simulation_stopped(self, event):
        """Notify simulation stopped"""
        await self.send_json({
            'type': 'simulation_stopped',
            'vehicle_id': event['vehicle_id']
        })

    # Database operations
    @database_sync_to_async
    def save_tracking_data(self, latitude, longitude, speed, heading):
        """Save tracking data to database"""
        try:
            vehicle = Vehicle.objects.get(id=self.vehicle_id)
            # Update vehicle position
            vehicle.latitude = latitude
            vehicle.longitude = longitude
            vehicle.save()

            # Record tracking point
            VehicleTracking.objects.create(
                vehicle=vehicle,
                latitude=latitude,
                longitude=longitude,
                speed=speed,
                heading=heading
            )
        except Vehicle.DoesNotExist:
            pass

    @database_sync_to_async
    def get_vehicle(self):
        """Get vehicle from database"""
        return Vehicle.objects.get(id=self.vehicle_id)

    @database_sync_to_async
    def get_route(self, route_id):
        """Get route from database"""
        return Route.objects.get(id=route_id)

    @database_sync_to_async
    def get_simulated_points(self, route, vehicle):
        """Get simulated movement points"""
        return TrackingService.simulate_vehicle_movement(vehicle, route, num_points=10)

    async def send_json(self, content):
        """Send JSON to client"""
        await self.send(
            text_data=json.dumps(content, cls=DjangoJSONEncoder)
        )

    async def send_error(self, error_message):
        """Send error message to client"""
        await self.send_json({
            'type': 'error',
            'message': error_message
        })


class FleetConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for fleet-wide updates"""

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'fleet_tracking'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("Fleet tracking consumer connected")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print("Fleet tracking consumer disconnected")

    async def fleet_update(self, event):
        """Broadcast fleet update"""
        await self.send_json({
            'type': 'fleet_update',
            'data': event['data']
        })

    async def send_json(self, content):
        """Send JSON to client"""
        await self.send(
            text_data=json.dumps(content, cls=DjangoJSONEncoder)
        )
