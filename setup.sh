#!/bin/bash

# Delivery Route Optimizer - Quick Start Script
# This script sets up and runs the production-level logistics system

set -e

echo "🚀 Delivery Route Optimizer - Quick Start Setup"
echo "================================================"
echo ""

# Step 1: Create .env if not exists
echo "📝 Checking environment configuration..."
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ .env created. Please edit with your settings if needed."
else
    echo "✅ .env already exists"
fi

echo ""
echo "🔧 Setting up virtual environment..."

# Step 2: Virtual Environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

source venv/bin/activate

# Step 3: Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

echo ""
echo "🗄️  Setting up database..."

# Step 4: Database migrations
python manage.py migrate

echo ""
echo "👤 Creating superuser..."

# Step 5: Check if admin exists
ADMIN_EXISTS=$(python manage.py shell -c "from django.contrib.auth.models import User; print('yes' if User.objects.filter(username='admin').exists() else 'no')")

if [ "$ADMIN_EXISTS" = "no" ]; then
    echo "Creating admin user..."
    python manage.py shell << EOF
from django.contrib.auth.models import User
from routes.models import UserProfile

User.objects.create_superuser('admin', 'admin@localhost', 'admin@123')
print("✅ Admin user created (username: admin, password: admin@123)")
EOF
else
    echo "✅ Admin user already exists"
fi

echo ""
echo "📊 Loading sample data..."

# Step 6: Load sample data
python manage.py shell << EOF
from routes.models import Location, Vehicle, UserProfile
from django.contrib.auth.models import User

# Create users if not exist
if not User.objects.filter(username='driver1').exists():
    driver1 = User.objects.create_user('driver1', 'driver1@example.com', 'driver123')
    UserProfile.objects.create(user=driver1, role='driver')
    print("✅ Created driver1 user")

# Create vehicles if not exist
if not Vehicle.objects.filter(name='Van-01').exists():
    Vehicle.objects.create(
        name='Van-01',
        latitude=40.7128,
        longitude=-74.0060,
        color='#FFC107',
        speed=50,
        status='idle',
        capacity=50
    )
    Vehicle.objects.create(
        name='Truck-01',
        latitude=40.7180,
        longitude=-74.0080,
        color='#FF6B6B',
        speed=60,
        status='active',
        capacity=100
    )
    Vehicle.objects.create(
        name='Bike-01',
        latitude=40.7080,
        longitude=-74.0040,
        color='#51CF66',
        speed=30,
        status='idle',
        capacity=20
    )
    print("✅ Created 3 sample vehicles")

# Create locations if not exist
locations = [
    ('Chelsea Market', 40.7425, -74.0033, '75 Ninth Ave'),
    ('Times Square', 40.7580, -73.9855, '1560 Broadway'),
    ('Central Park', 40.7829, -73.9654, 'Central Park'),
    ('Empire State', 40.7484, -73.9857, '350 Fifth Ave'),
    ('Brooklyn Bridge', 40.7061, -73.9969, 'Brooklyn Bridge')
]

for name, lat, lon, addr in locations:
    if not Location.objects.filter(name=name).exists():
        Location.objects.create(
            name=name,
            latitude=lat,
            longitude=lon,
            address=addr
        )

print(f"✅ Created sample locations (0 new added)")

EOF

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo ""
echo "🌐 Starting application..."
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Run the server:"
echo "   daphne -b 0.0.0.0 -p 8000 --reload core.asgi:application"
echo ""
echo "   OR for HTTP-only (no WebSocket):"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "2️⃣  Access the application:"
echo "   Frontend: http://localhost:8000"
echo "   Admin:    http://localhost:8000/admin"
echo "   API:      http://localhost:8000/api"
echo ""
echo "3️⃣  Credentials:"
echo "   Admin Username: admin"
echo "   Admin Password: admin@123"
echo ""
echo "4️⃣  Features enabled:"
echo "   ✓ Real-time GPS tracking via WebSocket"
echo "   ✓ Route optimization (TSP algorithm)"
echo "   ✓ ETA prediction"
echo "   ✓ Analytics dashboard"
echo "   ✓ Multi-vehicle support"
echo "   ✓ Modern yellow-themed UI"
echo ""
echo "📚 Full setup guide: SETUP_GUIDE.md"
echo ""
