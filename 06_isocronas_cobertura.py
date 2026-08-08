import pandas as pd
import networkx as nx
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt

print("--- MÓDULO 6: ISOCRONAS DE COBERTURA (CORRECCIÓN DE CENTROS URBANOS) ---")

# 1. CARGA DE DATOS
try:
    aristas = pd.read_csv("grafo_pesos_semana6.csv")
    nodos = pd.read_csv("modelo_nodos_3D.csv")
except FileNotFoundError:
    print("[ERROR] Faltan archivos base. Ejecuta los módulos anteriores.")
    exit()

aristas['geometry'] = aristas['geometry'].apply(wkt.loads)
gdf_aristas = gpd.GeoDataFrame(aristas, geometry='geometry')

# 2. CONSTRUCCIÓN DEL GRAFO
G = nx.from_pandas_edgelist(aristas, source='u', target='v', edge_attr=['W_uv'], create_using=nx.DiGraph())

# 3. SELECCIÓN GEOGRÁFICA EXACTA DE LOS CASCOS URBANOS
# San Antonio de Flores se ubica en el extremo norte (zona de alta concentración observada).
# Pespire se ubica en la zona sur-central.
nodos_norte = nodos[nodos['y'] > nodos['y'].quantile(0.75)]
nodos_sur = nodos[(nodos['y'] >= nodos['y'].quantile(0.3)) & (nodos['y'] <= nodos['y'].quantile(0.6))]

grado_nodos = dict(G.degree())

# Seleccionamos el nodo con mayor grado (intersección principal) dentro de los clústers correctos
nodo_san_antonio = max((n for n in nodos_norte['osmid'] if n in grado_nodos), key=grado_nodos.get)
nodo_pespire = max((n for n in nodos_sur['osmid'] if n in grado_nodos), key=grado_nodos.get)

centros = {
    "San Antonio de Flores": nodo_san_antonio,
    "Pespire": nodo_pespire
}

# 4. CONFIGURACIÓN DEL LIENZO DUAL (LIMPIO DE SOBRECARGA)
fig, axes = plt.subplots(1, 2, figsize=(20, 10))
fig.suptitle("Fronteras de Accesibilidad Territorial (Isocronas Topográficas)", 
             fontsize=16, fontweight='bold')

for ax, (nombre, nodo_origen) in zip(axes, centros.items()):
    print(f"\nCalculando isocronas para el casco urbano: {nombre} (Nodo {nodo_origen})")
    
    # Algoritmo de Dijkstra para acumular impedancias reales W(u,v)
    tiempos_viaje = nx.single_source_dijkstra_path_length(G, nodo_origen, weight='W_uv')
    
    nodos_30m = [n for n, t in tiempos_viaje.items() if t <= 30]
    nodos_60m = [n for n, t in tiempos_viaje.items() if 30 < t <= 60]
    nodos_120m = [n for n, t in tiempos_viaje.items() if 60 < t <= 120]
    
    # Fondo de la red completa (Gris tenue)
    gdf_aristas.plot(ax=ax, color='#e0e0e0', linewidth=0.5, zorder=1)
    
    def graficar_isocrona(nodos_iso, color, z):
        aristas_iso = aristas[aristas['u'].isin(nodos_iso) & aristas['v'].isin(nodos_iso)]
        if not aristas_iso.empty:
            gdf_iso = gpd.GeoDataFrame(aristas_iso, geometry='geometry')
            gdf_iso.plot(ax=ax, color=color, linewidth=2.5, zorder=z)

    # Superposición jerárquica de isocronas
    graficar_isocrona(nodos_30m + nodos_60m + nodos_120m, '#ffcc00', 2)
    graficar_isocrona(nodos_30m + nodos_60m, '#ff6600', 3)
    graficar_isocrona(nodos_30m, '#cc0000', 4)
    
    # Ubicación exacta del origen métrico
    segmento_origen = gdf_aristas[gdf_aristas['u'] == nodo_origen].iloc[0]
    coord_x, coord_y = segmento_origen.geometry.coords[0]
    ax.plot(coord_x, coord_y, marker='X', color='black', markersize=12, zorder=10)
    
    ax.set_title(f"Centro Neurálgico: {nombre}", fontsize=14, fontweight='bold')
    ax.set_facecolor('white')
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Leyenda limpia, sobria y profesional
    import matplotlib.lines as mlines
    l1 = mlines.Line2D([], [], color='#cc0000', linewidth=3.5, label='< 30 min (v variable)')
    l2 = mlines.Line2D([], [], color='#ff6600', linewidth=3.5, label='< 60 min (v variable)')
    l3 = mlines.Line2D([], [], color='#ffcc00', linewidth=3.5, label='< 120 min (v variable)')
    l4 = mlines.Line2D([], [], color='black', marker='X', linestyle='None', markersize=8, label='Casco Urbano')
    
    ax.legend(handles=[l1, l2, l3, l4], loc='lower right', fontsize=11, frameon=True, edgecolor='black')

plt.tight_layout()
plt.show()