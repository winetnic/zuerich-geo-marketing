import geopandas as gpd

print("Lade kategorisierte POIs...")
pois = gpd.read_file('data/processed/categorized_pois.geojson')

# Gewichtungsregeln
season_weights = {
    'Kultur':       {'sommer': 0.4, 'winter': 0.9},
    'Unterkunft':   {'sommer': 0.5, 'winter': 0.5},
    'Gastronomie':  {'sommer': 0.6, 'winter': 0.6},
    'Shopping':     {'sommer': 0.7, 'winter': 0.7},
    'Attraktion':   {'sommer': 0.6, 'winter': 0.6},
    'Sonstiges':    {'sommer': 0.3, 'winter': 0.3}
}

# Optional: Spezielle Tags berücksichtigen
# Beispiel: Parks → Sommerwert höher
for idx, row in pois.iterrows():
    sommer = 0.5
    winter = 0.5

    cat = row.get("category", "Sonstiges")
    w = season_weights.get(cat, {'sommer': 0.4, 'winter': 0.4})
    sommer = w['sommer']
    winter = w['winter']

    # Weitere Differenzierung je nach Tags
    tourism = row.get("tourism", "")
    leisure = row.get("leisure", "")
    amenity = row.get("amenity", "")

    if leisure in ["park", "garden"]:
        sommer = 1.0
        winter = 0.2
    elif tourism in ["viewpoint"]:
        sommer = 0.8
        winter = 0.1
    elif amenity in ["theatre", "cinema", "nightclub"]:
        sommer = 0.3
        winter = 0.9

    pois.at[idx, 'weight_sommer'] = round(sommer, 2)
    pois.at[idx, 'weight_winter'] = round(winter, 2)

# Speichern
output_path = 'data/processed/seasonal_pois.geojson'
pois.to_file(output_path, driver='GeoJSON')

print(f"Saisonale POI-Daten gespeichert unter: {output_path}")
