# ⚡ QUICKSTART - Delivery Route Optimizer

## 🚀 Get Running in 10 Minutes

### Prerequisites
- Linux/Ubuntu (or Mac/Windows WSL)
- Python 3.9+
- Git

### Step 1: Navigate to Project
```bash
cd ~/delivery-optimizer
```

### Step 2: Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Database
```bash
python manage.py migrate
```

### Step 5: Create Admin User
```bash
python manage.py createsuperuser
# Follow prompts, or use:
# Username: admin
# Email: admin@example.com
# Password: admin@123
```

### Step 6: Load Sample Data (Optional but Recommended)
```bash
python manage.py shell < seed_data.py
```

### Step 7: Run Application
```bash
# Option A: With WebSocket Support (RECOMMENDED)
daphne -b 0.0.0.0 -p 8000 --reload core.asgi:application

# Option B: HTTP Only
python manage.py runserver 0.0.0.0:8000
```

### Step 8: Access Application
- **Frontend**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin (admin/admin@123)
- **API**: http://localhost:8000/api/health/

## ✅ Test the System

### 1. Open Frontend
Navigate to http://localhost:8000

### 2. View Vehicles & Locations
- Left sidebar shows vehicles and locations
- Map displays all vehicle positions

### 3. Create Route
1. Click "Optimize Route" button
2. Select a vehicle
3. Select 2-4 locations
4. Click "Optimize"
5. See route polyline on map

### 4. Start Simulation
1. Select vehicle from left panel
2. Click "Start Sim"
3. Watch vehicle move along route with WebSocket updates

### 5. Check Analytics
- View metrics in right panel
- Switch between "Live" and "Metrics" tabs

## 📚 Quick API Tests

### Health Check
```bash
curl http://localhost:8000/api/health/
```

### List Vehicles
```bash
curl http://localhost:8000/api/vehicles/
```

### Optimize Route
```bash
curl -X POST http://localhost:8000/api/routes/optimize/ \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "location_ids": [1, 2, 3]
  }'
```

### Get Analytics
```bash
curl http://localhost:8000/api/analytics/fleet/
```

## 🎯 Key Features to Try

1. **Real-time Tracking**
   - Start simulation
   - Watch WebSocket updates on map

2. **Route Optimization**
   - Select locations
   - Let TSP algorithm find optimal route
   - See distance calculation

3. **Analytics Dashboard**
   - View delivery metrics
   - See vehicle utilization
   - Check average delivery time

4. **Multi-vehicle Support**
   - Select different vehicles
   - Each has separate route
   - Track all simultaneously

## 📍 Frontend Features

- **Yellow-themed UI** - Professional design
- **Leaflet Map** - Interactive map with markers
- **Real-time Updates** - WebSocket-powered
- **Analytics Charts** - Chart.js integration
- **Responsive Design** - Works on mobile

## 🔧 Troubleshooting

### Port 8000 in Use?
```bash
lsof -i :8000
kill -9 <PID>
```

### WebSocket Issues?
- Ensure you're using Daphne (not Django dev server)
- Check browser console for errors
- System auto-falls back to polling

### Database Issues?
```bash
rm db.sqlite3
python manage.py migrate
```

## 📖 Resources

- **Setup Details**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API Reference**: [API_EXAMPLES.md](API_EXAMPLES.md)
- **Full README**: [README.md](README.md)

## 🎓 Understanding the Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (index.html)                       │
│  - Leaflet maps, Chart.js, WebSocket client │
└──────────────┬──────────────────────────────┘
               │ WebSocket/HTTP
┌──────────────┴──────────────────────────────┐
│  Django REST API (routes/views.py)           │
│  - 15+ endpoints for all operations          │
└──────────────┬──────────────────────────────┘
               │
┌──────────────┴──────────────────────────────┐
│  Services Layer (routes/services.py)         │
│  - Routing, ETA, Tracking, Analytics        │
└──────────────┬──────────────────────────────┘
               │
┌──────────────┴──────────────────────────────┐
│  Database (SQLite)                           │
│  - 7 models with relationships               │
└──────────────────────────────────────────────┘
```

## 📋 Next Steps

1. **Explore Admin Panel**
   - Create more vehicles/locations
   - Manage users
   - View data

2. **Try API Endpoints**
   - Test route optimization
   - Create locations
   - Update vehicle positions

3. **Customize**
   - Change colors in template.config
   - Adjust vehicle speeds
   - Add your own locations

4. **Deploy**
   - Use Gunicorn for production
   - Set up Nginx reverse proxy
   - Use PostgreSQL database

## 📞 Quick Help

**Something not working?**
1. Check terminal output for errors
2. Check browser console (F12)
3. Review SETUP_GUIDE.md
4. Check specific endpoint in API_EXAMPLES.md

**Want to change something?**
- Frontend: Edit `/templates/index.html`
- API: Edit `routes/views.py`
- Models: Edit `routes/models.py` then `makemigrations`

---

**That's it!** You now have a production-level logistics system running locally. 🎉

For questions or issues, refer to the detailed guides:
- 📖 [SETUP_GUIDE.md](SETUP_GUIDE.md)
- 📚 [API_EXAMPLES.md](API_EXAMPLES.md)
- 📝 [README.md](README.md)
