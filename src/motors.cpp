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

// Partida suave: duty com sinal pedido pelo comando (alvo) e o aplicado na
// ponte H, que sobe aos poucos até o alvo. Protegidos por gLock.
int gTargetLeft = 0, gTargetRight = 0;
float gAppliedLeft = 0, gAppliedRight = 0;
uint32_t gLastRampMs = 0;

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

// Um passo da rampa: aumentar a força sobe no máximo maxStep; partir do zero
// (ou inverter) começa no MOTOR_MIN_DUTY; reduzir e parar são imediatos.
float rampToward(float applied, int target, float maxStep) {
  if (target == 0 || MOTOR_RAMP_MS == 0) return target;
  const float sign = (target > 0) ? 1.0f : -1.0f;
  const float want = fabsf(static_cast<float>(target));
  const bool sameWay = (applied > 0) == (target > 0) && applied != 0;
  if (!sameWay) return sign * min(want, static_cast<float>(MOTOR_MIN_DUTY));
  const float now = fabsf(applied);
  if (want <= now) return target;
  return sign * min(want, now + maxStep);
}

// Chamar somente com gLock adquirido. elapsedMs = tempo desde o último passo.
void rampLocked(uint32_t elapsedMs) {
  const uint32_t dt = (elapsedMs > 50) ? 50 : elapsedMs;  // loop atrasado: não pula a rampa
  const float maxStep = static_cast<float>(MOTOR_MAX_DUTY - MOTOR_MIN_DUTY) * dt /
                        (MOTOR_RAMP_MS > 0 ? MOTOR_RAMP_MS : 1);
  const float left = rampToward(gAppliedLeft, gTargetLeft, maxStep);
  const float right = rampToward(gAppliedRight, gTargetRight, maxStep);
  if (left != gAppliedLeft) { gAppliedLeft = left; setMotor(kLeft, lroundf(left)); }
  if (right != gAppliedRight) { gAppliedRight = right; setMotor(kRight, lroundf(right)); }
}

void setTargetsLocked(int left, int right) {
  gTargetLeft = left;
  gTargetRight = right;
  gLastRampMs = millis();
  rampLocked(0);  // parar/reduzir na hora; partir já no MOTOR_MIN_DUTY
}

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
    case Direction::Forward:  setTargetsLocked(duty, duty);            break;
    case Direction::Backward: setTargetsLocked(-duty, -duty);          break;
    case Direction::Left:     setTargetsLocked(-turnDuty, turnDuty);   break;
    case Direction::Right:    setTargetsLocked(turnDuty, -turnDuty);   break;
    case Direction::ForwardLeft:   setTargetsLocked(innerDuty, duty);    break;
    case Direction::ForwardRight:  setTargetsLocked(duty, innerDuty);    break;
    case Direction::BackwardLeft:  setTargetsLocked(-innerDuty, -duty);  break;
    case Direction::BackwardRight: setTargetsLocked(-duty, -innerDuty);  break;
    case Direction::Stop:     setTargetsLocked(0, 0);                  break;
  }
}

}  // namespace

void begin() {
  gLock = xSemaphoreCreateMutex();
  pwmAttach(kLeft.pin1, kLeft.ch1);
  pwmAttach(kLeft.pin2, kLeft.ch2);
  pwmAttach(kRight.pin1, kRight.ch1);
  pwmAttach(kRight.pin2, kRight.ch2);
  setMotor(kLeft, 0);   // pinos em LOW desde o boot (a rampa só escreve quando muda)
  setMotor(kRight, 0);
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

void update() {
  Guard g;
  const uint32_t now = millis();
  rampLocked(now - gLastRampMs);
  gLastRampMs = now;
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
