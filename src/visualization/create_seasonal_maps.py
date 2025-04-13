import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import os

# Daten laden
print("Lade Daten für saisonale Karten...")
try:
    zurich_boundary = gpd.read_file('data/raw/zurich_boundary.geojson').to_crs(epsg=3857)
    print("Zürich-Grenzen geladen")
except Exception as e:
    print(f"Fehler beim Laden der Zürich-Grenzen: {e}")
    # Erstelle einen leeren GeoDataFrame als Fallback
    zurich_boundary = gpd.GeoDataFrame()

try:
    seasonal_pois = gpd.read_file('data/processed/seasonal_pois.geojson').to_crs(epsg=3857)
    print(f"Saisonale POIs geladen: {len(seasonal_pois)}")
except Exception as e:
    print(f"Fehler beim Laden der saisonalen POIs: {e}")
    print("Beende Skript, da saisonale Daten fehlen.")
    exit(1)

# Prüfen, ob die erwarteten Spalten vorhanden sind
required_columns = ['weight_sommer', 'weight_winter', 'category']
missing_columns = [col for col in required_columns if col not in seasonal_pois.columns]

if missing_columns:
    print(f"Fehlende Spalten in den saisonalen Daten: {missing_columns}")
    print("Verfügbare Spalten:", seasonal_pois.columns.tolist())
    # Erstelle Dummy-Spalten für fehlende Spalten
    for col in missing_columns:
        if col.startswith('weight_'):
            seasonal_pois[col] = 0.5  # Standardgewicht
        else:
            seasonal_pois[col] = 'Unknown'  # Standardkategorie
    print("Dummy-Spalten wurden erstellt.")

# Saisonale Karten erstellen
seasons = ['sommer', 'winter']
print("Erstelle saisonale Karten...")

for season in seasons:
    print(f"Erstelle Karte für {season.capitalize()}...")
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Hintergrund und Grenzen
    if not zurich_boundary.empty:
        zurich_boundary.plot(ax=ax, alpha=0.5, edgecolor='k')
    
    # POIs mit saisonaler Gewichtung
    weight_col = f'weight_{season}'
    
    # Sicherstellen, dass die Spalte existiert und numerisch ist
    if weight_col in seasonal_pois.columns and seasonal_pois[weight_col].dtype in ['float64', 'int64']:
        # Erstelle ein neues GeoDataFrame mit nur validen Geometrien
        valid_pois = seasonal_pois[seasonal_pois.geometry.is_valid]
        
        # Plotte die POIs
        valid_pois.plot(
            ax=ax,
            column=weight_col,
            cmap='viridis',
            markersize=valid_pois[weight_col] * 100,  # Größe proportional zur Gewichtung
            legend=True,
            legend_kwds={'label': f'Besucheranteil {season.capitalize()}'},
            alpha=0.7
        )
    else:
        print(f"Warnung: Spalte '{weight_col}' nicht verfügbar oder nicht numerisch.")
        # Plotte einfache Punkte ohne Farbcodierung
        seasonal_pois.plot(ax=ax, alpha=0.7)
    
    # Basemap hinzufügen
    try:
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
    except Exception as e:
        print(f"Hintergrundkarte konnte nicht hinzugefügt werden: {e}")
    
    # Titel und Layout
    plt.title(f'Touristische Aktivität in Zürich - {season.capitalize()}', fontsize=16)
    plt.tight_layout()
    
    # Speichern
    output_dir = 'results/maps'
    os.makedirs(output_dir, exist_ok=True)
    output_path = f'{output_dir}/zurich_tourism_{season}.png'
    plt.savefig(output_path, dpi=300)
    print(f"Karte für {season} gespeichert unter: {output_path}")
    plt.close()

print("Saisonale Karten wurden erstellt.")