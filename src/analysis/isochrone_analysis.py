import osmnx as ox
import geopandas as gpd
import networkx as nx
import pandas as pd
from shapely.geometry import Point, Polygon

# Straßennetzwerk und POIs laden
print("Straßennetzwerk für Zürich laden...")
G = ox.graph_from_place('Zürich, Switzerland', network_type='walk')
pois = gpd.read_file('data/processed/categorized_pois.geojson')

# Verfügbare Kategorien ausgeben
print("\nVerfügbare Kategorien in den POI-Daten:")
categories = pois['category'].unique()
for i, cat in enumerate(categories):
    print(f"{i+1}. {cat}")

# Top-POIs auswählen, unabhängig von der Kategorie, wenn keine 'Attraktion' vorhanden ist
if 'Attraktion' in categories:
    print("\nWähle Top-Attraktionen aus...")
    top_attractions = pois[pois['category'] == 'Attraktion'].head(5)
else:
    print("\nKeine 'Attraktion'-Kategorie gefunden. Wähle Top-POIs aus jeder Kategorie...")
    # Nehme die ersten POIs aus jeder Kategorie
    top_attractions = pd.concat([pois[pois['category'] == cat].head(1) for cat in categories])

print(f"Anzahl ausgewählter POIs für Isochrone: {len(top_attractions)}")

# Funktion zur Erstellung von Isochronen
def create_isochrones(G, point, travel_times=[5, 10, 15]): # Zeit in Minuten
    # Nächsten Knoten zum POI finden
    nearest_node = ox.distance.nearest_nodes(G, point.x, point.y)
    
    # Erreichbare Knoten in den angegebenen Zeitintervallen finden
    isochrones = []
    for time in travel_times:
        # Zeit in Sekunden umrechnen (Gehgeschwindigkeit ~1.4 m/s)
        max_dist = time * 60 * 1.4
        
        # Erreichbare Knoten finden
        subgraph = nx.ego_graph(G, nearest_node, radius=max_dist, distance='length')
        node_points = [Point(data['x'], data['y']) for node, data in subgraph.nodes(data=True)]
        
        if len(node_points) > 3: # Mindestens 3 Punkte für ein Polygon
            # Konvexe Hülle bilden (vereinfachte Methode)
            try:
                convex_hull = gpd.GeoSeries(node_points).unary_union.convex_hull
                isochrones.append({
                    'geometry': convex_hull,
                    'time': time
                })
            except Exception as e:
                print(f"Fehler beim Erstellen der Konvexen Hülle: {e}")
    
    return gpd.GeoDataFrame(isochrones, crs=G.graph['crs']) if isochrones else None

# Prüfen, ob POIs Point-Geometrie haben oder umgewandelt werden müssen
def ensure_point_geometry(geom):
    if geom.geom_type == 'Point':
        return geom
    else:
        return geom.representative_point()

# Sicherstellen, dass alle POIs Point-Geometrien haben
top_attractions.geometry = top_attractions.geometry.apply(ensure_point_geometry)

# Isochronen für jede Top-Attraktion erstellen
if len(top_attractions) > 0:
    print("Isochronen erstellen...")
    all_isochrones = []
    for idx, attraction in top_attractions.iterrows():
        poi_name = attraction.get('name', str(idx))
        print(f"Bearbeite POI: {poi_name} ({idx})...")
        poi_point = attraction.geometry
        try:
            isochrones = create_isochrones(G, poi_point)
            if isochrones is not None:
                isochrones['poi_name'] = poi_name
                all_isochrones.append(isochrones)
        except Exception as e:
            print(f"Fehler bei der Isochron-Erstellung für {poi_name}: {e}")

    # Alle Isochronen zusammenführen
    if all_isochrones:
        print("Speichere Isochronen...")
        combined_isochrones = pd.concat(all_isochrones)
        combined_isochrones.to_file('data/processed/isochrones.geojson', driver='GeoJSON')
        print(f"Isochron-Analyse abgeschlossen. {len(combined_isochrones)} Isochronen erstellt.")
    else:
        print("Keine Isochronen erstellt. Überprüfen Sie die POI-Daten und das Netzwerk.")
else:
    print("Keine POIs für die Isochron-Analyse gefunden.")