// ============================================================================
// Robô Garçom IoT com Câmera — ponto de entrada
// Hardware: AI-Thinker ESP32-CAM + OV2640 + ponte H (MX1508/L9110S) + 2 motores DC
//
// Fluxo:
//   1. Motores em repouso (antes de tudo, para o robô não sair andando)
//   2. Câmera OV2640
//   3. Wi-Fi em modo Ponto de Acesso (RoboGarcom-IoT -> 192.168.4.1)
//   4. Servidores HTTP (dashboard :80, vídeo :81)
//   5. OTA (atualização de firmware pelo Wi-Fi)
//   loop(): OTA + parada de segurança por timeout de comando
// ============================================================================

#include <Arduino.h>
#include <ArduinoOTA.h>
#include <WiFi.h>

#include "camera.h"
#include "config.h"
#include "motors.h"
#include "web_server.h"

namespace {

void statusLed(bool on) { digitalWrite(STATUS_LED_PIN, on ? LOW : HIGH); }  // lógica invertida

// Falha fatal: pisca o LED vermelho para sempre (diagnóstico sem monitor serial).
[[noreturn]] void haltWithBlink(uint32_t periodMs) {
  motors::stop();
  for (;;) {
    statusLed(true);
    delay(periodMs);
    statusLed(false);
    delay(periodMs);
  }
}

void startAccessPoint() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(WIFI_AP_SSID, WIFI_AP_PASSWORD, WIFI_AP_CHANNEL, 0, WIFI_AP_MAX_CLIENTS);
  WiFi.setSleep(false);  // economia de energia do rádio aumenta MUITO a latência
  Serial.printf("[NET] Rede \"%s\" criada. IP: %s\n", WIFI_AP_SSID,
                WiFi.softAPIP().toString().c_str());
}

void startOta() {
  ArduinoOTA.setHostname(OTA_HOSTNAME);
  ArduinoOTA.setPassword(OTA_PASSWORD);
  ArduinoOTA.onStart([] {
    motors::stop();  // nunca atualizar com o robô em movimento
    Serial.println("[OTA] Atualizacao iniciada");
  });
  ArduinoOTA.onEnd([] { Serial.println("[OTA] Concluida, reiniciando"); });
  ArduinoOTA.onError([](ota_error_t e) { Serial.printf("[OTA] Erro %u\n", e); });
  ArduinoOTA.begin();
  Serial.println("[OTA] Pronto para receber firmware na porta 3232");
}

}  // namespace

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("=== Robo Garcom IoT ===");

  // 1) Motores primeiro: deixa as entradas da ponte H em LOW o quanto antes.
  motors::begin();

  pinMode(STATUS_LED_PIN, OUTPUT);
  statusLed(false);

  // 2) Câmera — se falhar, pisca rápido (verifique cabo flat e alimentação).
  if (!camera::begin()) haltWithBlink(100);

  // 3) Rede e 4) servidores — se falhar, pisca devagar.
  startAccessPoint();
  if (!web::begin()) haltWithBlink(500);

  // 5) OTA
  startOta();

  statusLed(true);  // LED vermelho aceso fixo = tudo pronto
  Serial.println("[SYS] Pronto! Conecte-se ao Wi-Fi e abra http://192.168.4.1");
}

void loop() {
  ArduinoOTA.handle();
  motors::enforceTimeout();
  delay(10);
}
