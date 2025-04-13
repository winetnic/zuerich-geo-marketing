# Import von Geodaten in PostgreSQL/PostGIS für das Zürich Geo-Marketing-Projekt

import geopandas as gpd
from sqlalchemy import create_engine
import os

def main():
    print("Importiere Geodaten in PostgreSQL/PostGIS...")
    
    # Datenbankverbindung herstellen (passe die Verbindungsparameter an)
    db_user = "geo_user"
    db_password = "nP7r#Xg2!vDqL9zA"
    db_host = "localhost"
    db_port = "5432"
    db_name = "zuerich_tourism"
    
    db_connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_connection_string)
    
    # Prüfen, ob die benötigten Geodaten existieren
    required_files = [
        'data/raw/zurich_boundary.geojson',
        'data/raw/tourism_pois.geojson'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"Folgende Dateien fehlen: {missing_files}")
        print("Bitte führe zuerst src/data_collection/collect_osm_data.py aus.")
        return
    
    # Geodaten laden
    print("Lade Geodaten...")
    zurich_boundary = gpd.read_file('data/raw/zurich_boundary.geojson')
    tourism_pois = gpd.read_file('data/raw/tourism_pois.geojson')
    
    # Daten in PostgreSQL/PostGIS importieren
    print("Importiere Stadtgrenzen...")
    zurich_boundary.to_postgis('zurich_boundary', engine, if_exists='replace')
    
    print("Importiere touristische POIs...")
    tourism_pois.to_postgis('tourism_pois', engine, if_exists='replace')
    
    print("Daten wurden erfolgreich in PostgreSQL/PostGIS importiert!")

if __name__ == "__main__":
    main()