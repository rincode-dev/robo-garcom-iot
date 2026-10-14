// ============================================================================
// Simulador do Robô Garçom IoT ("Bandejito")
//
// Imita o firmware da ESP32-CAM no seu PC, sem nenhum hardware:
//   http://localhost:8080          -> o MESMO dashboard de src/dashboard_html.h (modo manual)
//   GET /cmd, /flash, /status      -> a MESMA API do firmware
//   http://localhost:8081/stream   -> vídeo MJPEG gerado por software (salão visto de cima)
//
// Fase 5 (autonomia) — por enquanto SÓ no simulador (ensaio do que o firmware vai ganhar):
//   http://localhost:8080/pedidos  -> página de pedidos (mesa, cozinha e robô)
//   GET /auto/status, /auto/modo, /pedido/*  -> API planejada do modo autônomo
//   O robô segue uma fita preta no chão (5 sensores de linha), conta as marcas
//   (base, mesa 1, 2, 3), para na mesa do pedido e freia diante de obstáculos.
//
// Os parâmetros de motor e o timeout de segurança são lidos de src/config.h,
// então o comportamento acompanha o que você ajustar no firmware.
//
// Uso:  npm install   (só na primeira vez)
//       npm start
// ============================================================================

const http = require('http');
const fs = require('fs');
const path = require('path');
const jpeg = require('jpeg-js');

const SRC = path.join(__dirname, '..', 'src');
const CONTROL_PORT = 8080;
const STREAM_PORT = CONTROL_PORT + 1; // o dashboard procura o vídeo em "porta + 1"

// ---------------------------------------------------------------------------
// Lê o dashboard e as constantes direto do código do firmware
// ---------------------------------------------------------------------------
function loadDashboard() {
  const src = fs.readFileSync(path.join(SRC, 'dashboard_html.h'), 'utf8');
  const match = src.match(/R"rawliteral\(([\s\S]*?)\)rawliteral"/);
  if (!match) throw new Error('Nao encontrei o HTML em dashboard_html.h');
  return match[1];
}

function loadConfig() {
  const src = fs.readFileSync(path.join(SRC, 'config.h'), 'utf8');
  const num = (name, fallback) => {
    const m = src.match(new RegExp(`#define\\s+${name}\\s+([\\d.]+)f?`));
    return m ? parseFloat(m[1]) : fallback;
  };
  return {
    timeoutMs: num('COMMAND_TIMEOUT_MS', 600),
    maxDuty: num('MOTOR_MAX_DUTY', 180),
    minDuty: num('MOTOR_MIN_DUTY', 90),
    turnFactor: num('TURN_SPEED_FACTOR', 0.75),
    curveFactor: num('CURVE_INNER_FACTOR', 0.45),
  };
}

const CFG = loadConfig();

// ---------------------------------------------------------------------------
// Log no estilo do monitor serial
// ---------------------------------------------------------------------------
const t0 = Date.now();
function log(msg) {
  const s = ((Date.now() - t0) / 1000).toFixed(3).padStart(8);
  console.log(`${s}  ${msg}`);
}

// ---------------------------------------------------------------------------
// Mundo simulado: tapete de 200 x 150 cm (o "salão" em miniatura da Fase 5)
// ---------------------------------------------------------------------------
const W = 320, H = 240;              // resolução QVGA, igual à câmera real
const WORLD_W = 200, WORLD_H = 150;  // cm
const PX = W / WORLD_W;              // pixels por cm
const MAX_WHEEL_CM_S = 68;           // motor TT 1:48 a 6 V com roda de 65 mm
const BATTERY_V = 8.4;

// Robô com as medidas reais: base do kit de 21,2 cm, corpo de 10 cm e rodas do lado de
// fora (15 cm no total), eixo das rodas a 13,5 cm da frente, roda boba e câmera na frente.
// A posição do robô (x, y) é o meio do eixo das rodas.
const CHASSI_LARG = 15, CHASSI_COMP = 21.2;
const CENTRO_A_FRENTE_DO_EIXO = 2.9; // o centro do chassi fica 2,9 cm à frente do eixo
const WHEEL_BASE = 12.3;             // distância entre as rodas (cm)
const ROBOT_R = 11;                  // raio usado para colisão (em volta do centro do chassi)
const SENSOR_FRENTE = 13.5;          // barra de sensores de linha: cm à frente do eixo
const SENSOR_PASSO = 1.2;            // distância entre os 5 sensores (cm)

// Pista: UMA linha reta de fita isolante preta (1,9 cm). O balcão (base) fica na
// ponta esquerda. O robô vai até a mesa, faz meia-volta (180°) e volta pela mesma linha.
const FITA = 1.9;
const LINHA = { x0: 20, x1: 184, y: 80 };
const BLOCO = 4;                     // comprimento das marcas de ponta (base e fim): 4 x 8 cm

