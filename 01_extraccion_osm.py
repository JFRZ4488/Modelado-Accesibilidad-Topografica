import geopandas as gpd
import matplotlib.pyplot as plt
import osmnx as ox
import rasterio
from rasterio.mask import mask
import numpy as np
import pandas as pd

print("--- MÓDULO 1: EXTRACCIÓN ESPACIAL Y RECÓRTE DEL DEM ---")

# 1. Lectura y filtrado estricto de municipios
ruta_geojson = "hnd_admin_boundaries.geojson/hnd_admin2.geojson"
honduras = gpd.read_file(ruta_geojson)

municipios_objetivo = ['San Antonio de Flores', 'Pespire']
municipio = honduras[
    (honduras['adm2_name'].isin(municipios_objetivo)) & 
    (honduras['adm1_name'] == 'Choluteca')
]

# 2. Descarga de la red vial exclusiva
print("Descargando red de caminos desde OpenStreetMap...")
poligono_geometria = municipio.geometry.unary_union
grafo_caminos = ox.graph_from_polygon(poligono_geometria, network_type='all')

# 3. Lectura y corrección de valores nulos del DEM
print("Calibrando Modelo Digital de Elevación (DEM)...")
ruta_dem = "n13_w088_1arc_v3.tif" 

with rasterio.open(ruta_dem) as src:
    dem_recortado, transformacion = mask(src, [poligono_geometria], crop=True)
    dem_recortado = dem_recortado[0]
    
    valor_nodata = src.nodata
    if valor_nodata is not None:
        dem_recortado = np.where(dem_recortado == valor_nodata, np.nan, dem_recortado)
    else:
        dem_recortado = np.where(dem_recortado < 0, np.nan, dem_recortado)

# 4. Extracción de bases de datos tabulares (Nodos y Aristas)
nodos, aristas = ox.graph_to_gdfs(grafo_caminos)
aristas = aristas.reset_index()
nodos = nodos.reset_index()

aristas.to_csv("base_aristas.csv", index=False)
nodos.to_csv("base_nodos.csv", index=False)
municipio.to_csv("base_municipio.csv", index=False)

print("[OK] Módulo 1 finalizado. Archivos base exportados.")