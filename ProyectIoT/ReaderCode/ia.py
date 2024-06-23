import tensorflow as tf
import numpy as np
import pandas as pd
from itertools import combinations
from flask import Flask, request, jsonify

# Clase para predecir la suma de IDs
class IDSumPredictor:
    def __init__(self, productos_file, dataset_file, max_comb_size=3, epochs=250):
        # Leer los datos desde archivos Excel
        productos_df = pd.read_excel(productos_file, usecols=['id'])
        dataset_df = pd.read_excel(dataset_file, usecols=['val'])
        
        # Convertir los datos a arrays de numpy
        self.ids = productos_df['id'].to_numpy(dtype=float)
        self.suma_ids = dataset_df['val'].to_numpy(dtype=float)
        self.max_comb_size = max_comb_size

        # Generar combinaciones de tamaño limitado y sus sumas
        self.combs, self.sums = self.generar_combinaciones(self.ids, self.max_comb_size)
        self.combs = np.array([np.array(c) for c in self.combs], dtype=object)
        self.sums = np.array(self.sums, dtype=float)

        # Preparar datos para el modelo
        self.X = np.zeros((len(self.combs), len(self.ids)))
        for i, comb in enumerate(self.combs):
            for id in comb:
                self.X[i, int(id) - 1] = 1

        self.y = np.array(self.sums, dtype=float)

        # Definir y entrenar el modelo
        self.modelo = tf.keras.Sequential([
            tf.keras.layers.Dense(units=10, activation='relu', input_shape=[len(self.ids)]),
            tf.keras.layers.Dense(units=1)
        ])

        self.modelo.compile(
            optimizer=tf.keras.optimizers.Adam(0.1),
            loss='mean_squared_error'
        )

        # Entrenar el modelo
        print("Comenzando entrenamiento...")
        self.historial = self.modelo.fit(self.X, self.y, epochs=epochs, verbose=False)
        print("Modelo entrenado!")

        # Graficar el historial de pérdida
        import matplotlib.pyplot as plt
        plt.xlabel("# Epoca")
        plt.ylabel("Magnitud de pérdida")
        plt.plot(self.historial.history["loss"])
        plt.show()

    # Generar combinaciones de IDs y sus sumas
    def generar_combinaciones(self, ids, max_comb_size):
        combs = []
        sums = []
        for i in range(1, max_comb_size + 1):
            for comb in combinations(ids, i):
                combs.append(comb)
                sums.append(sum(comb))
        return combs, sums

    # Predecir la suma de una combinación de IDs
    def predecir_suma(self, ids_input):
        x_input = np.zeros((1, len(self.ids)))
        for id in ids_input:
            x_input[0, int(id) - 1] = 1
        resultado = self.modelo.predict(x_input)
        return round(resultado[0][0])  # Redondeo del resultado

# Inicializar el predictor con archivos de datos
predictor = IDSumPredictor('ProductosCode.xlsx', 'dataset.xlsx')

# Crear la aplicación Flask
app = Flask(__name__)

@app.route('/predecir', methods=['POST'])
def predecir():
    data = request.json
    ids_input = data.get('ids', [])
    resultado = predictor.predecir_suma(ids_input)
    return jsonify({'resultado': resultado})

if __name__ == '__main__':
    app.run(debug=True)
