import geopandas as gpd
import osmnx as ox
import networkx as nx
from shapely.geometry import Polygon
import os

print("Lade Daten...")
pois = gpd.read_file("data/processed/categorized_pois.geojson")
boundary = gpd.read_file("data/raw/zurich_boundary.geojson")

# Nur Punktgeometrien verwenden
pois = pois[pois.geometry.geom_type == "Point"]

# Auswahl: 6 POIs aus verschiedenen Kategorien (zufällig für Vielfalt)
categories = ["Kultur", "Attraktion", "Unterkunft", "Gastronomie"]
selected_pois = pois[pois["category"].isin(categories)].sample(n=6, random_state=42)

print("Ausgewählte POIs:")
print(selected_pois[["category"]])

# 🚶 Fussweg-Netzwerk für Zürich laden
print("Lade Fusswegenetz...")
G = ox.graph_from_polygon(boundary.unary_union, network_type="walk")

# Funktion für Isochronen
def make_iso_polygons(G, center_node, times=[5, 10, 15], speed_kmph=4.5):
    meters_per_minute = speed_kmph * 1000 / 60
    time_polys = []

    for minutes in times:
        cutoff = minutes * meters_per_minute
        subgraph = nx.ego_graph(G, center_node, radius=cutoff, distance="length")
        nodes = ox.graph_to_gdfs(subgraph, edges=False)
        polygon = nodes.unary_union.convex_hull
        time_polys.append((minutes, polygon))

    return time_polys

# Isochronen berechnen
isochrones = []
print("Berechne Isochronen...")
for idx, poi in selected_pois.iterrows():
    point = poi.geometry
    node = ox.distance.nearest_nodes(G, point.x, point.y)

    for minutes, polygon in make_iso_polygons(G, node):
        isochrones.append({
            "category": poi["category"],
            "time": minutes,
            "geometry": polygon
        })

# GeoDataFrame erstellen
gdf_iso = gpd.GeoDataFrame(isochrones)
gdf_iso.set_crs(G.graph['crs'], inplace=True)
gdf_iso = gdf_iso.to_crs(epsg=4326)

# Speichern
output_path = "data/processed/isochrones.geojson"
os.makedirs("data/processed", exist_ok=True)
gdf_iso.to_file(output_path, driver="GeoJSON")

print(f"Isochronen gespeichert unter: {output_path}")
