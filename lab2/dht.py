#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Arduino_JSON.h>
#include "DHT.h"
#include <ESP8266mDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

// WiFi credentials
#ifndef STASSID
#define STASSID "DESKTOP"
#define STAPSK "18261826"
#endif
const char* ssid = STASSID;
const char* password = STAPSK;

// ThinkSpeak API details
String serverName_send = "http://api.thingspeak.com/update?api_key=0TFQH1ND";

// DHT sensor details
#define DHTPIN D7     // what pin we're connected to
#define DHTTYPE DHT11 // DHT 11
DHT dht(DHTPIN, DHTTYPE);

// Timer delay (20 seconds)
unsigned long lastTime = 0;
unsigned long timerDelay = 20000;

void setup() {
  Serial.begin(115200);

  // Initialize DHT sensor
  dht.begin();

  // Connect to WiFi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("Connection Failed! Rebooting...");
    delay(5000);
    ESP.restart();
  }

  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());

  // Setup OTA updates
  ArduinoOTA.onStart([]() {
    String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
    Serial.println("Start updating " + type);
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });

  ArduinoOTA.begin();
  Serial.println("OTA Ready");
}

void loop() {
  // Handle OTA updates
  ArduinoOTA.handle();

  // Check if 20 seconds have passed
  if ((millis() - lastTime) > timerDelay) {
    // Check WiFi connection status
    if (WiFi.status() == WL_CONNECTED) {

      // Read data from the DHT sensor
      float humidity = dht.readHumidity();
      float temperature = dht.readTemperature(); // Celsius

      // Check if any reads failed
      if (isnan(humidity) || isnan(temperature)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
      }

      // Debug print DHT sensor values
      Serial.print("Humidity: ");
      Serial.print(humidity);
      Serial.print(" %\t");
      Serial.print("Temperature: ");
      Serial.print(temperature);
      Serial.println(" *C");

      // Generate a random number (in this case, 34)
      int randomNumber = 138; // You can change this to generate random numbers using random() if needed

      // Create ThinkSpeak URL with DHT sensor data and random number
      WiFiClient client;
      HTTPClient http;

      String serverPath_send = serverName_send + "&field1=" + String(temperature)
                                               + "&field2=" + String(humidity)
                                               + "&field3=" + String(randomNumber);
      
      // Send the HTTP GET request to ThinkSpeak
      http.begin(client, serverPath_send.c_str());
      int httpResponseCode = http.GET();

      // Handle HTTP response
      if (httpResponseCode > 0) {
        Serial.print("HTTP Response code: ");
        Serial.println(httpResponseCode);
        String payload = http.getString();
        Serial.println(payload);
      } else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }

      // Free resources
      http.end();
    } else {
      Serial.println("WiFi Disconnected");
    }

    // Update lastTime to current time
    lastTime = millis();
  }

  // You can also add other functionality like blinking an LED
  digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED on
  delay(100);                       // Wait for a short period
  digitalWrite(LED_BUILTIN, LOW);   // Turn the LED off
  delay(100); 
}
