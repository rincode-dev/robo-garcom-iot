#pragma once
// motors.h — controle diferencial de 2 motores DC via ponte H (MX1508 / L9110S).
// Thread-safe: pode ser chamado pelos handlers HTTP e pelo loop() ao mesmo tempo.

#include <Arduino.h>

namespace motors {

enum class Direction {
  Stop, Forward, Backward, Left, Right,
  ForwardLeft, ForwardRight, BackwardLeft, BackwardRight  // curvas (diagonais)
};

void begin();

// speedPercent: 0..100 (mapeado para MOTOR_MIN_DUTY..MOTOR_MAX_DUTY).
// Também renova o "watchdog" de comandos.
void drive(Direction dir, uint8_t speedPercent);

void stop();

// Deve ser chamado no loop(): para os motores se o dashboard
// parar de enviar comandos (Wi-Fi caiu, aba fechada, etc.).
void enforceTimeout();

// Deve ser chamado no loop(): avança a partida suave (MOTOR_RAMP_MS).
void update();

// Converte "forward", "backward", "left", "right", "stop" e as curvas
// "forward_left", "forward_right", "backward_left", "backward_right". Retorna false se inválido.
bool parseDirection(const char* text, Direction& out);

const char* directionName(Direction dir);
Direction currentDirection();

}  // namespace motors
