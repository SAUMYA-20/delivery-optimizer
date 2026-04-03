# routes/map_utils.py
import folium

def generate_map(locations):
    m = folium.Map(location=[locations[0].latitude, locations[0].longitude], zoom_start=12)

    for loc in locations:
        folium.Marker([loc.latitude, loc.longitude], popup=loc.name).add_to(m)

    m.save("map.html")