// Autonomia (valores iniciais; na Fase 5 vão para src/config.h)
const AUTO = {
  baseDuty: CFG.minDuty + 15,        // velocidade de cruzeiro (~40 cm/s com os valores padrão)
  kp: 22, kd: 0.35,                  // correção proporcional e derivativa na linha
  paraCm: 15, liberaCm: 22,          // freio do sensor de distância (VL53L0X)
  semLinhaS: 0.6,                    // sem ver a linha por mais que isso = perdido
  // Meia-volta no lugar: rodas em sentidos opostos, em pulsos (liga/desliga) para girar
  // devagar mesmo com o MOTOR_MIN_DUTY alto, sem derrubar o que está na bandeja.
  giroDuty: CFG.minDuty,
  giroPulsoS: 0.12, giroLigado: 0.5, // período do pulso e fração do tempo com o motor ligado
  giroMaxS: 4,                       // sem reencontrar a linha nesse tempo = perdido
};

// ---------------------------------------------------------------------------
// Geometria da pista
// ---------------------------------------------------------------------------
// Postos: balcão + 3 mesas, alternando os lados da linha. A marca de cada mesa fica
// 8 cm DEPOIS dela (no sentido da ida), para o centro do robô (onde ficam as bandejas)
// parar bem ao lado da mesa. A mesa fica a 28 cm da linha: o giro no lugar "varre"
// um círculo de ~14,5 cm de raio em volta do eixo das rodas e não pode bater nela.
const MESA_DIST = 28;
const MESA_R = 9;
const POSTOS = [
  { nome: 'Base', x: LINHA.x0 + BLOCO / 2, lado: 0 },
  { nome: 'Mesa 1', x: 70, lado: -1 },
  { nome: 'Mesa 2', x: 115, lado: 1 },
  { nome: 'Mesa 3', x: 160, lado: -1 },
].map(p => ({
  ...p,
  marca: p.lado ? { x: p.x + 8, comp: FITA } : { x: p.x, comp: BLOCO },
  mesa: p.lado ? { x: p.x, y: LINHA.y + p.lado * MESA_DIST } : { x: 8, y: LINHA.y },
}));
// Bloco de fim de linha: segurança, caso o robô passe da última mesa
const FIM = { x: LINHA.x1 - BLOCO / 2, comp: BLOCO };
const MARCAS = [...POSTOS.map(p => p.marca), FIM];
const OBSTACULO = { x: 95, y: LINHA.y, r: 6 }; // "pessoa" na linha, entre as mesas 1 e 2

// Onde o robô fica no balcão: virado para as mesas, com os sensores já na linha
// (é exatamente onde ele termina a meia-volta depois de chegar no bloco da base).
const POSE_BASE = { x: LINHA.x0 + BLOCO + SENSOR_FRENTE, y: LINHA.y, heading: 0 };

function naFita(x, y) {
  const dy = Math.abs(y - LINHA.y);
  if (dy < FITA / 2 && x >= LINHA.x0 && x <= LINHA.x1) return true;
  // Marcas atravessadas na linha: 8 cm de largura
  return dy < 4 && MARCAS.some(m => Math.abs(x - m.x) < m.comp / 2);
}

// ---------------------------------------------------------------------------
// Estado do robô
// ---------------------------------------------------------------------------
const robot = {
  x: 0, y: 0, heading: 0,
  dir: 'stop', speed: 0, lastCmd: 0, flash: false,
  duty: [0, 0], sensores: [0, 0, 0, 0, 0], distancia: 999,
  trail: [],
};

const auto = {
  modo: 'manual',          // 'manual' | 'auto'
  estado: 'manual',        // manual, na_base, indo, na_mesa, girando, voltando, obstaculo, perdido
  posicao: 0, alvo: 0,     // índice em POSTOS (0 = base); POSTOS.length = bloco de fim
  naMarca: false, semLinha: 0, ultimoErro: 0, antesObst: null,
  giro: null,              // meia-volta em andamento: { fase, t, depois }
  pedidoAtual: null,
};
let obstaculoLigado = false;
const pedidos = [];
let proximoId = 1;

function colocarNaBase() {
  robot.heading = POSE_BASE.heading;
  robot.x = POSE_BASE.x;
  robot.y = POSE_BASE.y;
  robot.trail = [];
  auto.posicao = 0;
  auto.giro = null;
  auto.naMarca = false;
  auto.semLinha = 0;
  auto.ultimoErro = 0;
  if (auto.modo === 'auto') auto.estado = 'na_base';
}
colocarNaBase();

// ---------------------------------------------------------------------------
// Motores (mesma lógica de motors.cpp no modo manual)
// ---------------------------------------------------------------------------
function percentToDuty(p) {
  if (p <= 0) return 0;
  p = Math.min(p, 100);
  return CFG.minDuty + ((CFG.maxDuty - CFG.minDuty) * (p - 1)) / 99;
}

