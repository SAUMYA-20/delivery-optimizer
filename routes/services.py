"""
Business logic services for routing, ETA, tracking, etc.
"""
import networkx as nx
from math import radians, cos, sin, sqrt, atan2, degrees
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
from .models import Location, Vehicle, Route, RouteStop, VehicleTracking, DeliveryEvent


class DistanceCalculator:
    """Haversine formula for real-world distances"""
    EARTH_RADIUS = 6371  # km

    @staticmethod
    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)

        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return DistanceCalculator.EARTH_RADIUS * c

    @staticmethod
    def route_distance(coordinates: List[Tuple[float, float]]) -> float:
        """Calculate total distance for a route"""
        if len(coordinates) < 2:
            return 0.0

        total = 0.0
        for i in range(len(coordinates) - 1):
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i+1]
            total += DistanceCalculator.haversine(lat1, lon1, lat2, lon2)

        return total


class RoutingService:
    """Route optimization using TSP"""

    @staticmethod
    def build_distance_matrix(locations: List[Location]) -> Dict[int, Dict[int, float]]:
        """Build distance matrix for locations"""
        matrix = {}
        for i, loc1 in enumerate(locations):
            matrix[i] = {}
            for j, loc2 in enumerate(locations):
                if i == j:
                    matrix[i][j] = 0.0
                else:
                    dist = DistanceCalculator.haversine(
                        loc1.latitude, loc1.longitude,
                        loc2.latitude, loc2.longitude
                    )
                    matrix[i][j] = dist
        return matrix

    @staticmethod
    def build_graph(locations: List[Location]) -> nx.Graph:
        """Build NetworkX graph for TSP"""
        G = nx.Graph()

        for i in range(len(locations)):
            for j in range(i+1, len(locations)):
                dist = DistanceCalculator.haversine(
                    locations[i].latitude, locations[i].longitude,
                    locations[j].latitude, locations[j].longitude
                )
                G.add_edge(i, j, weight=dist)

        return G

    @staticmethod
    def nearest_neighbor_tsp(locations: List[Location]) -> List[int]:
        """Fast nearest neighbor heuristic for TSP"""
        if len(locations) <= 2:
            return list(range(len(locations)))

        unvisited = set(range(len(locations)))
        current = 0
        path = [current]
        unvisited.remove(current)

        while unvisited:
            nearest = min(
                unvisited,
                key=lambda x: DistanceCalculator.haversine(
                    locations[current].latitude,
                    locations[current].longitude,
                    locations[x].latitude,
                    locations[x].longitude
                )
            )
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        return path

    @staticmethod
    def optimize_route(locations: List[Location]) -> List[int]:
        """Optimize route using appropriate algorithm based on size"""
        if len(locations) < 2:
            return list(range(len(locations)))

        if len(locations) == 2:
            return [0, 1]

        # For small datasets (< 10), use TSP approximation
        if len(locations) < 10:
            try:
                G = RoutingService.build_graph(locations)
                path = nx.approximation.traveling_salesman_problem(G, cycle=True)
                return path
            except:
                # Fallback to nearest neighbor
                return RoutingService.nearest_neighbor_tsp(locations)
        else:
            # For larger datasets, use fast nearest neighbor
            return RoutingService.nearest_neighbor_tsp(locations)

    @staticmethod
    def create_route(vehicle: Vehicle, location_ids: List[int]) -> Route:
        """Create optimized route for vehicle"""
        locations = Location.objects.filter(id__in=location_ids)

        if not locations.exists():
            raise ValueError("No locations found")

        # Get ordered locations
        locations_list = list(locations)
        if len(locations_list) > 1:
            optimal_order = RoutingService.optimize_route(locations_list)
        else:
            optimal_order = [0]

        # Create route
        route = Route.objects.create(
            vehicle=vehicle,
            is_active=True
        )

        # Add stops in optimal order
        coords = []
        for idx, location_idx in enumerate(optimal_order):
            location = locations_list[location_idx]
            RouteStop.objects.create(
                route=route,
                location=location,
                order=idx
            )
            coords.append((location.latitude, location.longitude))

        # Calculate total distance
        route.total_distance = DistanceCalculator.route_distance(coords)
        route.save()

        return route


