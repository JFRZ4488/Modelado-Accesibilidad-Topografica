import pandas as pd
import networkx as nx
import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
import random

print("--- MÓDULO 5: ENRUTAMIENTO ÓPTIMO (DIJKSTRA) Y DIVERGENCIA ---")

aristas = pd.read_csv("grafo_pesos_semana6.csv")
aristas['geometry'] = aristas['geometry'].apply(wkt.loads)
gdf_aristas = gpd.GeoDataFrame(aristas, geometry='geometry')

aristas['T_Plano_min'] = aristas['length'] / (5000 / 60)

G = nx.from_pandas_edgelist(
    aristas, source='u', target='v', 
    edge_attr=['T_Plano_min', 'W_uv', 'length', 'geometry'], 
    create_using=nx.DiGraph()
)

# Búsqueda estocástica del escenario de máxima divergencia
nodos_lista = list(G.nodes())
max_divergencia = 0
mejor_origen, mejor_destino = None, None
mejor_ruta_plana, mejor_ruta_topo = [], []

for _ in range(300):
    u = random.choice(nodos_lista)
    v = random.choice(nodos_lista)
    if u != v and nx.has_path(G, u, v):
        ruta_p = nx.shortest_path(G, source=u, target=v, weight='T_Plano_min')
        ruta_t = nx.shortest_path(G, source=u, target=v, weight='W_uv')
        if len(ruta_p) < 15:
            continue
        diferencia = len(set(ruta_p).symmetric_difference(set(ruta_t)))
        if diferencia > max_divergencia:
            max_divergencia = diferencia
            mejor_origen, mejor_destino = u, v
            mejor_ruta_plana, mejor_ruta_topo = ruta_p, ruta_t

print(f"Escenario crítico hallado con {max_divergencia} nodos de divergencia espacial.")

def obtener_geometrias(ruta, gdf):
    aristas_ruta = []
    for i in range(len(ruta)-1):
        segmento = gdf[(gdf['u'] == ruta[i]) & (gdf['v'] == ruta[i+1])]
        if not segmento.empty:
            aristas_ruta.append(segmento.iloc[0])
    return gpd.GeoDataFrame(aristas_ruta, geometry='geometry')

gdf_ruta_plana = obtener_geometrias(mejor_ruta_plana, gdf_aristas)
gdf_ruta_topo = obtener_geometrias(mejor_ruta_topo, gdf_aristas)

# Renderizado cartográfico formal (Estilo Académico)
fig, ax = plt.subplots(figsize=(12, 10))
gdf_aristas.plot(ax=ax, color='#cccccc', linewidth=0.5, alpha=0.6, zorder=1)
gdf_ruta_plana.plot(ax=ax, color='#0055a4', linewidth=2.5, linestyle='--', zorder=4)
gdf_ruta_topo.plot(ax=ax, color='#b30000', linewidth=2.5, zorder=5)

origen_geom = gdf_ruta_topo.iloc[0].geometry.coords[0]
destino_geom = gdf_ruta_topo.iloc[-1].geometry.coords[-1]
ax.plot(origen_geom[0], origen_geom[1], marker='o', color='black', markersize=7, zorder=10)
ax.plot(destino_geom[0], destino_geom[1], marker='s', color='black', markersize=7, zorder=10)

ax.annotate('Origen', xy=origen_geom, xytext=(-15, 10), textcoords='offset points', fontsize=12, fontweight='bold')
ax.annotate('Destino', xy=destino_geom, xytext=(10, -15), textcoords='offset points', fontsize=12, fontweight='bold')

ax.set_facecolor('white')
ax.set_aspect('equal')
ax.axis('off')

import matplotlib.lines as mlines
l1 = mlines.Line2D([], [], color='#0055a4', linestyle='--', linewidth=2.5, label='Ruta Euclidiana (Plana)')
l2 = mlines.Line2D([], [], color='#b30000', linestyle='-', linewidth=2.5, label='Ruta Topográfica (Minimiza Impedancia)')
l3 = mlines.Line2D([], [], color='black', marker='o', linestyle='None', markersize=7, label='Nodo Origen')
l4 = mlines.Line2D([], [], color='black', marker='s', linestyle='None', markersize=7, label='Nodo Destino')
ax.legend(handles=[l1, l2, l3, l4], loc='lower right', fontsize=11, frameon=True, facecolor='white', edgecolor='black')

plt.tight_layout()
print("[OK] Módulo 5 finalizado. Visualización generada.")
plt.show()