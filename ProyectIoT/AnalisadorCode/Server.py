import json
from flask import Flask, request, jsonify
import git
import os

# Definición de la ruta del directorio del repositorio y la URL del repositorio en GitHub
REPO_DIR = os.path.join(os.getcwd(), 'Codigos')
REPO_URL = 'https://github.com/UlisesFox/Codigos.git' 
JSON_FILE_PATH = os.path.join(REPO_DIR, 'codes.json')

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Ruta para recibir datos mediante una solicitud POST
@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json
    if "sequence" in data:
        sequence = data["sequence"]
        print(f"Recibido: {sequence}")
        update_json_file(sequence)
        return jsonify({"message": "Secuencia recibida"}), 200
    else:
        return jsonify({"message": "Datos no válidos"}), 400

# Función para actualizar el archivo JSON con la nueva secuencia
def update_json_file(sequence):
    # Clona el repositorio si no existe localmente
    if not os.path.exists(REPO_DIR):
        git.Repo.clone_from(REPO_URL, REPO_DIR)

    # Carga los datos existentes del archivo JSON si existe, de lo contrario, crea una lista vacía
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r') as file:
            data = json.load(file)
    else:
        data = []

    # Agrega la nueva secuencia a los datos
    data.append(sequence)

    # Guarda los datos actualizados en el archivo JSON
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

    # Realiza un commit y push de los cambios al repositorio remoto
    repo = git.Repo(REPO_DIR)
    repo.git.add(JSON_FILE_PATH)
    repo.index.commit(f'Agregado código {sequence}')
    origin = repo.remote(name='origin')
    origin.push()

# Ejecuta la aplicación Flask en el host 0.0.0.0 y puerto 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