class ETAService:
    """ETA prediction based on distance, speed, traffic"""

    DEFAULT_SPEED = 50.0  # km/h
    TRAFFIC_MULTIPLIER = 1.2  # 20% slower with traffic

    @staticmethod
    def calculate_eta(
        distance: float,
        speed: float = DEFAULT_SPEED,
        include_traffic: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate ETA for a delivery

        Args:
            distance: Distance in km
            speed: Speed in km/h
            include_traffic: Apply traffic multiplier

        Returns:
            Dict with eta_minutes and eta_datetime
        """
        if speed <= 0:
            speed = ETAService.DEFAULT_SPEED

        multiplier = ETAService.TRAFFIC_MULTIPLIER if include_traffic else 1.0
        minutes = (distance / speed) * 60 * multiplier

        eta_time = datetime.now() + timedelta(minutes=minutes)

        return {
            'eta_minutes': round(minutes, 2),
            'eta_datetime': eta_time.isoformat(),
            'distance_km': distance
        }

    @staticmethod
    def calculate_route_eta(route: Route, vehicle: Vehicle) -> Dict[str, Any]:
        """Calculate ETA for entire route"""
        stops = route.routestop_set.all()

        if not stops.exists():
            return {'error': 'No stops in route'}

        # Calculate remaining distance
        remaining_distance = route.total_distance

        # Get vehicle speed
        speed = vehicle.speed or ETAService.DEFAULT_SPEED

        return ETAService.calculate_eta(remaining_distance, speed, include_traffic=True)


class TrackingService:
    """Real-time GPS tracking and simulation"""

    @staticmethod
    def record_tracking_data(
        vehicle: Vehicle,
        latitude: float,
        longitude: float,
        speed: float = 0.0,
        heading: float = 0.0,
        accuracy: float = 10.0
    ) -> VehicleTracking:
        """Record vehicle position"""
        tracking = VehicleTracking.objects.create(
            vehicle=vehicle,
            latitude=latitude,
            longitude=longitude,
            speed=speed,
            heading=heading,
            accuracy=accuracy
        )
        return tracking

    @staticmethod
    def get_closest_route_stop(vehicle: Vehicle, route: Route) -> RouteStop:
        """Find next undelivered stop"""
        incomplete_stops = route.routestop_set.filter(was_delivered=False).order_by('order')
        if incomplete_stops.exists():
            return incomplete_stops.first()
        return None

    @staticmethod
    def simulate_vehicle_movement(vehicle: Vehicle, route: Route, num_points: int = 5):
        """Simulate vehicle moving along route with intermediate points"""
        stops = list(route.routestop_set.all().order_by('order'))

        if not stops:
            return []

        simulated_points = []

        for i in range(len(stops) - 1):
            start_stop = stops[i]
            end_stop = stops[i + 1]

            start_lat, start_lon = start_stop.location.latitude, start_stop.location.longitude
            end_lat, end_lon = end_stop.location.latitude, end_stop.location.longitude

            # Interpolate points between stops
            for point_num in range(num_points):
                t = point_num / num_points

                lat = start_lat + t * (end_lat - start_lat)
                lon = start_lon + t * (end_lon - start_lon)

                # Calculate heading
                dlat = end_lat - start_lat
                dlon = end_lon - start_lon
                heading = degrees(atan2(dlon, dlat))

                simulated_points.append({
                    'latitude': lat,
                    'longitude': lon,
                    'speed': vehicle.speed,
                    'heading': heading
                })

        return simulated_points


class AnalyticsService:
    """Analytics and reporting"""

    @staticmethod
    def get_vehicle_stats(vehicle: Vehicle) -> Dict[str, Any]:
        """Get analytics for a vehicle"""
        active_routes = vehicle.routes.filter(is_active=True)
        completed_routes = vehicle.routes.filter(is_active=False, completed_at__isnull=False)

        total_distance = sum(r.total_distance for r in completed_routes) or 0
        delivery_count = sum(r.routestop_set.filter(was_delivered=True).count() for r in completed_routes)

        return {
            'vehicle_id': vehicle.id,
            'vehicle_name': vehicle.name,
            'active_routes': active_routes.count(),
            'completed_routes': completed_routes.count(),
            'total_distance_km': round(total_distance, 2),
            'total_deliveries': delivery_count,
            'utilization': round((vehicle.current_load / vehicle.capacity * 100), 2) if vehicle.capacity > 0 else 0
        }

    @staticmethod
    def get_fleet_stats() -> Dict[str, Any]:
        """Get analytics for entire fleet"""
        vehicles = Vehicle.objects.all()

        stats = {
            'total_vehicles': vehicles.count(),
            'active_vehicles': vehicles.filter(status='active').count(),
            'idle_vehicles': vehicles.filter(status='idle').count(),
            'maintenance_vehicles': vehicles.filter(status='maintenance').count(),
            'total_distance_km': 0,
            'total_deliveries': 0,
            'vehicle_stats': []
        }

        for vehicle in vehicles:
            v_stats = AnalyticsService.get_vehicle_stats(vehicle)
            stats['vehicle_stats'].append(v_stats)
            stats['total_distance_km'] += v_stats['total_distance_km']
            stats['total_deliveries'] += v_stats['total_deliveries']

        return stats

    @staticmethod
    def get_average_delivery_time() -> float:
        """Calculate average delivery time"""
        events = DeliveryEvent.objects.filter(event_type='delivered')

        if not events.exists():
            return 0

        total_time = 0
        count = 0

        for event in events:
            route_events = DeliveryEvent.objects.filter(route=event.route).order_by('timestamp')
            start_event = route_events.filter(event_type='started').first()
            if start_event:
                time_diff = (event.timestamp - start_event.timestamp).total_seconds() / 60
                total_time += time_diff
                count += 1

        return round(total_time / count, 2) if count > 0 else 0


class SimulationService:
    """Helper for GPS simulation"""

    @staticmethod
    def get_interpolated_point(
        lat1: float, lon1: float,
        lat2: float, lon2: float,
        t: float
    ) -> Tuple[float, float]:
        """Linear interpolation between two points"""
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        return lat, lon