function wheelDuties(dir, speed) {
  const d = percentToDuty(speed);
  const t = d === 0 ? 0 : Math.max(d * CFG.turnFactor, CFG.minDuty);
  const c = d === 0 ? 0 : Math.min(d, Math.max(d * CFG.curveFactor, CFG.minDuty));
  switch (dir) {
    case 'forward':  return [d, d];
    case 'backward': return [-d, -d];
    case 'left':     return [-t, t];
    case 'right':    return [t, -t];
    case 'forward_left':   return [c, d];
    case 'forward_right':  return [d, c];
    case 'backward_left':  return [-c, -d];
    case 'backward_right': return [-d, -c];
    default:         return [0, 0];
  }
}

function dutyToCmS(duty) {
  const volts = (Math.abs(duty) / 255) * BATTERY_V;
  return Math.sign(duty) * Math.min(volts / 6, 1.2) * MAX_WHEEL_CM_S;
}

// No modo autônomo cada roda recebe um duty próprio. Abaixo de ~80% do
// MOTOR_MIN_DUTY o motor TT não vence o atrito e a roda para.
function dutyRoda(d) {
  d = Math.max(0, Math.min(CFG.maxDuty, d));
  return d < CFG.minDuty * 0.8 ? 0 : d;
}

// ---------------------------------------------------------------------------
// Sensores simulados
// ---------------------------------------------------------------------------
function centroChassi(x = robot.x, y = robot.y, h = robot.heading) {
  return { x: x + Math.cos(h) * CENTRO_A_FRENTE_DO_EIXO, y: y + Math.sin(h) * CENTRO_A_FRENTE_DO_EIXO };
}

function posSensor(i) {
  const h = robot.heading, lado = (i - 2) * SENSOR_PASSO; // i = 0 (esquerda) .. 4 (direita)
  return {
    x: robot.x + Math.cos(h) * SENSOR_FRENTE + Math.cos(h + Math.PI / 2) * lado,
    y: robot.y + Math.sin(h) * SENSOR_FRENTE + Math.sin(h + Math.PI / 2) * lado,
  };
}

function lerSensores() {
  return [0, 1, 2, 3, 4].map(i => { const p = posSensor(i); return naFita(p.x, p.y) ? 1 : 0; });
}

// VL53L0X na frente do chassi: mede a distância até o obstáculo no feixe à frente
function medirDistancia() {
  if (!obstaculoLigado) return 999;
  const h = robot.heading, frente = CENTRO_A_FRENTE_DO_EIXO + CHASSI_COMP / 2;
  const fx = robot.x + Math.cos(h) * frente, fy = robot.y + Math.sin(h) * frente;
  const vx = OBSTACULO.x - fx, vy = OBSTACULO.y - fy;
  const adiante = vx * Math.cos(h) + vy * Math.sin(h);
  const lateral = Math.abs(-vx * Math.sin(h) + vy * Math.cos(h));
  if (adiante <= 0 || lateral > OBSTACULO.r + 3) return 999;
  return Math.max(0, adiante - OBSTACULO.r);
}

function collides(x, y, h) {
  const c = centroChassi(x, y, h);
  if (c.x < ROBOT_R || c.y < ROBOT_R || c.x > WORLD_W - ROBOT_R || c.y > WORLD_H - ROBOT_R) return true;
  if (POSTOS.slice(1).some(p => Math.hypot(c.x - p.mesa.x, c.y - p.mesa.y) < MESA_R + ROBOT_R - 3)) return true;
  if (obstaculoLigado && Math.hypot(c.x - OBSTACULO.x, c.y - OBSTACULO.y) < OBSTACULO.r + ROBOT_R - 3) return true;
  return false;
}

// ---------------------------------------------------------------------------
// Modo autônomo: seguir a linha, contar marcas, meia-volta, atender pedidos
// ---------------------------------------------------------------------------
function despachar() {
  const p = pedidos.find(o => o.estado === 'pronto');
  if (!p) return;
  p.estado = 'a_caminho';
  auto.pedidoAtual = p.id;
  auto.alvo = p.mesa;
  auto.estado = 'indo';
  auto.naMarca = lerSensores().filter(Boolean).length >= 4;
  log(`[AUTO] Pedido #${p.id} -> ${POSTOS[p.mesa].nome}`);
}

// Meia-volta no lugar. Não precisa medir o ângulo: a barra de sensores está 13,5 cm
// à frente do eixo, então, girando em volta do eixo, ela sai da fita e só cai nela
// de novo depois de 180°, apontando para o outro lado.
function iniciarGiro(depois) {
  auto.estado = 'girando';
  auto.giro = { fase: 'saindo', t: 0, depois };
  log('[AUTO] Meia-volta (180 graus)');
}

