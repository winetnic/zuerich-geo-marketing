"""
Direkte Visualisierung von Tourismus-Statistiken für Zürich
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_dummy_tourism_data():
    """Erstellt realistische Dummy-Daten für die Tourismus-Statistik"""
    print("Erstelle Dummy-Tourismus-Daten...")
    
    # Jährlicher Trend (2010-2023)
    years = list(range(2010, 2024))
    trend_values = [2800000, 2900000, 3100000, 3200000, 3400000, 
                   3300000, 3500000, 3700000, 3800000, 3900000,
                   3600000, 3100000, 3800000, 4000000]
    
    yearly_data = pd.DataFrame({
        'Jahr': years,
        'Logiernächte': trend_values
    })
    
    # Monatliche Verteilung für 2023
    months = list(range(1, 13))
    month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    
    monthly_values = [280000, 290000, 310000, 330000, 350000, 380000,
                     400000, 410000, 370000, 340000, 300000, 320000]
    
    monthly_data = pd.DataFrame({
        'Monat': months,
        'Monatsname': month_names,
        'Logiernächte': monthly_values
    })
    
    # Herkunftsländer für 2023
    countries = ['Schweiz', 'Deutschland', 'USA', 'Grossbritannien', 'China', 
                'Italien', 'Frankreich', 'Spanien', 'Niederlande', 'Andere']
    
    country_values = [1200000, 600000, 450000, 350000, 300000, 
                     250000, 220000, 180000, 150000, 300000]
    
    country_data = pd.DataFrame({
        'Herkunft': countries,
        'Logiernächte': country_values
    })
    
    return {
        'yearly': yearly_data,
        'monthly': monthly_data,
        'countries': country_data
    }

def visualize_yearly_trend(data):
    """Visualisiert den jährlichen Trend der Übernachtungen"""
    print("Erstelle Jahrestrend-Visualisierung...")
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=data, x='Jahr', y='Logiernächte', marker='o', linewidth=2.5)
    
    # Formatierung
    plt.title('Entwicklung der Übernachtungszahlen in Zürich', fontsize=16)
    plt.xlabel('Jahr', fontsize=12)
    plt.ylabel('Anzahl Logiernächte (Millionen)', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # Y-Achse in Millionen
    plt.ticklabel_format(axis='y', style='plain')
    plt.yticks([i for i in range(0, 5000001, 500000)], 
              [f'{i/1000000:.1f}' for i in range(0, 5000001, 500000)])
    
    # Speicherung
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/yearly_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Jahrestrend-Plot gespeichert: results/plots/yearly_trend.png")

def visualize_monthly_pattern(data):
    """Visualisiert die saisonale Verteilung der Übernachtungen"""
    print("Erstelle saisonale Verteilungs-Visualisierung...")
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=data, x='Monatsname', y='Logiernächte', palette='Blues_d')
    
    # Formatierung
    plt.title('Saisonale Verteilung der Übernachtungen in Zürich (2023)', fontsize=16)
    plt.xlabel('Monat', fontsize=12)
    plt.ylabel('Anzahl Logiernächte (Tausend)', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Y-Achse in Tausend
    plt.ticklabel_format(axis='y', style='plain')
    plt.yticks([i for i in range(0, 500001, 50000)], 
              [f'{i/1000:.0f}' for i in range(0, 500001, 50000)])
    
    # Werte über den Balken
    for i, p in enumerate(ax.patches):
        ax.annotate(f'{data.Logiernächte.iloc[i]/1000:.0f}k', 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'bottom', fontsize=9)
    
    # Speicherung
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/seasonal_pattern.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Saisonalitäts-Plot gespeichert: results/plots/seasonal_pattern.png")

def visualize_origin_countries(data):
    """Visualisiert die Herkunftsländer der Touristen"""
    print("Erstelle Herkunftsländer-Visualisierung...")
    
    # Nach Logiernächten sortieren
    data = data.sort_values('Logiernächte', ascending=True)
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=data, y='Herkunft', x='Logiernächte', palette='viridis')
    
    # Formatierung
    plt.title('Top 10 Herkunftsländer der Touristen in Zürich (2023)', fontsize=16)
    plt.xlabel('Anzahl Logiernächte (Tausend)', fontsize=12)
    plt.ylabel('Herkunftsland', fontsize=12)
    plt.grid(True, alpha=0.3, axis='x')
    
    # X-Achse in Tausend
    plt.ticklabel_format(axis='x', style='plain')
    plt.xticks([i for i in range(0, 1300001, 200000)], 
              [f'{i/1000:.0f}' for i in range(0, 1300001, 200000)])
    
    # Werte neben den Balken
    for i, p in enumerate(ax.patches):
        ax.annotate(f'{data.Logiernächte.iloc[i]/1000:.0f}k', 
                   (p.get_width(), p.get_y() + p.get_height()/2), 
                   ha = 'left', va = 'center', fontsize=10, fontweight='bold')
    
    # Speicherung
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/origin_countries.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Herkunftsländer-Plot gespeichert: results/plots/origin_countries.png")

def create_tourism_dashboard():
    """Erstellt ein Dashboard mit allen Visualisierungen"""
    print("Erstelle Tourism-Dashboard...")
    
    # Daten generieren
    data = create_dummy_tourism_data()
    
    # Einzelne Visualisierungen erstellen
    visualize_yearly_trend(data['yearly'])
    visualize_monthly_pattern(data['monthly'])
    visualize_origin_countries(data['countries'])
    
    # Kombiniertes Dashboard erstellen
    plt.figure(figsize=(18, 14))
    
    # Jahrestrend
    plt.subplot(3, 1, 1)
    sns.lineplot(data=data['yearly'], x='Jahr', y='Logiernächte', marker='o', linewidth=2.5)
    plt.title('Entwicklung der Übernachtungszahlen in Zürich', fontsize=14)
    plt.xlabel('Jahr', fontsize=10)
    plt.ylabel('Millionen', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.ticklabel_format(axis='y', style='plain')
    plt.yticks([i for i in range(0, 5000001, 1000000)], 
              [f'{i/1000000:.1f}' for i in range(0, 5000001, 1000000)])
    
    # Monatliche Verteilung
    plt.subplot(3, 1, 2)
    sns.barplot(data=data['monthly'], x='Monatsname', y='Logiernächte', palette='Blues_d')
    plt.title('Saisonale Verteilung der Übernachtungen (2023)', fontsize=14)
    plt.xlabel('Monat', fontsize=10)
    plt.ylabel('Tausend', fontsize=10)
    plt.grid(True, alpha=0.3, axis='y')
    plt.ticklabel_format(axis='y', style='plain')
    plt.yticks([i for i in range(0, 500001, 100000)], 
              [f'{i/1000:.0f}' for i in range(0, 500001, 100000)])
    
    # Herkunftsländer
    plt.subplot(3, 1, 3)
    sorted_countries = data['countries'].sort_values('Logiernächte', ascending=True)
    sns.barplot(data=sorted_countries, y='Herkunft', x='Logiernächte', palette='viridis')
    plt.title('Top 10 Herkunftsländer der Touristen (2023)', fontsize=14)
    plt.xlabel('Anzahl Logiernächte (Tausend)', fontsize=10)
    plt.ylabel('Herkunftsland', fontsize=10)
    plt.grid(True, alpha=0.3, axis='x')
    plt.ticklabel_format(axis='x', style='plain')
    plt.xticks([i for i in range(0, 1300001, 200000)], 
              [f'{i/1000:.0f}' for i in range(0, 1300001, 200000)])
    
    plt.tight_layout()
    
    # Speicherung
    os.makedirs('results/plots', exist_ok=True)
    plt.savefig('results/plots/tourism_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Tourism-Dashboard gespeichert: results/plots/tourism_dashboard.png")

def main():
    """Hauptfunktion zur Visualisierung der Tourismus-Statistikdaten"""
    print("\n=== Direkte Visualisierung der Zürcher Tourismus-Statistikdaten ===\n")
    
    # Dashboard erstellen
    create_tourism_dashboard()
    
    print("\nVisualisierung abgeschlossen. Plots wurden im Ordner 'results/plots' gespeichert.")

if __name__ == "__main__":
    main()