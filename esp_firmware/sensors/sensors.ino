#include <WiFi.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <time.h>

static const char* WIFI_SSID = "YOUR-SSID";
static const char* WIFI_PASS = "YOUR-PASSWORD";

// Time settings
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 0;       
const int daylightOffset_sec = 0;   

#define DHTPIN 4              // GPIO where DHT11 is connected
#define DHTTYPE DHT11         // DHT 11
#define SOIL_MOISTURE_PIN 34  // Analog pin for soil moisture sensor

DHT dht(DHTPIN, DHTTYPE);
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
  
  // Init and sync time
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("Failed to obtain time");
    return;
  }

  server.begin();
}

void loop() {
  WiFiClient client = server.available();

  if (client) {
    Serial.println("New Client.");
    String currentLine = "";

    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        currentLine += c;

        if (c == '\n') {
          float h = dht.readHumidity();
          float t = dht.readTemperature();
          int s = analogRead(SOIL_MOISTURE_PIN);

          // Get current timestamp
          struct tm timeinfo;
          char timeString[20];  // "YYYY-MM-DD HH:MM:SS"
          if (getLocalTime(&timeinfo)) {
            strftime(timeString, sizeof(timeString), "%Y-%m-%d %H:%M:%S", &timeinfo);
          } else {
            strcpy(timeString, "N/A");
          }

          // Debug info
          Serial.printf("Humidity: %.2f %%\tTemperature: %.2f °C\tSoil Moisture: %d\tTimestamp: %s\n", h, t, s, timeString);

          // Send JSON response
          client.println("HTTP/1.1 200 OK");
          client.println("Content-type: application/json");
          client.println();
          client.print("{\"temperature\": ");
          client.print(t);
          client.print(", \"humidity\": ");
          client.print(h);
          client.print(", \"soil_moisture\": ");
          client.print(s);
          client.print(", \"timestamp\": \"");
          client.print(timeString);
          client.println("\"}");

          break;
        }
      }
    }

    delay(1);
    client.stop();
    Serial.println("Client Disconnected.");
  }
}