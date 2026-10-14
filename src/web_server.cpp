#include "web_server.h"

#include <WiFi.h>
#include <esp_camera.h>
#include <esp_http_server.h>

#include "config.h"
#include "dashboard_html.h"
#include "motors.h"

namespace web {
namespace {

#define PART_BOUNDARY "robogarcomframe"
const char* kStreamContentType = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
const char* kStreamBoundary = "\r\n--" PART_BOUNDARY "\r\n";
const char* kStreamPartHeader = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

httpd_handle_t gControlServer = nullptr;
httpd_handle_t gStreamServer = nullptr;
volatile float gStreamFps = 0;
volatile bool gFlashOn = false;

// Lê um parâmetro da query string (?chave=valor). Retorna false se ausente.
bool queryParam(httpd_req_t* req, const char* key, char* out, size_t outLen) {
  char query[96];
  if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK) return false;
  return httpd_query_key_value(query, key, out, outLen) == ESP_OK;
}

esp_err_t sendText(httpd_req_t* req, const char* status, const char* body) {
  httpd_resp_set_status(req, status);
  httpd_resp_set_type(req, "text/plain");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  return httpd_resp_send(req, body, HTTPD_RESP_USE_STRLEN);
}

// GET / -> página do dashboard
esp_err_t handleIndex(httpd_req_t* req) {
  httpd_resp_set_type(req, "text/html; charset=utf-8");
  return httpd_resp_send(req, DASHBOARD_HTML, HTTPD_RESP_USE_STRLEN);
}

// GET /cmd?dir=forward&speed=70 -> move o robô
esp_err_t handleCommand(httpd_req_t* req) {
  char dirText[16];  // cabe "backward_right" (14) + terminador
  char speedText[8];
  if (!queryParam(req, "dir", dirText, sizeof(dirText))) {
    return sendText(req, "400 Bad Request", "faltou ?dir=");
  }
  motors::Direction dir;
  if (!motors::parseDirection(dirText, dir)) {
    return sendText(req, "400 Bad Request", "dir invalido");
  }
  int speed = 70;
  if (queryParam(req, "speed", speedText, sizeof(speedText))) {
    speed = constrain(atoi(speedText), 0, 100);
  }
  motors::drive(dir, static_cast<uint8_t>(speed));
  return sendText(req, "200 OK", "ok");
}

// GET /flash?on=1 -> liga/desliga o LED de flash
esp_err_t handleFlash(httpd_req_t* req) {
  char value[4];
  if (!queryParam(req, "on", value, sizeof(value))) {
    return sendText(req, "400 Bad Request", "faltou ?on=");
  }
  gFlashOn = (value[0] == '1');
  digitalWrite(FLASH_LED_PIN, gFlashOn ? HIGH : LOW);
  return sendText(req, "200 OK", gFlashOn ? "on" : "off");
}

// GET /status -> JSON com telemetria básica para o dashboard
esp_err_t handleStatus(httpd_req_t* req) {
  char json[192];
  snprintf(json, sizeof(json),
           "{\"uptime_s\":%lu,\"clients\":%d,\"fps\":%.1f,\"heap_kb\":%u,"
           "\"psram\":%s,\"dir\":\"%s\",\"flash\":%s}",
           static_cast<unsigned long>(millis() / 1000), WiFi.softAPgetStationNum(),
           static_cast<double>(gStreamFps), static_cast<unsigned>(ESP.getFreeHeap() / 1024),
           psramFound() ? "true" : "false", motors::directionName(motors::currentDirection()),
           gFlashOn ? "true" : "false");
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");
  return httpd_resp_send(req, json, HTTPD_RESP_USE_STRLEN);
}

// GET :81/stream -> MJPEG: sequência infinita de JPEGs separados por "boundary".
// O navegador exibe isso nativamente em uma tag <img>.
esp_err_t handleStream(httpd_req_t* req) {
  esp_err_t res = httpd_resp_set_type(req, kStreamContentType);
  if (res != ESP_OK) return res;
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  httpd_resp_set_hdr(req, "Cache-Control", "no-store");

  char partHeader[64];
  uint32_t frames = 0;
  uint32_t windowStart = millis();

  while (true) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("[WEB] Falha ao capturar quadro");
      res = ESP_FAIL;
      break;
    }
    res = httpd_resp_send_chunk(req, kStreamBoundary, strlen(kStreamBoundary));
    if (res == ESP_OK) {
      size_t len = snprintf(partHeader, sizeof(partHeader), kStreamPartHeader,
                            static_cast<unsigned>(fb->len));
      res = httpd_resp_send_chunk(req, partHeader, len);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, reinterpret_cast<const char*>(fb->buf), fb->len);
    }
    esp_camera_fb_return(fb);
    if (res != ESP_OK) break;  // cliente fechou a aba / perdeu conexão

    ++frames;
    uint32_t elapsed = millis() - windowStart;
    if (elapsed >= 1000) {
      gStreamFps = frames * 1000.0f / elapsed;
      frames = 0;
      windowStart = millis();
    }
  }
  gStreamFps = 0;
  return res;
}

bool registerUri(httpd_handle_t server, const char* uri, esp_err_t (*handler)(httpd_req_t*)) {
  httpd_uri_t def = {};
  def.uri = uri;
  def.method = HTTP_GET;
  def.handler = handler;
  return httpd_register_uri_handler(server, &def) == ESP_OK;
}

}  // namespace

bool begin() {
  pinMode(FLASH_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);

  httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
  cfg.server_port = HTTP_CONTROL_PORT;
  cfg.lru_purge_enable = true;  // descarta conexões velhas em vez de recusar novas
  if (httpd_start(&gControlServer, &cfg) != ESP_OK) {
    Serial.println("[WEB] ERRO ao iniciar servidor de controle");
    return false;
  }
  registerUri(gControlServer, "/", handleIndex);
  registerUri(gControlServer, "/cmd", handleCommand);
  registerUri(gControlServer, "/flash", handleFlash);
  registerUri(gControlServer, "/status", handleStatus);

  // Cada instância do httpd precisa de porta de controle interna diferente.
  cfg.server_port = HTTP_STREAM_PORT;
  cfg.ctrl_port += 1;
  if (httpd_start(&gStreamServer, &cfg) != ESP_OK) {
    Serial.println("[WEB] ERRO ao iniciar servidor de video");
    return false;
  }
  registerUri(gStreamServer, "/stream", handleStream);

  Serial.printf("[WEB] Dashboard: http://%s/\n", WiFi.softAPIP().toString().c_str());
  Serial.printf("[WEB] Video:     http://%s:%d/stream\n", WiFi.softAPIP().toString().c_str(),
                HTTP_STREAM_PORT);
  return true;
}

}  // namespace web
