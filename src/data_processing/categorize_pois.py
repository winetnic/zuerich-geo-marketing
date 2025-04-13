import geopandas as gpd
import pandas as pd

# POI-Daten laden
tourism_pois = gpd.read_file('data/raw/tourism_pois.geojson')

# Kategorisierungsfunktion
def categorize_poi(poi):
    if 'tourism' in poi and poi['tourism'] in ['museum', 'gallery', 'artwork']:
        return 'Kultur'
    elif 'tourism' in poi and poi['tourism'] in ['hotel', 'hostel', 'guest_house']:
        return 'Unterkunft'
    elif 'amenity' in poi and poi['amenity'] in ['restaurant', 'cafe', 'bar']:
        return 'Gastronomie'
    elif 'shop' in poi:
        return 'Shopping'
    elif 'tourism' in poi and poi['tourism'] == 'attraction':
        return 'Attraktion'
    else:
        return 'Sonstiges'

# Anwenden der Kategoriefunktion
tourism_pois['category'] = tourism_pois.apply(categorize_poi, axis=1)

# Verarbeitete Daten speichern
tourism_pois.to_file('data/processed/categorized_pois.geojson', driver='GeoJSON')

# Kurze Statistik ausgeben
category_counts = tourism_pois['category'].value_counts()
print("POIs nach Kategorien:")
print(category_counts)
print(f"\nInsgesamt wurden {len(tourism_pois)} POIs in {len(category_counts)} Kategorien eingeteilt.")