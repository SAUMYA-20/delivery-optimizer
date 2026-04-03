"""
Django management command to view and maintain delivery analytics
Usage: python manage.py analytics [--report|--cleanup|--export]
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import json

from routes.models import Route, RouteStop, DeliveryEvent, Vehicle, VehicleTracking
from routes.services import AnalyticsService


class Command(BaseCommand):
    help = 'Manage and maintain delivery analytics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate full analytics report',
        )
        parser.add_argument(
            '--daily',
            action='store_true',
            help='Daily performance report',
        )
        parser.add_argument(
            '--weekly',
            action='store_true',
            help='Weekly performance report',
        )
        parser.add_argument(
            '--vehicle',
            type=int,
            help='Get stats for specific vehicle ID',
        )
        parser.add_argument(
            '--fleet',
            action='store_true',
            help='Get fleet-wide statistics',
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export to JSON file',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean old data (>180 days tracking)',
        )

    def handle(self, *args, **options):
        if options['fleet']:
            self.show_fleet_stats()
        elif options['vehicle']:
            self.show_vehicle_stats(options['vehicle'])
        elif options['daily']:
            self.show_daily_report()
        elif options['weekly']:
            self.show_weekly_report()
        elif options['report']:
            self.show_full_report()
        elif options['export']:
            self.export_analytics(options['export'])
        elif options['cleanup']:
            self.cleanup_old_data()
        else:
            self.show_summary()

    def show_summary(self):
        """Show quick analytics summary"""
        self.stdout.write(self.style.SUCCESS('\n📊 ANALYTICS SUMMARY\n'))

        vehicles = Vehicle.objects.all()
        self.stdout.write(f"Vehicles: {vehicles.count()}")
        self.stdout.write(f"  • Active: {vehicles.filter(status='active').count()}")
        self.stdout.write(f"  • Idle: {vehicles.filter(status='idle').count()}\n")

        routes = Route.objects.all()
        self.stdout.write(f"Routes: {routes.count()}")
        self.stdout.write(f"  • Active: {Route.objects.filter(is_active=True).count()}")
        self.stdout.write(f"  • Completed: {Route.objects.filter(is_active=False).count()}\n")

        events = DeliveryEvent.objects.all()
        self.stdout.write(f"Events: {events.count()}")
        self.stdout.write(f"  • Delivered: {DeliveryEvent.objects.filter(event_type='delivered').count()}")
        self.stdout.write(f"  • Failed: {DeliveryEvent.objects.filter(event_type='failed').count()}\n")

        self.stdout.write(self.style.WARNING('Run with --report for detailed analytics'))

    def show_fleet_stats(self):
        """Display fleet statistics"""
        self.stdout.write(self.style.SUCCESS('\n🚗 FLEET STATISTICS\n'))

        stats = AnalyticsService.get_fleet_stats()

        self.stdout.write(f"Total Vehicles: {stats['total_vehicles']}")
        self.stdout.write(f"Active Vehicles: {stats['active_vehicles']}")
        self.stdout.write(f"Idle Vehicles: {stats['idle_vehicles']}")
        self.stdout.write(f"Maintenance Vehicles: {stats['maintenance_vehicles']}\n")

        self.stdout.write(f"Total Deliveries: {stats['total_deliveries']}")
        self.stdout.write(f"Total Distance: {stats['total_distance_km']:.2f} km\n")

        self.stdout.write(self.style.SUCCESS('Vehicles:'))
        for v_stat in stats['vehicle_stats']:
            self.stdout.write(
                f"  • {v_stat['vehicle_name']}: "
                f"{v_stat['total_deliveries']} deliveries, "
                f"{v_stat['total_distance_km']:.1f} km"
            )

    def show_vehicle_stats(self, vehicle_id):
        """Display vehicle-specific statistics"""
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Vehicle {vehicle_id} not found'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n📍 VEHICLE: {vehicle.name}\n'))

        stats = AnalyticsService.get_vehicle_stats(vehicle)

        for key, value in stats.items():
            if key != 'vehicle_id':
                self.stdout.write(f"{key}: {value}")

    def show_daily_report(self):
        """Show today's report"""
        self.stdout.write(self.style.SUCCESS('\n📅 TODAY\'S REPORT\n'))

        today = timezone.now().date()
        deliveries = DeliveryEvent.objects.filter(
            event_type='delivered',
            timestamp__date=today
        )
        routes = Route.objects.filter(
            completed_at__date=today,
            is_active=False
        )

        self.stdout.write(f"Routes completed: {routes.count()}")
        self.stdout.write(f"Deliveries made: {deliveries.count()}\n")

        if deliveries.exists():
            self.stdout.write(self.style.SUCCESS('Recent deliveries:'))
            for d in deliveries[:10]:
                self.stdout.write(
                    f"  [{d.timestamp.strftime('%H:%M')}] "
                    f"{d.route.vehicle.name} → {d.location.name if d.location else 'N/A'}"
                )

    def show_weekly_report(self):
        """Show weekly report"""
        self.stdout.write(self.style.SUCCESS('\n📊 WEEKLY REPORT (Last 7 Days)\n'))

        week_ago = timezone.now() - timedelta(days=7)

        vehicles = Vehicle.objects.all()
        for vehicle in vehicles:
            deliveries = DeliveryEvent.objects.filter(
                route__vehicle=vehicle,
                event_type='delivered',
                timestamp__gte=week_ago
            ).count()

            routes = vehicle.routes.filter(
                is_active=False,
                completed_at__gte=week_ago
            ).count()

            if deliveries > 0 or routes > 0:
                self.stdout.write(
                    f"{vehicle.name}: "
                    f"{deliveries} deliveries, {routes} routes"
                )

    def show_full_report(self):
        """Generate comprehensive report"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(self.style.SUCCESS('FULL ANALYTICS REPORT'))
        self.stdout.write(self.style.SUCCESS('='*80 + '\n'))

        # Fleet overview
        self.show_fleet_stats()

        # Recent activity
        self.stdout.write(self.style.SUCCESS('\n⏰ RECENT ACTIVITY (Last 24h)\n'))
        yesterday = timezone.now() - timedelta(days=1)
        events = DeliveryEvent.objects.filter(timestamp__gte=yesterday)
        self.stdout.write(f"Events: {events.count()}")

        # Metrics
        self.stdout.write(self.style.SUCCESS('\n📈 METRICS\n'))
        total_delivered = DeliveryEvent.objects.filter(event_type='delivered').count()
        total_failed = DeliveryEvent.objects.filter(event_type='failed').count()
        total = total_delivered + total_failed

        if total > 0:
            success_rate = round((total_delivered / total * 100), 2)
            self.stdout.write(f"Total Deliveries: {total_delivered}")
            self.stdout.write(f"Failed Deliveries: {total_failed}")
            self.stdout.write(f"Success Rate: {success_rate}%")

        avg_time = AnalyticsService.get_average_delivery_time()
        self.stdout.write(f"Average Delivery Time: {avg_time} minutes")

        self.stdout.write(self.style.SUCCESS('\n' + '='*80 + '\n'))

    def export_analytics(self, filepath):
        """Export analytics to JSON"""
        stats = AnalyticsService.get_fleet_stats()

        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        self.stdout.write(self.style.SUCCESS(f'Exported to {filepath}'))

    def cleanup_old_data(self):
        """Clean old tracking data"""
        self.stdout.write(self.style.WARNING('\n🧹 CLEANUP OLD DATA\n'))

        # 180 days ago
        cutoff = timezone.now() - timedelta(days=180)

        old_tracking = VehicleTracking.objects.filter(timestamp__lt=cutoff)
        count = old_tracking.count()

        if count > 0:
            self.stdout.write(f"Found {count} old tracking records")
            confirm = input("Delete? (yes/no): ")
            if confirm.lower() == 'yes':
                old_tracking.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} records'))
        else:
            self.stdout.write("No old records to clean")