function passoGiro(s, n, dt) {
  const g = auto.giro;
  g.t += dt;
  if (g.fase === 'saindo' && n === 0) g.fase = 'procurando'; // a barra inteira saiu da fita
  else if (g.fase === 'procurando' && s[2]) {                 // o sensor do meio achou a fita
    auto.giro = null;
    auto.naMarca = n >= 4;
    auto.ultimoErro = 0;
    auto.semLinha = 0;
    auto.estado = g.depois;
    log(g.depois === 'na_base' ? '[AUTO] No balcao, virado para as mesas'
                               : '[AUTO] Meia-volta completa: voltando para o balcao');
    return [0, 0];
  }
  if (g.t > AUTO.giroMaxS) {
    auto.giro = null;
    auto.estado = 'perdido';
    log('[AUTO] Meia-volta travou ou nao achou a linha (algo no caminho do giro?): parado');
    return [0, 0];
  }
  // O sensor de distância gira junto com o robô e "varre" o entorno: se aparecer algo
  // perto da frente, pausa o giro (sem contar o tempo) até liberar.
  if (robot.distancia < AUTO.paraCm) {
    g.t -= dt;
    if (!g.pausado) { g.pausado = true; log('[AUTO] Algo perto durante a meia-volta: pausando'); }
    return [0, 0];
  }
  if (g.pausado) { g.pausado = false; log('[AUTO] Livre: continuando a meia-volta'); }
  const ligado = (g.t % AUTO.giroPulsoS) < AUTO.giroPulsoS * AUTO.giroLigado;
  return ligado ? [-AUTO.giroDuty, AUTO.giroDuty] : [0, 0];
}

function chegouNaMesa() {
  auto.estado = 'na_mesa';
  const p = pedidos.find(o => o.id === auto.pedidoAtual);
  if (p) p.estado = 'na_mesa';
  log(`[AUTO] Chegou na ${POSTOS[auto.posicao].nome}: aguardando "Entregue"`);
}

function autoStep(dt) {
  const s = lerSensores();
  robot.sensores = s;
  robot.distancia = medirDistancia();
  const n = s.filter(Boolean).length;
  const marca = n >= 4;

  if (auto.estado === 'na_base') { despachar(); return [0, 0]; }
  if (auto.estado === 'girando') return passoGiro(s, n, dt);

  if (auto.estado === 'obstaculo') {
    if (robot.distancia > AUTO.liberaCm) { auto.estado = auto.antesObst; log('[AUTO] Caminho livre, continuando'); }
    return [0, 0];
  }

  if (auto.estado !== 'indo' && auto.estado !== 'voltando') return [0, 0];

  if (robot.distancia < AUTO.paraCm) {
    auto.antesObst = auto.estado;
    auto.estado = 'obstaculo';
    log(`[AUTO] Obstaculo a ${robot.distancia.toFixed(0)} cm: freando`);
    return [0, 0];
  }

  // Marca atravessada na fita: na ida conta para cima (balcão -> 1 -> 2 -> 3),
  // na volta conta para baixo até a marca do balcão (posição 0).
  if (marca && !auto.naMarca) {
    auto.naMarca = true;
    if (auto.estado === 'indo') {
      auto.posicao++;
      if (auto.posicao === auto.alvo) { chegouNaMesa(); return [0, 0]; }
      if (auto.posicao >= POSTOS.length) {
        // Passou da última mesa sem achar a certa: o pedido volta para a fila
        const p = pedidos.find(o => o.id === auto.pedidoAtual);
        if (p) p.estado = 'pronto';
        auto.pedidoAtual = null;
        log('[AUTO] Fim da linha sem achar a mesa: voltando');
        iniciarGiro('voltando');
        return [0, 0];
      }
    } else {
      auto.posicao--;
      if (auto.posicao <= 0) {
        auto.posicao = 0;
        log('[AUTO] Chegou no balcao');
        iniciarGiro('na_base');
        return [0, 0];
      }
    }
  }
  auto.naMarca = marca;

  if (n === 0) {
    auto.semLinha += dt;
    if (auto.semLinha > AUTO.semLinhaS) {
      auto.estado = 'perdido';
      log('[AUTO] Perdeu a linha: parado');
      return [0, 0];
    }
  } else auto.semLinha = 0;

  // Erro = onde a linha está embaixo da barra (-2 = toda à esquerda, +2 = toda à direita)
  let erro = auto.ultimoErro;
  if (!marca && n > 0) erro = s.reduce((acc, v, i) => acc + v * (i - 2), 0) / n;
  const derivada = (erro - auto.ultimoErro) / dt;
  auto.ultimoErro = erro;
  const corr = AUTO.kp * erro + AUTO.kd * derivada;
  return [dutyRoda(AUTO.baseDuty + corr), dutyRoda(AUTO.baseDuty - corr)];
}

