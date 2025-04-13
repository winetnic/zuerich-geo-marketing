import pandas as pd
import requests
from io import StringIO
import os

print("Sammle statistische Daten für Zürich...")

# Sicherstellen, dass das Verzeichnis existiert
os.makedirs('data/raw', exist_ok=True)

# URLs für statistische Daten der Stadt Zürich
# Hinweis: Dies sind Beispiel-URLs, ersetzen Sie sie durch aktuelle Quellen
urls = {
    "tourism_stats": "https://data.stadt-zuerich.ch/dataset/tourism_stats.csv",
    "overnight_stats": "https://data.stadt-zuerich.ch/dataset/overnight_stats.csv"
}

# Dummy-Daten erstellen, falls die Daten nicht verfügbar sind
def create_dummy_data(data_type):
    print(f"Erstelle Beispieldaten für {data_type}...")
    
    if data_type == "tourism_stats":
        # Beispieldaten für Tourismusstatistik
        months = range(1, 13)
        years = [2022, 2023]
        data = []
        
        for year in years:
            for month in months:
                visitors = 10000 + (month * 1000) + (year - 2022) * 5000
                data.append({
                    "year": year,
                    "month": month,
                    "visitors": visitors,
                    "district": "Stadt Zürich",
                    "average_stay": 2.5 + (month % 3) * 0.2
                })
        
        return pd.DataFrame(data)
    
    elif data_type == "overnight_stats":
        # Beispieldaten für Übernachtungsstatistik
        months = range(1, 13)
        countries = ["Schweiz", "Deutschland", "USA", "UK", "China", "Japan"]
        data = []
        
        for country in countries:
            for month in months:
                overnight_stays = 5000 + (month * 500) + (countries.index(country) * 1000)
                data.append({
                    "month": month,
                    "country": country,
                    "overnight_stays": overnight_stays,
                    "avg_duration": 1.8 + (countries.index(country) * 0.3)
                })
        
        return pd.DataFrame(data)
    
    return pd.DataFrame()

# Daten herunterladen oder Dummy-Daten erstellen
datasets = {}

for name, url in urls.items():
    print(f"Versuche, {name} von {url} zu laden...")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            datasets[name] = pd.read_csv(StringIO(response.text))
            print(f"{name} erfolgreich geladen.")
        else:
            print(f"Fehler beim Laden von {name}: HTTP Status {response.status_code}")
            datasets[name] = create_dummy_data(name)
    except Exception as e:
        print(f"Fehler beim Laden von {name}: {e}")
        datasets[name] = create_dummy_data(name)

# Daten nach Stadtbezirken filtern (falls entsprechende Spalte vorhanden)
for name, df in datasets.items():
    if 'district' in df.columns:
        print(f"Filtere {name} nach Stadtbezirken von Zürich...")
        # Hier könnten Sie nach bestimmten Bezirken filtern
        # df = df[df['district'].isin(['Bezirk1', 'Bezirk2', ...])]

# Daten speichern
for name, df in datasets.items():
    file_path = f'data/raw/{name}.csv'
    df.to_csv(file_path, index=False)
    print(f"{name} gespeichert unter {file_path} mit {len(df)} Einträgen.")

print("Statistische Datensammlung abgeschlossen.")