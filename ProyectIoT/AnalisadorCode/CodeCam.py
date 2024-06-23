import json
import cv2
import numpy as np
import requests
import time
import pytesseract

# Configura la ruta del ejecutable de Tesseract (ajusta según tu sistema)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Para Windows
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'  # Para macOS o Linux

# URL de la cámara ESP32
url = 'http://192.168.100.138'
#url = 'http://172.20.10.2'

# URL del servidor Flask
server_url = 'http://192.168.100.125:5000/receive_data'  # Cambia esto si el servidor está en una máquina diferente

# Función para capturar una imagen desde la cámara ESP32
def get_frame():
    timestamp = int(round(time.time() * 1000))
    response = requests.get(f'{url}/capture?_cb={timestamp}', stream=True)
    if response.status_code == 200:
        img_data = np.asarray(bytearray(response.raw.read()), dtype="uint8")
        frame = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        return frame
    else:
        print("Error al obtener el cuadro de video")
        return None

# Función para preprocesar la imagen
def preprocess_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
    return thresh

# Función para detectar y reconocer números en la imagen completa
def detect_and_recognize_numbers(frame):
    text = pytesseract.image_to_string(frame, config='--psm 6')
    text = ''.join(filter(str.isdigit, text))  # Filtra solo los dígitos
    return text

# Conjunto para almacenar secuencias detectadas
detected_sequences = set()

# Bucle principal
while True:
    frame = get_frame()
    if frame is not None:
        preprocessed_frame = preprocess_frame(frame)
        recognized_text = detect_and_recognize_numbers(preprocessed_frame)
        
        # Busca secuencias de 13 dígitos
        for i in range(len(recognized_text) - 12):
            sequence = recognized_text[i:i+13]
            if len(sequence) == 13 and sequence not in detected_sequences:
                detected_sequences.add(sequence)
                print(f"Encontrado 13 dígitos: {sequence}")

                # Enviar la secuencia al servidor Flask
                response = requests.post(server_url, json={"sequence": sequence})
                if response.status_code == 200:
                    print(f"Secuencia {sequence} enviada con éxito")
                else:
                    print(f"Error al enviar la secuencia {sequence}: {response.status_code}")
        
    else:
        print("Error al obtener el cuadro de video")

    # Espera entre escaneos
    time.sleep(1)  # Espera de 1 segundo entre cada intento de escaneo

    # Salir del bucle si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos y cerrar ventana de OpenCV
cv2.destroyAllWindows()