// ---------------------------------------------------------------------------
// Física (50 Hz)
// ---------------------------------------------------------------------------
const PHYSICS_DT = 0.02;
setInterval(() => {
  let dl, dr;
  if (auto.modo === 'manual') {
    // Parada de segurança — igual a motors::enforceTimeout()
    if (robot.dir !== 'stop' && Date.now() - robot.lastCmd > CFG.timeoutMs) {
      robot.dir = 'stop';
      log('[MOT] Sem comandos -> parada de seguranca');
    }
    [dl, dr] = wheelDuties(robot.dir, robot.speed);
    robot.sensores = lerSensores();
    robot.distancia = medirDistancia();
  } else {
    [dl, dr] = autoStep(PHYSICS_DT);
  }
  robot.duty = [dl, dr];
  const vl = dutyToCmS(dl), vr = dutyToCmS(dr);
  const v = (vl + vr) / 2;
  const w = (vr - vl) / WHEEL_BASE;
  // Ângulo cresce no sentido horário na tela (eixo y para baixo).
  const nh = robot.heading - w * PHYSICS_DT;
  const nx = robot.x + Math.cos(nh) * v * PHYSICS_DT;
  const ny = robot.y + Math.sin(nh) * v * PHYSICS_DT;
  if (!collides(nx, ny, nh)) { robot.x = nx; robot.y = ny; robot.heading = nh; }
  if (v !== 0) {
    const c = centroChassi();
    const last = robot.trail[robot.trail.length - 1];
    if (!last || Math.hypot(last.x - c.x, last.y - c.y) > 3) {
      robot.trail.push(c);
      if (robot.trail.length > 300) robot.trail.shift();
    }
  }
}, PHYSICS_DT * 1000);

// ---------------------------------------------------------------------------
// Renderização em um buffer RGBA (desenho "na mão", sem bibliotecas gráficas)
// ---------------------------------------------------------------------------
const frame = Buffer.alloc(W * H * 4);

