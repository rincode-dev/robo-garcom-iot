#pragma once
// ============================================================================
// config.h — ÚNICO lugar para pinos, rede e ajustes finos do robô.
// Qualquer mudança de fiação deve ser refletida aqui E no manual_montagem_fisica.md.
// ============================================================================

#include <Arduino.h>

// ---------------------------------------------------------------------------
// Rede Wi-Fi (modo Ponto de Acesso — o próprio robô cria a rede)
// ---------------------------------------------------------------------------
#define WIFI_AP_SSID        "RoboGarcom-IoT"
#define WIFI_AP_PASSWORD    "garcom1234"     // mínimo 8 caracteres (WPA2)
#define WIFI_AP_CHANNEL     6                // 1, 6 ou 11 costumam ter menos interferência
#define WIFI_AP_MAX_CLIENTS 2                // 1 piloto + 1 espectador
// IP fixo do robô no modo AP: http://192.168.4.1

// ---------------------------------------------------------------------------
// Atualização via Wi-Fi (OTA)
// ---------------------------------------------------------------------------
#define OTA_HOSTNAME        "robo-garcom"
#define OTA_PASSWORD        "garcom-ota"     // igual a --auth no platformio.ini

// ---------------------------------------------------------------------------
// Servidores HTTP
// ---------------------------------------------------------------------------
#define HTTP_CONTROL_PORT   80               // dashboard + comandos
#define HTTP_STREAM_PORT    81               // vídeo MJPEG (bloqueia o handler, por isso porta própria)

// ---------------------------------------------------------------------------
// Câmera OV2640 — pinagem FIXA do módulo AI-Thinker (NÃO ALTERAR)
// Estes GPIOs estão soldados à câmera na placa e não podem ser reutilizados.
// ---------------------------------------------------------------------------
#define CAM_PIN_PWDN    32
#define CAM_PIN_RESET   -1   // não conectado
#define CAM_PIN_XCLK     0
#define CAM_PIN_SIOD    26   // SCCB (I2C) dados
#define CAM_PIN_SIOC    27   // SCCB (I2C) clock
#define CAM_PIN_D7      35   // Y9
#define CAM_PIN_D6      34   // Y8
#define CAM_PIN_D5      39   // Y7
#define CAM_PIN_D4      36   // Y6
#define CAM_PIN_D3      21   // Y5
#define CAM_PIN_D2      19   // Y4
#define CAM_PIN_D1      18   // Y3
#define CAM_PIN_D0       5   // Y2
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22

// Qualidade de imagem: QVGA (320x240) = mais FPS e menos latência.
// Opções úteis: FRAMESIZE_QVGA, FRAMESIZE_CIF (400x296), FRAMESIZE_VGA (640x480)
#define CAM_FRAME_SIZE      FRAMESIZE_QVGA
#define CAM_JPEG_QUALITY    12      // 10 (melhor) .. 63 (pior). 10–15 é o ponto doce
#define CAM_XCLK_FREQ_HZ    20000000
#define CAM_VFLIP           false   // inverta se a imagem aparecer de cabeça para baixo
#define CAM_HMIRROR         false   // inverta se a imagem aparecer espelhada

// ---------------------------------------------------------------------------
// LEDs da placa
// ---------------------------------------------------------------------------
#define FLASH_LED_PIN    4   // LED de flash branco (forte!). Reservado — só para o flash.
#define STATUS_LED_PIN  33   // LED vermelho na parte de trás. Lógica INVERTIDA (LOW = aceso)

// ---------------------------------------------------------------------------
// Motores — Ponte H (MX1508 "mini L298N" ou L9110S)
//
// Pinos LIVRES da ESP32-CAM (sem cartão microSD em uso): 12, 13, 14, 15.
//   - GPIO12 é pino de "strapping": precisa estar em LOW no boot.
//     Por isso há um resistor de 10 kΩ de GPIO12 para GND (ver manual).
//   - GPIO14/15 emitem pulsos curtos no boot: o robô pode "tremer" por
//     alguns milissegundos ao ligar. É normal.
// ---------------------------------------------------------------------------
#define MOTOR_LEFT_IN1    14   // -> IN1 do driver (Motor A, esquerdo)
#define MOTOR_LEFT_IN2    15   // -> IN2 do driver
#define MOTOR_RIGHT_IN1   13   // -> IN3 do driver (Motor B, direito)
#define MOTOR_RIGHT_IN2   12   // -> IN4 do driver

// Se um motor girar ao contrário, troque para true (evita refazer a fiação).
#define MOTOR_LEFT_INVERTED   false
#define MOTOR_RIGHT_INVERTED  false

// Canais LEDC (PWM). Canal 0 / timer 0 são usados pelo XCLK da câmera.
// Canais 2–5 usam os timers 1 e 2 -> sem conflito.
#define MOTOR_LEFT_CH1    2
#define MOTOR_LEFT_CH2    3
#define MOTOR_RIGHT_CH1   4
#define MOTOR_RIGHT_CH2   5

#define MOTOR_PWM_FREQ_HZ  2000
#define MOTOR_PWM_RES_BITS 8       // duty 0..255

// Limite de tensão média nos motores amarelos (3–6 V).
// Bateria 2x18650 = até 8,4 V. 8,4 V * 180/255 ≈ 5,9 V  -> seguro.
#define MOTOR_MAX_DUTY     180
#define MOTOR_MIN_DUTY      90     // abaixo disso o motor só "zumbe" sem girar
#define TURN_SPEED_FACTOR  0.75f   // giros mais suaves que as retas
#define CURVE_INNER_FACTOR 0.45f   // curvas (W+D etc.): roda de dentro gira a 45% da de fora

// Partida suave: a roda já parte no MOTOR_MIN_DUTY e sobe até o MOTOR_MAX_DUTY
// em MOTOR_RAMP_MS (a arrancada brusca faz o robô alto "empinar" para trás).
// Reduzir, parar ou inverter continua imediato. 0 = sem rampa.
#define MOTOR_RAMP_MS      500

// Segurança: se nenhum comando chegar nesse intervalo, os motores param.
// O dashboard reenvia o comando a cada 200 ms enquanto o botão está pressionado.
#define COMMAND_TIMEOUT_MS 600
