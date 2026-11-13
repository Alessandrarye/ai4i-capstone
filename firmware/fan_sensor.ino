#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPmDNS.h>

const char* WIFI_SSID = "YOUR_WIFI_VALUE";
const char* WIFI_PASS = "YOUR_WIFI_VALUE";
String SERVER_URL = "";

const int MPU = 0x68;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected. IP address: ");
  Serial.println(WiFi.localIP());
    MDNS.begin("fan-sensor");
  IPAddress host = MDNS.queryHost("foundry");
  while (host == IPAddress(0, 0, 0, 0)) {
    Serial.println("looking for foundry.local...");
    delay(2000);
    host = MDNS.queryHost("foundry");
  }
  SERVER_URL = "http://" + host.toString() + ":8000/live-reading";
  Serial.println("posting to " + SERVER_URL);
}

float readMagnitude() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true);
  int16_t rawX = Wire.read() << 8 | Wire.read();
  int16_t rawY = Wire.read() << 8 | Wire.read();
  int16_t rawZ = Wire.read() << 8 | Wire.read();
  float ax = rawX / 16384.0;
  float ay = rawY / 16384.0;
  float az = rawZ / 16384.0;
  return sqrt(ax * ax + ay * ay + az * az);
}

void loop() {
  const int N = 100;
  float samples[N];
  float sum = 0;
  for (int i = 0; i < N; i++) {
    samples[i] = readMagnitude();
    sum += samples[i];
    delay(5);
  }
  float mean = sum / N;
  float varSum = 0;
  for (int i = 0; i < N; i++) {
    float d = samples[i] - mean;
    varSum += d * d;
  }
  float vibration = sqrt(varSum / N);

  Serial.print("vibration: ");
  Serial.println(vibration, 4);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    String body = "{\"vibration\": " + String(vibration, 4) + "}";
    int code = http.POST(body);
    Serial.print("POST status: ");
    Serial.println(code);
    http.end();
  }

  delay(1000);
}
