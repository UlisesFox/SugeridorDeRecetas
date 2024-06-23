import tensorflow as tf
import numpy as np
import pandas as pd
from itertools import combinations

# Leer los datos desde archivos Excel
productos_df = pd.read_excel('ProductosCode.xlsx', usecols=['id'])
dataset_df = pd.read_excel('dataset.xlsx', usecols=['Suma de IDs'])

# Convertir los datos a arrays de numpy
ids = productos_df['id'].to_numpy(dtype=float)
suma_ids = dataset_df['Suma de IDs'].to_numpy(dtype=float)

# Generar combinaciones de tamaño limitado (hasta 3 elementos) y sus sumas
def generar_combinaciones(ids, max_comb_size=3):
    combs = []
    sums = []
    for i in range(1, max_comb_size + 1):
        for comb in combinations(ids, i):
            combs.append(comb)
            sums.append(sum(comb))
    return combs, sums

combs, sums = generar_combinaciones(ids, max_comb_size=3)
combs = np.array([np.array(c) for c in combs], dtype=object)
sums = np.array(sums, dtype=float)

# Preparar datos para el modelo
X = np.zeros((len(combs), len(ids)))
for i, comb in enumerate(combs):
    for id in comb:
        X[i, int(id) - 1] = 1

y = np.array(sums, dtype=float)

# Definir el modelo
modelo = tf.keras.Sequential([
    tf.keras.layers.Dense(units=10, activation='relu', input_shape=[len(ids)]),
    tf.keras.layers.Dense(units=1)
])

modelo.compile(
    optimizer=tf.keras.optimizers.Adam(0.1),
    loss='mean_squared_error'
)

# Entrenar el modelo
print("Comenzando entrenamiento...")
historial = modelo.fit(X, y, epochs=150, verbose=False)
print("Modelo entrenado!")

# Graficar la pérdida
import matplotlib.pyplot as plt
plt.xlabel("# Epoca")
plt.ylabel("Magnitud de pérdida")
plt.plot(historial.history["loss"])
plt.show()

# Función para predecir la suma dada una combinación de IDs
def predecir_suma(ids_input):
    x_input = np.zeros((1, len(ids)))
    for id in ids_input:
        x_input[0, int(id) - 1] = 1
    resultado = modelo.predict(x_input)
    return round(resultado[0][0])  # Redondeo del resultado

# Ejemplo de predicción
print("Hagamos una predicción!")
ids_input = [1, 2, 3]
resultado = predecir_suma(ids_input)
print(f"El resultado para los IDs {ids_input} es {resultado}!")

# Ver pesos internos del modelo
for layer in modelo.layers:
    print(layer.get_weights())