function px(x, y, [r, g, b], a = 1) {
  x |= 0; y |= 0;
  if (x < 0 || y < 0 || x >= W || y >= H) return;
  const i = (y * W + x) * 4;
  frame[i] = frame[i] * (1 - a) + r * a;
  frame[i + 1] = frame[i + 1] * (1 - a) + g * a;
  frame[i + 2] = frame[i + 2] * (1 - a) + b * a;
  frame[i + 3] = 255;
}
function fillRect(x, y, w, h, c) {
  for (let j = Math.max(0, y | 0); j < Math.min(H, y + h); j++)
    for (let i = Math.max(0, x | 0); i < Math.min(W, x + w); i++) px(i, j, c);
}
function fillCircle(cx, cy, r, c, a = 1) {
  for (let j = Math.floor(cy - r); j <= cy + r; j++)
    for (let i = Math.floor(cx - r); i <= cx + r; i++)
      if ((i - cx) ** 2 + (j - cy) ** 2 <= r * r) px(i, j, c, a);
}
function fillTriangle(p, c, a) {
  const [A, B, C] = p;
  const minX = Math.floor(Math.min(A.x, B.x, C.x)), maxX = Math.ceil(Math.max(A.x, B.x, C.x));
  const minY = Math.floor(Math.min(A.y, B.y, C.y)), maxY = Math.ceil(Math.max(A.y, B.y, C.y));
  const s = (p1, p2, p3) => (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
  for (let y = minY; y <= maxY; y++)
    for (let x = minX; x <= maxX; x++) {
      const P = { x, y };
      const d1 = s(P, A, B), d2 = s(P, B, C), d3 = s(P, C, A);
      const neg = d1 < 0 || d2 < 0 || d3 < 0, pos = d1 > 0 || d2 > 0 || d3 > 0;
      if (!(neg && pos)) px(x, y, c, a);
    }
}
// Retângulo girado: centro (cm), ângulo, comprimento (na direção do ângulo) e largura (cm)
function fillRotRect(cx, cy, ang, comp, larg, c, a = 1) {
  const ux = Math.cos(ang), uy = Math.sin(ang), vx = -uy, vy = ux;
  const k = (sa, sb) => ({ x: (cx + ux * sa * comp / 2 + vx * sb * larg / 2) * PX,
                           y: (cy + uy * sa * comp / 2 + vy * sb * larg / 2) * PX });
  const p1 = k(1, 1), p2 = k(1, -1), p3 = k(-1, -1), p4 = k(-1, 1);
  fillTriangle([p1, p2, p3], c, a);
  fillTriangle([p1, p3, p4], c, a);
}

// Fonte de 3 x 5 pixels para os números das mesas
const FONTE = {
  1: ['.#.', '##.', '.#.', '.#.', '###'], 2: ['##.', '..#', '.#.', '#..', '###'],
  3: ['##.', '..#', '.#.', '..#', '##.'], B: ['##.', '#.#', '##.', '#.#', '##.'],
};
function texto(ch, cx, cy, escala, cor) {
  const g = FONTE[ch]; if (!g) return;
  g.forEach((linha, j) => [...linha].forEach((v, i) => {
    if (v === '#') fillRect(cx + (i - 1.5) * escala, cy + (j - 2.5) * escala, escala, escala, cor);
  }));
}

// O fundo (tapete, fita, marcas, mesas) não muda: desenha uma vez e copia
const fundo = Buffer.alloc(W * H * 4);
(function desenharFundo() {
  for (let y = 0; y < H; y++)
    for (let x = 0; x < W; x++) {
      const linha = x % 16 === 0 || y % 16 === 0;
      px(x, y, linha ? [214, 214, 206] : [232, 232, 224]);
    }
  const preto = [25, 25, 28];
  fillRect(LINHA.x0 * PX, (LINHA.y - FITA / 2) * PX, (LINHA.x1 - LINHA.x0) * PX, FITA * PX, preto);
  for (const m of MARCAS) fillRotRect(m.x, LINHA.y, 0, m.comp, 8, preto);
  // Base (balcão) e mesas
  const b = POSTOS[0].mesa;
  fillRect((b.x - 8) * PX, (b.y - 14) * PX, 16 * PX, 28 * PX, [176, 120, 60]);
  texto('B', b.x * PX, b.y * PX, 3, [255, 255, 255]);
  POSTOS.slice(1).forEach((p, i) => {
    fillCircle(p.mesa.x * PX, p.mesa.y * PX, MESA_R * PX, [140, 98, 60]);
    fillCircle(p.mesa.x * PX, p.mesa.y * PX, MESA_R * PX - 2, [168, 122, 78]);
    texto(String(i + 1), p.mesa.x * PX, p.mesa.y * PX, 3, [255, 255, 255]);
  });
  frame.copy(fundo);
})();

const COR_ESTADO = {
  manual: [220, 225, 235], na_base: [120, 170, 255], indo: [62, 207, 142], voltando: [62, 207, 142],
  na_mesa: [245, 197, 66], girando: [180, 140, 255], obstaculo: [255, 93, 93], perdido: [255, 93, 93],
};

function render() {
  fundo.copy(frame);
  if (obstaculoLigado) {
    fillCircle(OBSTACULO.x * PX, OBSTACULO.y * PX, OBSTACULO.r * PX, [90, 60, 140]);
    fillCircle(OBSTACULO.x * PX, OBSTACULO.y * PX, OBSTACULO.r * PX * 0.55, [235, 190, 150]);
  }
  for (const p of robot.trail) fillCircle(p.x * PX, p.y * PX, 1, [62, 166, 255], 0.5);

  const h = robot.heading, c = centroChassi();
  // Campo de visão da câmera (cone na direção da frente)
  const fx = (c.x + Math.cos(h) * CHASSI_COMP / 2) * PX, fy = (c.y + Math.sin(h) * CHASSI_COMP / 2) * PX;
  const reach = 45 * PX, fov = 0.5;
  fillTriangle([
    { x: fx, y: fy },
    { x: fx + Math.cos(h - fov) * reach, y: fy + Math.sin(h - fov) * reach },
    { x: fx + Math.cos(h + fov) * reach, y: fy + Math.sin(h + fov) * reach },
  ], [255, 245, 200], robot.flash ? 0.45 : 0.18);

  // Rodas (no eixo, atrás), corpo, bandeja, câmera e sensores
  for (const lado of [-1, 1]) {
    const wx = robot.x + Math.cos(h + Math.PI / 2) * lado * (CHASSI_LARG / 2 - 1);
    const wy = robot.y + Math.sin(h + Math.PI / 2) * lado * (CHASSI_LARG / 2 - 1);
    fillRotRect(wx, wy, h, 6.5, 2.7, [30, 30, 30]);
  }
  const cor = auto.modo === 'manual' ? (robot.dir === 'stop' ? COR_ESTADO.manual : [62, 207, 142])
                                     : COR_ESTADO[auto.estado];
  fillRotRect(c.x, c.y, h, CHASSI_COMP, CHASSI_LARG - 3, cor);
  fillRotRect(c.x, c.y, h, 13, 9.5, [201, 111, 59]);            // bandeja de cima (terracota)
  fillCircle(c.x * PX, c.y * PX, 2.6 * PX, [242, 238, 227]);    // cabeça
  fillCircle((c.x + Math.cos(h) * 2.4) * PX, (c.y + Math.sin(h) * 2.4) * PX, 1.6, [40, 40, 40]); // lente
  for (let i = 0; i < 5; i++) {
    const p = posSensor(i);
    fillCircle(p.x * PX, p.y * PX, 1.2, robot.sensores[i] ? [255, 60, 60] : [90, 200, 255]);
  }

  // Flash: clareia a imagem toda
  if (robot.flash) for (let i = 0; i < frame.length; i += 4) {
    frame[i] = Math.min(255, frame[i] * 1.25 + 20);
    frame[i + 1] = Math.min(255, frame[i + 1] * 1.25 + 20);
    frame[i + 2] = Math.min(255, frame[i + 2] * 1.25 + 20);
  }
  return jpeg.encode({ data: frame, width: W, height: H }, 70).data;
}

// ---------------------------------------------------------------------------
// Servidor de vídeo (porta 8081): MJPEG, exatamente como o firmware faz
// ---------------------------------------------------------------------------
const BOUNDARY = 'robogarcomframe';
const viewers = new Set();
let fps = 0, frames = 0, fpsWindow = Date.now();

setInterval(() => {
  if (viewers.size === 0) { fps = 0; frames = 0; fpsWindow = Date.now(); return; }
  const jpg = render();
  for (const res of viewers) {
    res.write(`\r\n--${BOUNDARY}\r\nContent-Type: image/jpeg\r\nContent-Length: ${jpg.length}\r\n\r\n`);
    res.write(jpg);
  }
  frames++;
  const elapsed = Date.now() - fpsWindow;
  if (elapsed >= 1000) { fps = (frames * 1000) / elapsed; frames = 0; fpsWindow = Date.now(); }
}, 1000 / 20);

http.createServer((req, res) => {
  if (!req.url.startsWith('/stream')) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {
    'Content-Type': `multipart/x-mixed-replace;boundary=${BOUNDARY}`,
    'Access-Control-Allow-Origin': '*',
    'Cache-Control': 'no-store',
  });
  viewers.add(res);
  log(`[WEB] Cliente de video conectado (${viewers.size})`);
  req.on('close', () => { viewers.delete(res); log('[WEB] Cliente de video saiu'); });
}).listen(STREAM_PORT);

