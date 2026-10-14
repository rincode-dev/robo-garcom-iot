#pragma once
// web_server.h — dois servidores HTTP nativos do ESP-IDF (esp_http_server):
//   :80  -> dashboard (GET /), comandos (GET /cmd), flash (GET /flash), status (GET /status)
//   :81  -> vídeo MJPEG (GET /stream)
// O stream fica em porta separada porque o handler dele nunca termina;
// assim os comandos de movimento não esperam na fila atrás do vídeo.

namespace web {

bool begin();

}  // namespace web
