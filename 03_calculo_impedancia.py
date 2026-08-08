import pandas as pd
import numpy as np

print("--- MÓDULO 3: MATRIZ DE IMPEDANCIA Y PESOS ASIMÉTRICOS ---")

aristas = pd.read_csv("modelo_aristas_3D.csv")

# 1. Definición de la función de Tobler (Tensor cinemático inverso)
def Phi(s):
    return 1 / (6 * np.exp(-3.5 * np.abs(s + 0.05)))

aristas['phi_s'] = Phi(aristas['pendiente_s'])

# 2. Factores de fricción superficial multicriterio
diccionario_friccion = {
    'trunk': 1.0, 'primary': 1.0, 'secondary': 1.0, 'tertiary': 1.0, 
    'residential': 1.0, 'unclassified': 1.2, 'service': 1.2, 
    'track': 1.2, 'path': 1.5, 'footway': 1.5, 'steps': 1.5
}
aristas['f_uv'] = aristas['highway'].map(diccionario_friccion).fillna(1.5)

# 3. Cálculo de la ecuación estricta de costo W(u,v) en minutos (con factor 0.06 integrado)
aristas['W_uv'] = aristas['distancia_ds'] * aristas['phi_s'] * aristas['f_uv'] * 0.06

aristas.to_csv("grafo_pesos_semana6.csv", index=False)
print("[OK] Módulo 3 finalizado. Grafo ponderado definitivo guardado.")