// ---------------------------------------------------------------------------
// Servidor de controle (porta 8080): dashboard + API
// ---------------------------------------------------------------------------
const DIRS = ['forward', 'backward', 'left', 'right', 'stop',
              'forward_left', 'forward_right', 'backward_left', 'backward_right'];

function text(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(body);
}
function json(res, obj) {
  res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(obj));
}

function irParaManual(motivo) {
  if (auto.modo === 'manual') return;
  auto.modo = 'manual';
  auto.estado = 'manual';
  auto.giro = null;
  const p = pedidos.find(o => o.id === auto.pedidoAtual && ['a_caminho', 'na_mesa'].includes(o.estado));
  if (p) p.estado = 'pronto'; // volta para a fila
  auto.pedidoAtual = null;
  log(`[AUTO] Modo manual (${motivo})`);
}

function rotaAuto(url, res) {
  const q = (k) => url.searchParams.get(k);

  if (url.pathname === '/auto/status') {
    return json(res, {
      modo: auto.modo, estado: auto.estado,
      posicao: POSTOS[auto.posicao].nome, alvo: POSTOS[auto.alvo].nome,
      sensores: robot.sensores, distancia_cm: robot.distancia > 500 ? null : Math.round(robot.distancia),
      obstaculo: obstaculoLigado,
      mesas: POSTOS.length - 1,
      pedidos: pedidos.slice(-20),
    });
  }

  if (url.pathname === '/auto/modo') {
    const m = q('m');
    if (m === 'manual') { irParaManual('pedido pelo painel'); return text(res, 200, 'manual'); }
    if (m !== 'auto') return text(res, 400, 'use ?m=auto ou ?m=manual');
    const naBase = Math.hypot(robot.x - POSE_BASE.x, robot.y - POSE_BASE.y) < 6
                   && Math.cos(robot.heading - POSE_BASE.heading) > 0.9;
    if (!naBase) return text(res, 409, 'Coloque o robo na base antes (botao "Colocar na base")');
    robot.dir = 'stop';
    auto.modo = 'auto';
    auto.posicao = 0;
    auto.naMarca = false;
    auto.estado = 'na_base';
    log('[AUTO] Modo automatico: esperando pedidos prontos');
    return text(res, 200, 'auto');
  }

  if (url.pathname === '/pedido/novo') {
    const mesa = parseInt(q('mesa'), 10);
    if (!(mesa >= 1 && mesa < POSTOS.length)) return text(res, 400, 'mesa invalida');
    const itens = (q('itens') || '').replace(/[<>]/g, '').slice(0, 80) || 'pedido';
    const p = { id: proximoId++, mesa, itens, estado: 'novo', criado: Date.now() };
    pedidos.push(p);
    if (pedidos.length > 50) pedidos.shift();
    log(`[PED] Novo pedido #${p.id} da ${POSTOS[mesa].nome}: ${itens}`);
    return text(res, 200, String(p.id));
  }

  if (url.pathname === '/pedido/pronto' || url.pathname === '/pedido/cancelar') {
    const p = pedidos.find(o => o.id === parseInt(q('id'), 10));
    if (!p) return text(res, 404, 'pedido nao encontrado');
    if (url.pathname === '/pedido/pronto') {
      if (p.estado !== 'novo') return text(res, 409, 'pedido nao esta aguardando a cozinha');
      p.estado = 'pronto';
      log(`[PED] Pedido #${p.id} pronto na cozinha`);
    } else {
      if (!['novo', 'pronto'].includes(p.estado)) return text(res, 409, 'pedido ja saiu da cozinha');
      p.estado = 'cancelado';
      log(`[PED] Pedido #${p.id} cancelado`);
    }
    return text(res, 200, p.estado);
  }

  if (url.pathname === '/pedido/entregue') {
    if (auto.estado !== 'na_mesa') return text(res, 409, 'o robo nao esta parado numa mesa');
    const p = pedidos.find(o => o.id === auto.pedidoAtual);
    if (p) { p.estado = 'entregue'; log(`[PED] Pedido #${p.id} entregue`); }
    auto.pedidoAtual = null;
    auto.alvo = 0;
    iniciarGiro('voltando');
    return text(res, 200, 'voltando');
  }

  // Ajudantes do simulador (no robô real isso é feito com a mão)
  if (url.pathname === '/sim/base') {
    colocarNaBase();
    log('[SIM] Robo colocado na base');
    return text(res, 200, 'ok');
  }
  if (url.pathname === '/sim/obstaculo') {
    obstaculoLigado = q('on') === '1';
    log(`[SIM] Obstaculo ${obstaculoLigado ? 'colocado na pista' : 'removido'}`);
    return text(res, 200, obstaculoLigado ? 'on' : 'off');
  }
  return false;
}

