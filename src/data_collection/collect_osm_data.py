import osmnx as ox
import geopandas as gpd
import os

# Verzeichnis erstellen, falls es nicht existiert
os.makedirs('data/raw', exist_ok=True)

# Zürich Gebietsabgrenzung mit alternativen Suchbegriffen
print("Lade Stadtgrenzen von Zürich...")
try:
    # Versuche verschiedene Abfragevarianten
    query_options = [
        "Zürich, Switzerland",
        "Zurich, Switzerland",
        "Zürich Stadt",
        "Zurich City"
    ]
    
    zurich_boundary = None
    for query in query_options:
        try:
            print(f"Versuche Abfrage: '{query}'")
            zurich_boundary = ox.geocode_to_gdf(query)
            if not zurich_boundary.empty:
                print(f"Erfolgreiche Abfrage mit: '{query}'")
                break
        except Exception as e:
            print(f"Fehler bei Abfrage '{query}': {e}")
    
    if zurich_boundary is None or zurich_boundary.empty:
        raise Exception("Keine der Abfragen war erfolgreich")
        
    # Für Flächenberechnung in Schweizer Projektion transformieren
    zurich_boundary_proj = zurich_boundary.to_crs(epsg=2056)  # CH1903+ / LV95
    print(f"Stadtgrenzen geladen. Fläche: {zurich_boundary_proj.area.sum()/1e6:.2f} km²")

except Exception as e:
    print(f"Fehler beim Laden der Stadtgrenzen: {e}")
    print("Erstelle vereinfachte Bounding Box für Zürich...")
    # Alternativ: Verwende eine vereinfachte Bounding Box für Zürich
    zurich_box = ox.utils_geo.bbox_from_point((47.3769, 8.5417), dist=7000)  # ~7km um Zentrum
    zurich_boundary = ox.geocode_to_gdf("Switzerland")  # Platzhalter für Schweiz-CRS
    zurich_boundary = gpd.GeoDataFrame(
        geometry=[ox.utils_geo.bbox_to_poly(*zurich_box)], 
        crs=zurich_boundary.crs
    )
    print("Vereinfachte Bounding Box erstellt.")

# Stadtgrenzen als GeoJSON speichern
zurich_boundary.to_file('data/raw/zurich_boundary.geojson', driver='GeoJSON')
print("Stadtgrenzen gespeichert.")

# OSM-Straßennetzwerk für Zürich herunterladen (nur innerhalb der Stadtgrenzen)
print("Lade Straßennetzwerk innerhalb der Stadtgrenzen...")
try:
    zurich_graph = ox.graph_from_polygon(zurich_boundary.unary_union, network_type='all')
    zurich_nodes, zurich_edges = ox.graph_to_gdfs(zurich_graph)
    print(f"Straßennetzwerk geladen: {len(zurich_nodes)} Knoten, {len(zurich_edges)} Kanten")
except Exception as e:
    print(f"Fehler beim Laden des Straßennetzwerks: {e}")
    print("Versuche alternativen Ansatz mit place...")
    zurich_graph = ox.graph_from_place("Zürich, Switzerland", network_type='all')
    zurich_nodes, zurich_edges = ox.graph_to_gdfs(zurich_graph)
    print(f"Straßennetzwerk geladen: {len(zurich_nodes)} Knoten, {len(zurich_edges)} Kanten")

# POIs für Tourismus herunterladen
print("Lade touristische POIs...")
tourism_tags = {
    'tourism': ['attraction', 'museum', 'hotel', 'viewpoint', 'artwork', 'gallery'],
    'amenity': ['restaurant', 'cafe', 'bar', 'theatre', 'cinema', 'nightclub'],
    'shop': ['souvenir', 'clothes', 'mall', 'department_store', 'jewelry'],
    'historic': ['monument', 'memorial', 'castle', 'ruins'],
    'leisure': ['park', 'garden']
}

# POIs innerhalb der Stadtgrenzen herunterladen und filtern
try:
    print("Versuche POIs mit Polygon zu laden...")
    tourism_pois = ox.features_from_polygon(zurich_boundary.unary_union, tags=tourism_tags)
except Exception as e:
    print(f"Fehler beim Laden der POIs mit Polygon: {e}")
    print("Versuche alternativen Ansatz mit place...")
    tourism_pois = ox.features_from_place("Zürich, Switzerland", tags=tourism_tags)

# Filtere POIs, die innerhalb der Stadtgrenzen liegen
print("Filtere POIs innerhalb der Stadtgrenzen...")
tourism_pois = gpd.sjoin(tourism_pois, zurich_boundary[['geometry']], how="inner", predicate="within")
print(f"POIs geladen und gefiltert: {len(tourism_pois)}")

# Daten speichern
print("Speichere Daten...")
zurich_nodes.to_file('data/raw/zurich_nodes.geojson', driver='GeoJSON')
zurich_edges.to_file('data/raw/zurich_edges.geojson', driver='GeoJSON')
tourism_pois.to_file('data/raw/tourism_pois.geojson', driver='GeoJSON')

print("Datensammlung abgeschlossen.")
