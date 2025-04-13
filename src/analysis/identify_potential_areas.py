import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import pandas as pd

print("Identifiziere Gebiete mit touristischem Potenzial...")

# Daten laden
zurich_boundary = gpd.read_file('data/raw/zurich_boundary.geojson')
hotspots = gpd.read_file('data/processed/hotspot_analysis.geojson')
pois = gpd.read_file('data/processed/categorized_pois.geojson')

# Alle Datensätze auf das gleiche CRS bringen
common_crs = zurich_boundary.crs
hotspots = hotspots.to_crs(common_crs)
pois = pois.to_crs(common_crs)

print("Erstelle Grid über Zürich...")
# Grid über Zürich erstellen
minx, miny, maxx, maxy = zurich_boundary.total_bounds
cell_size = 0.005  # Ungefähr 500m bei geografischen Koordinaten
x_points = np.arange(minx, maxx, cell_size)
y_points = np.arange(miny, maxy, cell_size)

# Grid-Punkte erstellen
grid_points = []
for x in x_points:
    for y in y_points:
        point = Point(x, y)
        if zurich_boundary.contains(point).any():
            grid_points.append({
                'geometry': point,
                'grid_id': f'grid_{len(grid_points)}'
            })

print(f"Grid mit {len(grid_points)} Punkten erstellt.")
grid_gdf = gpd.GeoDataFrame(grid_points, crs=common_crs)

# POI-Dichte pro Grid-Zelle berechnen
print("Berechne POI-Dichte...")
def count_pois_in_buffer(point, poi_gdf, buffer_distance=0.005):
    buffer = point.buffer(buffer_distance)
    return len(poi_gdf[poi_gdf.intersects(buffer)])

grid_gdf['poi_count'] = grid_gdf.geometry.apply(
    lambda x: count_pois_in_buffer(x, pois)
)

# Hotspot-Wert für jede Grid-Zelle berechnen
print("Berechne Hotspot-Werte...")
def get_hotspot_value(point, hotspot_gdf, buffer_distance=0.005):
    buffer = point.buffer(buffer_distance)
    nearby_hotspots = hotspot_gdf[hotspot_gdf.intersects(buffer)]
    if len(nearby_hotspots) > 0:
        return nearby_hotspots.density.mean()
    return 0

grid_gdf['hotspot_value'] = grid_gdf.geometry.apply(
    lambda x: get_hotspot_value(x, hotspots)
)

# Potenzialwert berechnen
print("Berechne Potenzialwerte...")
# Gebiete mit wenigen POIs aber in der Nähe von Hotspots haben hohes Potenzial
if grid_gdf['poi_count'].max() > 0 and grid_gdf['hotspot_value'].max() > 0:
    grid_gdf['potential'] = (1 - grid_gdf['poi_count'] / grid_gdf['poi_count'].max()) * \
                           (grid_gdf['hotspot_value'] / grid_gdf['hotspot_value'].max())
else:
    grid_gdf['potential'] = 0

# Null-Werte ersetzen
grid_gdf['potential'] = grid_gdf['potential'].fillna(0)

# Top-Potenzialgebiete identifizieren (oberste 10%)
potential_threshold = grid_gdf['potential'].quantile(0.9)
high_potential_areas = grid_gdf[grid_gdf['potential'] >= potential_threshold]

print(f"{len(high_potential_areas)} Gebiete mit hohem Potenzial identifiziert.")

# Ergebnisse speichern
high_potential_areas.to_file('data/processed/high_potential_areas.geojson', driver='GeoJSON')

print("Potenzialanalyse abgeschlossen und gespeichert unter 'data/processed/high_potential_areas.geojson'")