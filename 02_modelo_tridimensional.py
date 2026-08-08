import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
import osmnx as ox

print("--- MÓDULO 2: REPROYECCIÓN MÉTRICA (UTM 16N) Y CÁLCULO 3D ---")

nodos = pd.read_csv("base_nodos.csv")
aristas = pd.read_csv("base_aristas.csv")

# 1. Extracción de la elevación (z) desde el DEM
print("Muestreando elevaciones (z) del DEM...")
ruta_dem = "n13_w088_1arc_v3.tif"
coordenadas = [(x, y) for x, y in zip(nodos['x'], nodos['y'])]

with rasterio.open(ruta_dem) as src:
    elevaciones = [val[0] for val in src.sample(coordenadas)]

nodos['z'] = elevaciones
nodos['z'] = np.where(nodos['z'] < -100, np.nan, nodos['z'])
nodos['z'] = nodos['z'].fillna(nodos['z'].mean())

# 2. Reproyección estricta a UTM Zona 16N
print("Reproyectando grafo a coordenadas métricas (EPSG:32616)...")
grafo_temporal = ox.graph_from_gdfs(
    gpd.GeoDataFrame(nodos, geometry=gpd.points_from_xy(nodos.x, nodos.y), crs="EPSG:4326").set_index('osmid'), 
    gpd.GeoDataFrame(aristas, geometry=gpd.GeoSeries.from_wkt(aristas['geometry']), crs="EPSG:4326").set_index(['u', 'v', 'key'])
)

grafo_proyectado = ox.project_graph(grafo_temporal)
nodos_utm, aristas_utm = ox.graph_to_gdfs(grafo_proyectado)
aristas_utm = aristas_utm.reset_index()
nodos_utm = nodos_utm.reset_index()

# 3. Fusión topológica y cálculo de variables físicas
mapa_elevaciones = nodos_utm.set_index('osmid')['z']
aristas_utm['z_u'] = aristas_utm['u'].map(mapa_elevaciones)
aristas_utm['z_v'] = aristas_utm['v'].map(mapa_elevaciones)

aristas_utm['dz'] = aristas_utm['z_v'] - aristas_utm['z_u']
aristas_utm['pendiente_s'] = np.where(aristas_utm['length'] > 0, aristas_utm['dz'] / aristas_utm['length'], 0)
aristas_utm['distancia_ds'] = np.sqrt(aristas_utm['length']**2 + aristas_utm['dz']**2)

aristas_utm.to_csv("modelo_aristas_3D.csv", index=False)
nodos_utm.to_csv("modelo_nodos_3D.csv", index=False)

print("[OK] Módulo 2 finalizado. Espacio métrico consolidado.")