import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import requests

# Función para enviar los IDs a un servidor y obtener un resultado predicho
def predecir_suma(ids):
    url = 'http://127.0.0.1:5000/predecir'
    data = {'ids': ids}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['resultado']
    else:
        raise Exception(f"Error en la solicitud: {response.status_code}")

while True:
    # Cargar el archivo Excel en un DataFrame de pandas
    df = pd.read_excel("./Codigos/Codes.xlsx")
    print(df.columns)
    print("")
    print(df)

    # Convertir la columna 'Fecha completa' a un array de numpy
    order_date = np.array(df['Fecha completa'])
    print('\n' + 'Fecha completa', type(order_date), order_date.dtype)
    print("")
    print(order_date)
    print("")

    # Convertir las fechas a formato 'datetime64[D]'
    order_date_deily = np.array(order_date, dtype='datetime64[D]')
    print(order_date_deily)
    print("")
    print(np.unique(order_date_deily))
    print("")
    print(len(np.unique(order_date_deily)))
    print("")

    # Definir las rutas de los archivos Excel
    codes_file_path = "./Codigos/Codes.xlsx"
    product_codes_file_path = "ProductosCode.xlsx"

    # Cargar los archivos Excel en DataFrames de pandas
    df = pd.read_excel(codes_file_path)
    pf = pd.read_excel(product_codes_file_path)

    # Limpiar la columna 'codigo' en el DataFrame de productos
    pf['codigo'] = pf['codigo'].apply(lambda x: ''.join(re.findall(r'\d+', str(x))))

    # Asegurar que las columnas 'codigo' sean de tipo string
    df['codigo'] = df['codigo'].astype(str)
    pf['codigo'] = pf['codigo'].astype(str)

    # Encontrar la intersección entre los dos DataFrames en la columna 'codigo'
    interseccion = pd.merge(pf, df, on='codigo', how='inner')

    print(interseccion)
    print('')

    # Extraer los IDs y nombres de productos de la intersección
    ids = interseccion['id'].tolist()
    productos = interseccion['ingrediente'].tolist()

    print(productos)

    # Enviar los IDs al servidor y obtener el resultado predicho
    resultado = predecir_suma(ids)

    # Cargar otro archivo Excel en un DataFrame
    dataset_path = "dataset.xlsx"
    dataset = pd.read_excel(dataset_path)

    # Crear un DataFrame con el resultado predicho
    resultado_df = pd.DataFrame({'val': [resultado]})
    merge_result_id = pd.merge(dataset, resultado_df, on='val', how='inner')

    print("Las recetas que le recomiendo son:")
    print(merge_result_id)

    # Crear un gráfico de caja para visualizar la cantidad por fecha
    sns.boxplot(x="Fecha completa", y="Cantidad", data=df)
    plt.show()

    # Esperar 25 segundos antes de repetir el proceso
    time.sleep(25)
