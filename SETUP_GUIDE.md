# Delivery Route Optimizer - Setup Guide

## System Requirements
- Ubuntu 20.04+ (or Linux)
- Python 3.9+
- pip package manager
- Git

## Step 1: Environment Setup

### Clone/Extract Project
```bash
cd ~/delivery-optimizer
```

### Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: Environment Configuration

### Create .env File
```bash
cp .env.example .env
```

### Edit .env with Your Settings
```bash
nano .env
```

**Example .env:**
```
DEBUG=True
SECRET_KEY=your-super-secret-key-change-this
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Optional: Google Maps API
GOOGLE_MAPS_API_KEY=your-key-here
USE_TRAFFIC_API=False

# WebSocket
CHANNEL_LAYERS_BACKEND=channels.layers.InMemoryChannelLayer

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000

# Vehicle Defaults
DEFAULT_VEHICLE_SPEED=50
DEFAULT_VEHICLE_CAPACITY=100

# Features
ENABLE_WEBSOCKETS=True
ENABLE_ANALYTICS=True
SIMULATE_GPS=True
GPS_UPDATE_INTERVAL=5
```

## Step 3: Database Setup

### Apply Migrations
```bash
python manage.py migrate
```

### Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Load Sample Data (Optional)
```bash
python manage.py shell
```

Paste this into the Python shell:
```python
from routes.models import Location, Vehicle, UserProfile
from django.contrib.auth.models import User

# Create users
admin_user = User.objects.create_user('admin', 'admin@example.com', 'admin123', is_staff=True, is_superuser=True)
driver1 = User.objects.create_user('driver1', 'driver1@example.com', 'driver123')
UserProfile.objects.create(user=driver1, role='driver')

# Create vehicles
Vehicle.objects.create(name='Van-01', driver=driver1, latitude=51.5074, longitude=-0.1278, color='#FFC107', speed=50)
Vehicle.objects.create(name='Truck-01', latitude=51.5174, longitude=-0.1278, color='#FF6B6B', speed=60)
Vehicle.objects.create(name='Bike-01', latitude=51.5274, longitude=-0.1278, color='#51CF66', speed=30)

# Create locations
Location.objects.create(name='Customer A', latitude=51.515, longitude=-0.1, address='123 Main St')
Location.objects.create(name='Customer B', latitude=51.520, longitude=-0.12, address='456 Oxford St')
Location.objects.create(name='Customer C', latitude=51.525, longitude=-0.15, address='789 King St')
Location.objects.create(name='Customer D', latitude=51.510, longitude=-0.08, address='321 Queen St')
Location.objects.create(name='Warehouse', latitude=51.5074, longitude=-0.1278, address='Central Warehouse')

exit()
```

## Step 4: Run the Application

### Using Daphne (with WebSocket Support)
```bash
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

Or with auto-reload during development:
```bash
daphne -b 0.0.0.0 -p 8000 --reload core.asgi:application
```

### OR Use Django Development Server (HTTP Only)
```bash
python manage.py runserver 0.0.0.0:8000
```

## Step 5: Access the Application

### Frontend
- **URL**: http://localhost:8000
- Open in your web browser

### Admin Panel
- **URL**: http://localhost:8000/admin
- **Username**: admin
- **Password**: admin123

### API Documentation
- **Base URL**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/api/health/

## API Endpoints Reference

### Authentication
```
POST   /api/auth/register/          - Register new user
POST   /api/auth/login/             - Login user
```

### Locations
```
GET    /api/locations/              - List all locations
POST   /api/locations/              - Create location
GET    /api/locations/<id>/         - Get location details
PUT    /api/locations/<id>/         - Update location
DELETE /api/locations/<id>/         - Delete location
```

### Vehicles
```
GET    /api/vehicles/               - List all vehicles
POST   /api/vehicles/               - Create vehicle
GET    /api/vehicles/<id>/          - Get vehicle details
PUT    /api/vehicles/<id>/          - Update vehicle
POST   /api/vehicles/position/update/ - Update GPS position
```

### Routes & Optimization
```
GET    /api/routes/                 - List all routes
GET    /api/routes/<id>/            - Get route details
POST   /api/routes/optimize/        - Optimize new route
POST   /api/routes/delivery/complete/ - Mark delivery complete
```

### Tracking
```
GET    /api/tracking/vehicles/<id>/ - Get vehicle tracking history
POST   /api/tracking/simulate/      - Get simulated movement points
```

### Analytics
```
GET    /api/analytics/vehicles/<id>/ - Vehicle analytics
GET    /api/analytics/fleet/         - Fleet analytics
GET    /api/analytics/deliveries/   - Delivery metrics
```

### WebSocket Endpoints
```
ws://localhost:8000/ws/tracking/vehicle/<vehicle_id>/
ws://localhost:8000/ws/fleet/
```

## Usage Examples

### Example 1: Create Location
```bash
curl -X POST http://localhost:8000/api/locations/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Downtown Center",
    "latitude": 51.5,
    "longitude": -0.1,
    "address": "100 Market St"
  }'
