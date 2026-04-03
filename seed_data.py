#!/usr/bin/env python
"""
Sample data seeding script for Delivery Route Optimizer
Usage: python manage.py shell < seed_data.py
"""

from django.contrib.auth.models import User
from routes.models import UserProfile, Vehicle, Location, Route, RouteStop, DeliveryEvent

print("\n" + "="*60)
print("🌱 Seeding Sample Data for Delivery Route Optimizer")
print("="*60 + "\n")

# Create Users
print("👥 Creating sample users...")
users_data = [
    {'username': 'admin', 'email': 'admin@example.com', 'password': 'admin@123', 'role': 'admin', 'is_staff': True},
    {'username': 'driver1', 'email': 'driver1@example.com', 'password': 'driver123', 'role': 'driver', 'is_staff': False},
    {'username': 'driver2', 'email': 'driver2@example.com', 'password': 'driver123', 'role': 'driver', 'is_staff': False},
    {'username': 'customer1', 'email': 'customer1@example.com', 'password': 'customer123', 'role': 'customer', 'is_staff': False},
]

for user_data in users_data:
    username = user_data['username']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            email=user_data['email'],
            password=user_data['password']
        )
        if user_data.get('is_staff'):
            user.is_staff = True
            user.is_superuser = True
            user.save()

        UserProfile.objects.create(user=user, role=user_data['role'])
        print(f"  ✓ Created {username} ({user_data['role']})")
    else:
        print(f"  ✓ {username} already exists")

# Create Vehicles
print("\n🚗 Creating vehicles...")
vehicles_data = [
    {
        'name': 'Van-01',
        'latitude': 28.6315,
        'longitude': 77.2196,
        'color': '#FFC107',
        'speed': 50,
        'status': 'idle',
        'capacity': 50,
        'driver_username': 'driver1'
    },
    {
        'name': 'Truck-01',
        'latitude': 28.4595,
        'longitude': 77.1046,
        'color': '#FF6B6B',
        'speed': 60,
        'status': 'active',
        'capacity': 100,
        'driver_username': 'driver2'
    },
    {
        'name': 'Bike-01',
        'latitude': 28.5494,
        'longitude': 77.1906,
        'color': '#51CF66',
        'speed': 30,
        'status': 'idle',
        'capacity': 20
    },
    {
        'name': 'Cargo-01',
        'latitude': 28.5921,
        'longitude': 77.3971,
        'color': '#FFB300',
        'speed': 45,
        'status': 'idle',
        'capacity': 75
    }
]

for veh_data in vehicles_data:
    name = veh_data['name']
    if not Vehicle.objects.filter(name=name).exists():
        driver = None
        if veh_data.get('driver_username'):
            driver = User.objects.get(username=veh_data['driver_username'])

        Vehicle.objects.create(
            name=name,
            driver=driver,
            latitude=veh_data['latitude'],
            longitude=veh_data['longitude'],
            color=veh_data['color'],
            speed=veh_data['speed'],
            status=veh_data['status'],
            capacity=veh_data['capacity']
        )
        print(f"  ✓ Created {name} ({veh_data['status']})")
    else:
        print(f"  ✓ {name} already exists")

