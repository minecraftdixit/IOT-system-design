#include "DHT.h"
#define DHTPIN D7 // what pin we're connected to
#define DHTTYPE DHT11 // DHT 11
DHT dht(DHTPIN, DHTTYPE);
// InfluxDB-related libraries and settings
#if defined(ESP32)
#include <WiFiMulti.h>
WiFiMulti wifiMulti;
#define DEVICE "ESP32"
#elif defined(ESP8266)
#include <ESP8266WiFiMulti.h>
ESP8266WiFiMulti wifiMulti;
#define DEVICE "ESP8266"
#endif
#include <InfluxDbClient.h>
#include <InfluxDbCloud.h>
// WiFi AP SSID
#define WIFI_SSID "iotla"
// WiFi password
#define WIFI_PASSWORD "878"
// InfluxDB v2 server URL, e.g.,
https://eu-central-1-1.aws.cloud2.influxdata.com (Use: InfluxDB UI -> Load
Data -> Client Libraries)
#define INFLUXDB_URL "https://us-eas.aws.cloud2.influxdata.com"

// InfluxDB v2 server or cloud API authentication token (Use: InfluxDB UI
-> Load Data -> Tokens -> <select token>)
#define INFLUXDB_TOKEN
"pW7wJTj5sk7A85gsJrH84o58MXkHk4wO2Bx6RCp9iY_HNOV3kCSIzFkhKRA779
Nq0ZUIoQA1Mjw=="
// InfluxDB v2 organization ID (Use: InfluxDB UI -> Settings -> Profile ->
<name under tile>)
#define INFLUXDB_ORG "346b795810f29"
// InfluxDB v2 bucket name (Use: InfluxDB UI -> Load Data -> Buckets)
#define INFLUXDB_BUCKET "ESP66"
// Set timezone string according to
https://www.gnu.org/software/libc/manual/html_node/TZ-Variable.html
#define TZ_INFO "CET-1CEST,M3.10.5.0/3"
// InfluxDB client instance with preconfigured InfluxCloud certificate
InfluxDBClient client(INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_BUCKET,
INFLUXDB_TOKEN, InfluxDbCloud2CACert);
Point sensor("temperature_status");
void setup() {
Serial.begin(115200);
// Setup Wi-Fi connection
WiFi.mode(WIFI_STA);
wifiMulti.addAP(WIFI_SSID, WIFI_PASSWORD);
Serial.print("Connecting to Wi-Fi...");
while (wifiMulti.run() != WL_CONNECTED) {
Serial.print(".");
delay(500);
}
Serial.println();
// Add tags
sensor.addTag("device", DEVICE);
sensor.addTag("SSID", WiFi.SSID());
// Sync time (necessary for certificate validation and data writing)

timeSync(TZ_INFO, "pool.ntp.org", "time.nis.gov");
// Check InfluxDB connection
if (client.validateConnection()) {
Serial.print("Connected to InfluxDB: ");
Serial.println(client.getServerUrl());
} else {
Serial.print("InfluxDB connection failed: ");
Serial.println(client.getLastErrorMessage());
}

dht.begin();
}
void loop() {
// Read humidity and temperature from DHT11 sensor
float humidity = dht.readHumidity();
float temperature = dht.readTemperature();
// Check for sensor read failure
if (isnan(humidity) || isnan(temperature)) {
Serial.println("Failed to read from DHT sensor!");
return;
}
sensor.clearFields();
sensor.addField("temperature", temperature);
sensor.addField("humidity", humidity);
// Print what is being written to InfluxDB
Serial.print("Writing: ");
Serial.println(client.pointToLineProtocol(sensor));
// If Wi-Fi is disconnected, try reconnecting
if (wifiMulti.run() != WL_CONNECTED) {
Serial.println("Wi-Fi connection lost");
}

// Write data to InfluxDB
if (!client.writePoint(sensor)) {
Serial.print("InfluxDB write failed: ");
Serial.println(client.getLastErrorMessage());
}
// Wait 10 seconds before sending the next reading
Serial.println("Waiting for 10s...");
delay(10000);
}
