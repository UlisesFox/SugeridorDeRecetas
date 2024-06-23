#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "Totalplay-25A5";
const char* password = "25A596DC6z9T9BXY";

WebServer server(80);

void handleRoot() {
  server.send(200, "text/plain", "Hola desde ESP32!");
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }
  Serial.println("Conectado a la red WiFi");

  server.on("/", handleRoot);
  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  server.handleClient();
}