# Create Locations - Across All of India
print("\n📍 Creating delivery locations across India...")
locations_data = [
    # North India (Delhi/NCR)
    ('Connaught Place, Delhi', 28.6315, 77.2196, 'Connaught Place, New Delhi'),
    ('Cyber City Gurugram', 28.4595, 77.1046, 'DLF Cyber City, Gurugram'),
    ('Noida City Centre', 28.5921, 77.3971, 'Noida City Centre, Noida'),
    ('Hauz Khas, Delhi', 28.5494, 77.1906, 'Hauz Khas, South Delhi'),
    ('Greater Noida', 28.4744, 77.5559, 'Greater Noida, Uttar Pradesh'),
    ('Chandigarh IT Park', 30.7333, 76.7333, 'Technology Park, Chandigarh'),

    # West India
    ('Gateway of India, Mumbai', 18.9220, 72.8347, 'Gateway of India, Mumbai, Maharashtra'),
    ('Bandra, Mumbai', 19.0596, 72.8295, 'Bandra, Mumbai, Maharashtra'),
    ('Powai, Mumbai', 19.1136, 72.9026, 'Powai, Mumbai, Maharashtra'),
    ('Marine Drive, Mumbai', 18.9432, 72.8236, 'Marine Drive, Mumbai, Maharashtra'),
    ('Pune City Center', 18.5204, 73.8567, 'Pune Central Business District, Maharashtra'),
    ('Hinjewadi IT Park, Pune', 18.5912, 73.7680, 'Hinjewadi Tech Park, Pune, Maharashtra'),

    # South India
    ('Bangalore MG Road', 12.9716, 77.5946, 'MG Road Business District, Bangalore, Karnataka'),
    ('Koramangala, Bangalore', 13.0352, 77.6245, 'Koramangala IT Hub, Bangalore, Karnataka'),
    ('Whitefield, Bangalore', 12.9698, 77.7499, 'Whitefield Tech Park, Bangalore, Karnataka'),
    ('Fort Kochi, Kerala', 9.9673, 76.2419, 'Fort Kochi, Kerala'),
    ('Infopark Kochi', 9.9299, 76.3500, 'Infopark Complex, Kochi, Kerala'),
    ('T Nagar, Chennai', 13.0284, 80.2449, 'T Nagar Shopping District, Chennai, Tamil Nadu'),
    ('Anna Nagar, Chennai', 13.0822, 80.2084, 'Anna Nagar, Chennai, Tamil Nadu'),
    ('Thiruvananthapuram', 8.5241, 76.9366, 'Thiruvananthapuram City, Kerala'),

    # East India
    ('Salt Lake, Kolkata', 22.5726, 88.3639, 'Salt Lake City, Kolkata, West Bengal'),
    ('Park Street, Kolkata', 22.5437, 88.3728, 'Park Street Area, Kolkata, West Bengal'),
    ('Rajarhat Business District', 22.5965, 88.4715, 'Rajarhat, Kolkata'),
    ('Guwahati City Center', 26.1445, 91.7362, 'Guwahati Business District, Assam'),

    # Central India
    ('Banjara Hills, Hyderabad', 17.3850, 78.4867, 'Banjara Hills, Hyderabad, Telangana'),
    ('HITEC City, Hyderabad', 17.3611, 78.3735, 'HITEC City, Hyderabad, Telangana'),
    ('Cyber Towers, Hyderabad', 17.4460, 78.3733, 'Cyber Towers, Hyderabad, Telangana'),
    ('Indore Business District', 22.7196, 75.8577, 'Indore City Center, Madhya Pradesh'),
    ('Bhopal City Center', 23.1815, 79.9864, 'Bhopal Business District, Madhya Pradesh'),

    # Tier-2 & Other Cities
    ('Jaipur IT Park', 26.9124, 75.7873, 'IT Park, Jaipur, Rajasthan'),
    ('Navi Mumbai', 19.0176, 73.0197, 'Navi Mumbai Business Park, Maharashtra'),
    ('HSR Layout, Bangalore', 12.9352, 77.6245, 'HSR Layout, Bangalore, Karnataka'),
    ('Visakhapatnam Port City', 17.6869, 83.2185, 'Visakhapatnam, Andhra Pradesh'),
    ('Udaipur City Center', 24.5854, 73.7125, 'Udaipur Tourist Hub, Rajasthan'),
    ('Lucknow Business District', 26.8467, 80.9462, 'Lucknow, Uttar Pradesh'),
    ('Ahmedabad City Center', 23.0225, 72.5714, 'Ahmedabad Central, Gujarat'),
    ('Vadodara Business Hub', 22.3072, 73.1812, 'Vadodara, Gujarat'),
    ('Surat Downtown', 21.1458, 72.8326, 'Surat Diamond District, Gujarat'),
    ('Nagpur City Center', 21.1458, 79.0882, 'Nagpur Orange City Center, Maharashtra'),
]

for name, lat, lon, addr in locations_data:
    if not Location.objects.filter(name=name).exists():
        Location.objects.create(
            name=name,
            latitude=lat,
            longitude=lon,
            address=addr
        )
        print(f"  ✓ Created {name}")
    else:
        print(f"  ✓ {name} already exists")

print("\n" + "="*60)
print("✅ Sample data seeding complete!")
print("="*60)

# Print summary statistics
print("\n📊 Summary:")
print(f"  • Total Users: {User.objects.count()}")
print(f"  • Total Vehicles: {Vehicle.objects.count()}")
print(f"  • Total Locations: {Location.objects.count()}")
print(f"  • Total Routes: {Route.objects.count()}")

print("\n🔑 Sample Credentials:")
print("  Admin:")
print("    Username: admin")
print("    Password: admin@123")
print("\n  Driver:")
print("    Username: driver1")
print("    Password: driver123")

print("\n📍 Sample Locations Available:")
for loc in Location.objects.all()[:5]:
    print(f"  • {loc.name} ({loc.latitude:.4f}, {loc.longitude:.4f})")

print("\n🚗 Sample Vehicles Available:")
for veh in Vehicle.objects.all():
    driver_name = veh.driver.username if veh.driver else "None"
    print(f"  • {veh.name} - Driver: {driver_name} - Status: {veh.status}")

print("\n" + "="*60)
print("Ready to test! Start with:")
print("  1. Login to admin: http://localhost:8000/admin")
print("  2. Open app: http://localhost:8000")
print("  3. Create a route: POST /api/routes/optimize/")
print("="*60 + "\n")

exit()
