import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import os
import numpy as np

# Daten laden
print("Lade Daten für Hotspot-Map...")
zurich_boundary = gpd.read_file('data/raw/zurich_boundary.geojson')
hotspots = gpd.read_file('data/processed/hotspot_analysis.geojson')
pois = gpd.read_file('data/processed/categorized_pois.geojson')

# Auf Web Mercator (EPSG:3857) umprojizieren für Hintergrundkarte
zurich_boundary = zurich_boundary.to_crs(epsg=3857)
hotspots = hotspots.to_crs(epsg=3857)
pois = pois.to_crs(epsg=3857)

# Plot erstellen
fig, ax = plt.subplots(figsize=(12, 10))

# Hintergrundkarte und Grenzen hinzufügen
zurich_boundary.plot(ax=ax, alpha=0.5, edgecolor='k')

# Hotspots als Heatmap visualisieren
# Punkte in ein Grid umwandeln
from matplotlib.colors import LinearSegmentedColormap

# Hotspot-Intensitäten in ein Grid umwandeln
x = hotspots.geometry.x.values
y = hotspots.geometry.y.values
z = hotspots.density.values

# Konturplot erstellen
try:
    # Versuche mit matplotlib's griddata
    from matplotlib.tri import Triangulation, LinearTriInterpolator
    
    triang = Triangulation(x, y)
    interpolator = LinearTriInterpolator(triang, z)
    
    # Neues Grid erstellen
    xi = np.linspace(min(x), max(x), 100)
    yi = np.linspace(min(y), max(y), 100)
    Xi, Yi = np.meshgrid(xi, yi)
    
    # Interpolieren
    zi = interpolator(Xi, Yi)
    
    # Hotspot-Karte erstellen
    contour = ax.contourf(Xi, Yi, zi, levels=15, cmap='hot_r', alpha=0.7)
except Exception as e:
    print(f"Konturplot konnte nicht erstellt werden: {e}")
    print("Erstelle stattdessen Scatterplot...")
    # Fallback: Scatter Plot
    scatter = ax.scatter(x, y, c=z, cmap='hot_r', alpha=0.7, s=50)
    plt.colorbar(scatter, ax=ax, label='Dichte')

# POIs nach Kategorie hinzufügen
categories = pois['category'].unique()
for category in categories:
    subset = pois[pois.category == category]
    subset.plot(ax=ax, marker='o', label=category, markersize=15, alpha=0.7)

# Legende hinzufügen
ax.legend(title='Kategorien', loc='upper right')

# Hintergrundkarte hinzufügen
try:
    cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
except Exception as e:
    print(f"Hintergrundkarte konnte nicht hinzugefügt werden: {e}")

# Layout und Titel
plt.title('Touristische Hotspots in Zürich', fontsize=16)
plt.tight_layout()

# Speichern
output_dir = 'results/maps'
os.makedirs(output_dir, exist_ok=True)
plt.savefig(f'{output_dir}/zurich_hotspots.png', dpi=300)
print(f"Hotspot-Karte gespeichert unter: {output_dir}/zurich_hotspots.png")
plt.close()