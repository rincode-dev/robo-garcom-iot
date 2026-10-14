#include "camera.h"

#include "config.h"

namespace camera {

bool begin() {
  camera_config_t cfg = {};
  cfg.pin_pwdn = CAM_PIN_PWDN;
  cfg.pin_reset = CAM_PIN_RESET;
  cfg.pin_xclk = CAM_PIN_XCLK;
  cfg.pin_sccb_sda = CAM_PIN_SIOD;
  cfg.pin_sccb_scl = CAM_PIN_SIOC;
  cfg.pin_d7 = CAM_PIN_D7;
  cfg.pin_d6 = CAM_PIN_D6;
  cfg.pin_d5 = CAM_PIN_D5;
  cfg.pin_d4 = CAM_PIN_D4;
  cfg.pin_d3 = CAM_PIN_D3;
  cfg.pin_d2 = CAM_PIN_D2;
  cfg.pin_d1 = CAM_PIN_D1;
  cfg.pin_d0 = CAM_PIN_D0;
  cfg.pin_vsync = CAM_PIN_VSYNC;
  cfg.pin_href = CAM_PIN_HREF;
  cfg.pin_pclk = CAM_PIN_PCLK;

  // O XCLK da câmera ocupa LEDC canal 0 / timer 0 (motores usam 2–5).
  cfg.xclk_freq_hz = CAM_XCLK_FREQ_HZ;
  cfg.ledc_timer = LEDC_TIMER_0;
  cfg.ledc_channel = LEDC_CHANNEL_0;

  // JPEG direto do sensor: o ESP32 só repassa os bytes, sem recomprimir.
  cfg.pixel_format = PIXFORMAT_JPEG;
  cfg.frame_size = CAM_FRAME_SIZE;
  cfg.jpeg_quality = CAM_JPEG_QUALITY;

  if (psramFound()) {
    // 2 buffers na PSRAM + "pegar o mais recente" = menor latência possível.
    cfg.fb_count = 2;
    cfg.fb_location = CAMERA_FB_IN_PSRAM;
    cfg.grab_mode = CAMERA_GRAB_LATEST;
  } else {
    // Sem PSRAM só cabe 1 buffer pequeno na RAM interna.
    Serial.println("[CAM] AVISO: PSRAM nao encontrada, usando modo reduzido");
    cfg.frame_size = FRAMESIZE_QVGA;
    cfg.fb_count = 1;
    cfg.fb_location = CAMERA_FB_IN_DRAM;
    cfg.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  }

  esp_err_t err = esp_camera_init(&cfg);
  if (err != ESP_OK) {
    Serial.printf("[CAM] ERRO 0x%x ao iniciar a camera\n", err);
    return false;
  }

  sensor_t* s = esp_camera_sensor_get();
  s->set_vflip(s, CAM_VFLIP ? 1 : 0);
  s->set_hmirror(s, CAM_HMIRROR ? 1 : 0);

  Serial.println("[CAM] Camera OV2640 pronta");
  return true;
}

}  // namespace camera
