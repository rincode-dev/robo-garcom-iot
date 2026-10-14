#include "motors.h"

#include <esp_arduino_version.h>
#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

#include "config.h"

namespace motors {
namespace {

struct Motor {
  uint8_t pin1, pin2;
  uint8_t ch1, ch2;
  bool inverted;
};

const Motor kLeft = {MOTOR_LEFT_IN1, MOTOR_LEFT_IN2, MOTOR_LEFT_CH1, MOTOR_LEFT_CH2,
                     MOTOR_LEFT_INVERTED};
const Motor kRight = {MOTOR_RIGHT_IN1, MOTOR_RIGHT_IN2, MOTOR_RIGHT_CH1, MOTOR_RIGHT_CH2,
                      MOTOR_RIGHT_INVERTED};

SemaphoreHandle_t gLock = nullptr;
volatile uint32_t gLastCommandMs = 0;
volatile Direction gDirection = Direction::Stop;

// --- Camada de compatibilidade LEDC (Arduino core 2.x e 3.x) ---------------
void pwmAttach(uint8_t pin, uint8_t channel) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttachChannel(pin, MOTOR_PWM_FREQ_HZ, MOTOR_PWM_RES_BITS, channel);
#else
  ledcSetup(channel, MOTOR_PWM_FREQ_HZ, MOTOR_PWM_RES_BITS);
  ledcAttachPin(pin, channel);
#endif
}

void pwmWrite(uint8_t pin, uint8_t channel, uint32_t duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  (void)channel;
  ledcWrite(pin, duty);
#else
  (void)pin;
  ledcWrite(channel, duty);
#endif
}

// signedDuty > 0 = para frente, < 0 = para trás, 0 = solto (roda livre).
// Na ponte H: PWM em um lado e LOW no outro define sentido e velocidade.
void setMotor(const Motor& m, int signedDuty) {
  if (m.inverted) signedDuty = -signedDuty;
  uint32_t duty = static_cast<uint32_t>(abs(signedDuty));
  if (signedDuty > 0) {
    pwmWrite(m.pin2, m.ch2, 0);
    pwmWrite(m.pin1, m.ch1, duty);
  } else if (signedDuty < 0) {
    pwmWrite(m.pin1, m.ch1, 0);
    pwmWrite(m.pin2, m.ch2, duty);
  } else {
    pwmWrite(m.pin1, m.ch1, 0);
    pwmWrite(m.pin2, m.ch2, 0);
  }
}

int percentToDuty(uint8_t percent) {
  if (percent == 0) return 0;
  if (percent > 100) percent = 100;
  return MOTOR_MIN_DUTY + (MOTOR_MAX_DUTY - MOTOR_MIN_DUTY) * (percent - 1) / 99;
}

class Guard {
 public:
  Guard() { xSemaphoreTake(gLock, portMAX_DELAY); }
  ~Guard() { xSemaphoreGive(gLock); }
};

// Chamar somente com gLock adquirido.
void applyLocked(Direction dir, uint8_t speedPercent) {
  const int duty = percentToDuty(speedPercent);
  // Giros mais suaves, mas nunca abaixo do torque mínimo para girar no eixo.
  const int turnDuty =
      (duty == 0) ? 0 : max(static_cast<int>(duty * TURN_SPEED_FACTOR), MOTOR_MIN_DUTY);
  // Curva: roda de dentro mais lenta que a de fora, sem cair abaixo do torque mínimo.
  const int innerDuty =
      (duty == 0) ? 0 : min(duty, max(static_cast<int>(duty * CURVE_INNER_FACTOR), MOTOR_MIN_DUTY));

  gDirection = (duty == 0) ? Direction::Stop : dir;
  switch (gDirection) {
    case Direction::Forward:  setMotor(kLeft, duty);       setMotor(kRight, duty);      break;
    case Direction::Backward: setMotor(kLeft, -duty);      setMotor(kRight, -duty);     break;
    case Direction::Left:     setMotor(kLeft, -turnDuty);  setMotor(kRight, turnDuty);  break;
    case Direction::Right:    setMotor(kLeft, turnDuty);   setMotor(kRight, -turnDuty); break;
    case Direction::ForwardLeft:   setMotor(kLeft, innerDuty);   setMotor(kRight, duty);        break;
    case Direction::ForwardRight:  setMotor(kLeft, duty);        setMotor(kRight, innerDuty);   break;
    case Direction::BackwardLeft:  setMotor(kLeft, -innerDuty);  setMotor(kRight, -duty);       break;
    case Direction::BackwardRight: setMotor(kLeft, -duty);       setMotor(kRight, -innerDuty);  break;
    case Direction::Stop:     setMotor(kLeft, 0);          setMotor(kRight, 0);         break;
  }
}

}  // namespace

void begin() {
  gLock = xSemaphoreCreateMutex();
  pwmAttach(kLeft.pin1, kLeft.ch1);
  pwmAttach(kLeft.pin2, kLeft.ch2);
  pwmAttach(kRight.pin1, kRight.ch1);
  pwmAttach(kRight.pin2, kRight.ch2);
  stop();
  Serial.println("[MOT] Motores prontos");
}

void drive(Direction dir, uint8_t speedPercent) {
  Guard g;
  gLastCommandMs = millis();
  applyLocked(dir, speedPercent);
}

void stop() { drive(Direction::Stop, 0); }

void enforceTimeout() {
  Guard g;  // verificação e parada atômicas: um comando novo não é "atropelado"
  if (gDirection == Direction::Stop) return;
  if (millis() - gLastCommandMs > COMMAND_TIMEOUT_MS) {
    applyLocked(Direction::Stop, 0);
    Serial.println("[MOT] Sem comandos -> parada de seguranca");
  }
}

bool parseDirection(const char* text, Direction& out) {
  if (!strcmp(text, "forward"))  { out = Direction::Forward;  return true; }
  if (!strcmp(text, "backward")) { out = Direction::Backward; return true; }
  if (!strcmp(text, "left"))     { out = Direction::Left;     return true; }
  if (!strcmp(text, "right"))    { out = Direction::Right;    return true; }
  if (!strcmp(text, "stop"))     { out = Direction::Stop;     return true; }
  if (!strcmp(text, "forward_left"))   { out = Direction::ForwardLeft;   return true; }
  if (!strcmp(text, "forward_right"))  { out = Direction::ForwardRight;  return true; }
  if (!strcmp(text, "backward_left"))  { out = Direction::BackwardLeft;  return true; }
  if (!strcmp(text, "backward_right")) { out = Direction::BackwardRight; return true; }
  return false;
}

const char* directionName(Direction dir) {
  switch (dir) {
    case Direction::Forward:  return "forward";
    case Direction::Backward: return "backward";
    case Direction::Left:     return "left";
    case Direction::Right:    return "right";
    case Direction::ForwardLeft:   return "forward_left";
    case Direction::ForwardRight:  return "forward_right";
    case Direction::BackwardLeft:  return "backward_left";
    case Direction::BackwardRight: return "backward_right";
    default:                  return "stop";
  }
}

Direction currentDirection() { return gDirection; }

}  // namespace motors
