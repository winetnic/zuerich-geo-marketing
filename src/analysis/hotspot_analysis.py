import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import gaussian_kde

print("Lade POI-Daten...")
# Kategorisierte POIs laden
pois = gpd.read_file('data/processed/categorized_pois.geojson')

print("Lade Stadtgrenze Zürich...")
# Stadtgrenze laden
zurich_boundary = gpd.read_file('data/raw/zurich_boundary.geojson')

# POIs auf Stadtgrenze beschränken
print("Filtere POIs innerhalb der Stadtgrenze...")
pois = pois[pois.within(zurich_boundary.union_all())]

# Nur Punktgeometrien verwenden (z.B. keine Flächen wie Parks, Gebäude etc.)
pois = pois[pois.geometry.geom_type == "Point"]

# Prüfen, ob genug Punkte vorhanden sind
if len(pois) < 5:
    print(f"Zu wenige POIs für KDE: {len(pois)}")
    exit()

print(f"Anzahl analysierter POIs: {len(pois)}")

# Umwandlung der Geometrien in Punkte für die KDE-Analyse
points = np.vstack([pois.geometry.x, pois.geometry.y]).T

# Kernel Density Estimation durchführen
print("Führe Kernel Density Estimation (KDE) durch...")
kde = gaussian_kde(points.T)

# Raster für die Visualisierung erstellen
x_min, y_min, x_max, y_max = pois.total_bounds
x_grid = np.linspace(x_min, x_max, 100)
y_grid = np.linspace(y_min, y_max, 100)
X, Y = np.meshgrid(x_grid, y_grid)
positions = np.vstack([X.ravel(), Y.ravel()])

# KDE auf dem Raster berechnen
Z = kde(positions)

# Resultate in ein DataFrame umwandeln für die Speicherung
kde_results = pd.DataFrame({
    'x': X.ravel(),
    'y': Y.ravel(),
    'density': Z
})

# In GeoDataFrame umwandeln
gdf_kde = gpd.GeoDataFrame(
    kde_results, geometry=gpd.points_from_xy(kde_results.x, kde_results.y),
    crs=pois.crs
)

# Ergebnisse speichern
output_path = 'data/processed/hotspot_analysis.geojson'
gdf_kde.to_file(output_path, driver='GeoJSON')

print(f"Hotspot-Analyse abgeschlossen und gespeichert unter: {output_path}")
