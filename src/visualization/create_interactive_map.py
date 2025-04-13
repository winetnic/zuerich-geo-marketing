import geopandas as gpd
import folium
from folium import plugins
import numpy as np
import os

print("Lade Daten für interaktive Karte...")

# Daten laden und auf WGS84 (EPSG:4326) projizieren für Folium
pois = gpd.read_file('data/processed/categorized_pois.geojson').to_crs(epsg=4326)
isochrones = gpd.read_file('data/processed/isochrones.geojson').to_crs(epsg=4326)
seasonal_pois = gpd.read_file('data/processed/seasonal_pois.geojson').to_crs(epsg=4326)

# Nur Punktgeometrien für Zentrum bestimmen
points_only = pois[pois.geometry.geom_type == "Point"]
center = [points_only.geometry.y.mean(), points_only.geometry.x.mean()]

# Interaktive Karte erstellen
m = folium.Map(location=center, zoom_start=13, tiles='CartoDB positron')

# Farben für Kategorien definieren
category_colors = {
    'Kultur': 'blue',
    'Unterkunft': 'green',
    'Gastronomie': 'red',
    'Shopping': 'purple',
    'Attraktion': 'orange',
    'Sonstiges': 'gray'
}

# POIs nach Kategorie hinzufügen
print("Füge POI-Kategorien zur Karte hinzu...")
for category, color in category_colors.items():
    cat_layer = folium.FeatureGroup(name=f'Kategorie: {category}')
    subset = pois[(pois.geometry.geom_type == "Point") & (pois.category == category)]
    
    for idx, row in subset.iterrows():
        name = row.get('name', f'POI {idx}')
        popup_text = f"<b>{name}</b><br>Kategorie: {category}"
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(cat_layer)
    
    cat_layer.add_to(m)

# 🔥 Echte Heatmap basierend auf POI-Verteilung
print("Füge echte POI-Heatmap hinzu...")
poi_heat_data = [
    [row.geometry.y, row.geometry.x]
    for idx, row in pois.iterrows()
    if row.geometry.geom_type == "Point"
]
heatmap_layer = folium.FeatureGroup(name='POI Heatmap')
plugins.HeatMap(poi_heat_data, radius=25, blur=15, max_zoom=14).add_to(heatmap_layer)
heatmap_layer.add_to(m)

# Isochronen-Layer
print("Füge Isochronen hinzu...")
isochrone_layer = folium.FeatureGroup(name='Erreichbarkeit (Isochronen)')
time_colors = {5: 'green', 10: 'yellow', 15: 'red'}

for idx, row in isochrones.iterrows():
    time = row.get('time', 5)
    color = time_colors.get(time, 'blue')
    folium.GeoJson(
        row.geometry,
        style_function=lambda x, col=color: {
            'fillColor': col,
            'color': col,
            'weight': 1,
            'fillOpacity': 0.3
        },
        tooltip=f"{row.get('poi_name', 'POI')}: {time} Minuten zu Fuss"
    ).add_to(isochrone_layer)

isochrone_layer.add_to(m)

# Saisonale Layer
print("Füge saisonale Layer hinzu...")
summer_layer = folium.FeatureGroup(name='Sommer-Hotspots')
winter_layer = folium.FeatureGroup(name='Winter-Hotspots')

for idx, row in seasonal_pois.iterrows():
    if row.geometry.geom_type != "Point":
        continue

    if row.weight_sommer > 0.6:
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=row.weight_sommer * 10,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.5,
            tooltip=f"{row.get('name', 'POI')}: Sommerwert {row.weight_sommer:.2f}"
        ).add_to(summer_layer)

    if row.weight_winter > 0.4:
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=row.weight_winter * 10,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.5,
            tooltip=f"{row.get('name', 'POI')}: Winterwert {row.weight_winter:.2f}"
        ).add_to(winter_layer)

summer_layer.add_to(m)
winter_layer.add_to(m)

# Layer Control
folium.LayerControl(collapsed=False).add_to(m)

# Karte speichern
output_path = 'results/zurich_interactive_map.html'
m.save(output_path)

print(f"Interaktive Karte gespeichert unter: {output_path}")