http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === '/') {
    // Relido a cada acesso: edite dashboard_html.h e só recarregue a página (F5).
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(loadDashboard());
  }

  if (url.pathname === '/pedidos') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    return res.end(fs.readFileSync(path.join(__dirname, 'pedidos.html'), 'utf8'));
  }

  if (url.pathname === '/cmd') {
    const dir = url.searchParams.get('dir');
    if (!dir) return text(res, 400, 'faltou ?dir=');
    if (!DIRS.includes(dir)) return text(res, 400, 'dir invalido');
    const speed = Math.max(0, Math.min(100, parseInt(url.searchParams.get('speed') ?? '70', 10) || 0));
    // Comando manual durante o modo automático: o humano assume o controle
    if (auto.modo === 'auto' && dir !== 'stop') irParaManual('controle manual assumiu');
    if (auto.modo === 'auto') return text(res, 200, 'ok'); // "stop" do painel não tira do automático
    if (dir !== robot.dir) log(`[MOT] ${dir} (velocidade ${speed}%)`);
    robot.dir = speed === 0 ? 'stop' : dir;
    robot.speed = speed;
    robot.lastCmd = Date.now();
    return text(res, 200, 'ok');
  }

  if (url.pathname === '/flash') {
    const on = url.searchParams.get('on');
    if (on === null) return text(res, 400, 'faltou ?on=');
    robot.flash = on === '1';
    log(`[WEB] Flash ${robot.flash ? 'ligado' : 'desligado'}`);
    return text(res, 200, robot.flash ? 'on' : 'off');
  }

  if (url.pathname === '/status') {
    return json(res, {
      uptime_s: Math.floor((Date.now() - t0) / 1000),
      clients: viewers.size,
      fps: Math.round(fps * 10) / 10,
      heap_kb: 0,
      psram: true,
      dir: robot.dir,
      flash: robot.flash,
    });
  }

  if (rotaAuto(url, res) !== false) return;

  text(res, 404, 'nao encontrado');
}).listen(CONTROL_PORT, () => {
  console.log('');
  console.log('=== Robo Garcom IoT - SIMULADOR ===');
  console.log(`Parametros lidos de src/config.h: ${JSON.stringify(CFG)}`);
  console.log(`Pista: linha reta de ${LINHA.x1 - LINHA.x0} cm, ${POSTOS.length - 1} mesas, meia-volta na mesa e no balcao`);
  console.log('');
  console.log(`  Controle manual:     http://localhost:${CONTROL_PORT}`);
  console.log(`  Pedidos (autonomo):  http://localhost:${CONTROL_PORT}/pedidos`);
  console.log('  Para encerrar:       Ctrl + C');
  console.log('');
});