```

### Example 2: Optimize Route
```bash
curl -X POST http://localhost:8000/api/routes/optimize/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "location_ids": [1, 2, 3, 4]
  }'
```

### Example 3: Update Vehicle Position
```bash
curl -X POST http://localhost:8000/api/vehicles/position/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "latitude": 51.515,
    "longitude": -0.12,
    "speed": 45.5,
    "heading": 90.0
  }'
```

### Example 4: Get Fleet Analytics
```bash
curl http://localhost:8000/api/analytics/fleet/
```

## Frontend Features

### Dashboard Components
1. **Map View**
   - Display all vehicles with color-coded markers
   - Show optimized routes as polylines
   - Real-time marker updates

2. **Vehicle Panel** (Left Sidebar)
   - List of active vehicles
   - Quick actions (Optimize, Start/Stop Simulation)
   - Location management

3. **Analytics Panel** (Right Sidebar)
   - Live vehicle delivery chart
   - Fleet metrics (total delivered, distance, utilization)
   - Vehicle-specific statistics

4. **Control Modals**
   - Route optimization dialog
   - Add location dialog
   - Responsive design for mobile

### Yellow-themed UI
- Primary Color: #FFC107 (Amber)
- Clean card-based layout
- Smooth animations and transitions
- Professional color scheme with contrasting elements

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database Issues
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### WebSocket Connection Issues
1. Ensure Daphne is running (not Django's development server)
2. Check CORS_ALLOWED_ORIGINS in settings
3. Check browser console for connection errors
4. System will auto-fallback to polling if WebSocket fails

### Python/Django Errors
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Development Tips

### Run Tests
```bash
python manage.py test
```

### Check Code Style
```bash
pip install flake8
flake8 routes/ --max-line-length=100
```

### Enable Debug Mode
```bash
# Add to .env
DEBUG=True
```

### Create Test Data Quickly
```bash
python manage.py shell < scripts/seed_data.py
```

## Performance Optimization

1. **Database Indexing**: Already configured on VehicleTracking and RouteStop models
2. **Caching**: Implement Redis for analytics cache (optional)
3. **Pagination**: API endpoints support 100 items per page by default
4. **WebSocket Scaling**: Use Channels with Redis for multi-instance deployment

## Deployment to Production

### Using Gunicorn + Nginx + Supervisor

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

For production setup with Nginx and SSL, refer to Django deployment documentation.

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│        Frontend (HTML/CSS/JS)                │
│  - Leaflet Maps, Chart.js Analytics         │
│  - Real-time WebSocket Updates              │
└──────────────────┬──────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────┴──────────────────────────┐
│      Django Backend (REST API)               │
│  - DRF Viewsets / Function-based Views       │
│  - Route Optimization (TSP)                  │
│  - Real-time Tracking                        │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│  Services Layer (routes/services.py)         │
│  - Routing Service (TSP with NetworkX)       │
│  - Distance Calculator (Haversine)           │
│  - ETA Service (Duration Prediction)         │
│  - Tracking Service (GPS Simulation)         │
│  - Analytics Service (Metrics)               │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────┴──────────────────────────┐
│    Models & Database (SQLite)                │
│  - User, Vehicle, Location, Route            │
│  - VehicleTracking, RouteStop, DeliveryEvent │
└──────────────────────────────────────────────┘
```

## Support & Resources

- **Django Docs**: https://docs.djangoproject.com/
- **Django Channels**: https://channels.readthedocs.io/
- **DRF**: https://www.django-rest-framework.org/
- **Leaflet**: https://leafletjs.com/
- **NetworkX**: https://networkx.org/

---

**Last Updated**: March 2026
**Version**: 1.0.0
