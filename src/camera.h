#pragma once
// camera.h — inicialização da câmera OV2640.

#include <esp_camera.h>

namespace camera {

// Inicializa o sensor. Retorna false se a câmera não for detectada
// (cabo flat solto, alimentação fraca ou módulo com defeito).
bool begin();

}  // namespace camera
