import pandas as pd
import networkx as nx
import scipy.sparse as sparse

print("--- MÓDULO 4: VALIDACIÓN ESTADÍSTICA Y MATRIZ DISPERSA ---")

aristas = pd.read_csv("grafo_pesos_semana6.csv")

# 1. Cálculo del modelo plano de referencia (5 km/h -> 83.33 m/min)
velocidad_plana_m_min = 5000 / 60 
aristas['T_Plano_min'] = aristas['length'] / velocidad_plana_m_min
aristas['T_Real_min'] = aristas['W_uv']

# 2. Métricas descriptivas globales
stats_plano = aristas['T_Plano_min'].describe()
stats_real = aristas['T_Real_min'].describe()
aumento_total = ((aristas['T_Real_min'].sum() - aristas['T_Plano_min'].sum()) / aristas['T_Plano_min'].sum()) * 100

comparativa = pd.DataFrame({
    'Métrica': ['Media', 'Mediana', 'Desviación Estándar', 'Valor Máximo', 'Suma Total'],
    'Modelo Plano [min]': [stats_plano['mean'], stats_plano['50%'], stats_plano['std'], stats_plano['max'], aristas['T_Plano_min'].sum()],
    'Modelo Topográfico [min]': [stats_real['mean'], stats_real['50%'], stats_real['std'], stats_real['max'], aristas['T_Real_min'].sum()]
})
print("\n", comparativa.round(2).to_string(index=False))
print(f"\nIncremento global del costo motriz por relieve: {aumento_total:.2f}%")

# 3. Construcción del Grafo y exportación de matriz dispersa (SciPy)
G = nx.from_pandas_edgelist(aristas, source='u', target='v', edge_attr=['W_uv'], create_using=nx.DiGraph())
matriz_adyacencia = nx.to_scipy_sparse_array(G, weight='W_uv')
sparse.save_npz("matriz_adyacencia_semana6.npz", matriz_adyacencia)

print("[OK] Módulo 4 finalizado. Matriz dispersa exportada.")