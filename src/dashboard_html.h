#pragma once
// dashboard_html.h — interface web servida em GET /.
// Tudo inline (sem CDN): o robô cria uma rede própria SEM internet.
//
// Protocolo de controle (baixa latência):
//   - Ao pressionar um botão/tecla: GET /cmd?dir=<direção>&speed=<0-100> imediatamente.
//   - Enquanto segurar: reenvia a cada 200 ms ("heartbeat").
//   - Ao soltar, perder o foco ou trocar de aba: GET /cmd?dir=stop.
//   - Se o heartbeat parar (Wi-Fi caiu), o firmware para sozinho após COMMAND_TIMEOUT_MS.

static const char DASHBOARD_HTML[] = R"rawliteral(<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
<title>Robô Garçom IoT</title>
<style>
  :root{--bg:#0f1218;--card:#181d26;--line:#2a3140;--txt:#e8ecf3;--mut:#8b95a7;--acc:#3ea6ff;--ok:#3ecf8e;--bad:#ff5d5d}
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
       user-select:none;-webkit-user-select:none}
  header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--line)}
  h1{font-size:17px;margin:0;font-weight:600}
  .pill{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--mut)}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--bad)}
  .dot.on{background:var(--ok)}
  main{max-width:960px;margin:0 auto;padding:16px;display:grid;gap:16px;grid-template-columns:1fr}
  @media(min-width:800px){main{grid-template-columns:3fr 2fr}}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px}
  .video{position:relative;aspect-ratio:4/3;background:#000;border-radius:10px;overflow:hidden}
  .video img{width:100%;height:100%;object-fit:contain;display:block}
  .video .msg{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:var(--mut)}
  .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px;text-align:center}
  .stats b{display:block;font-size:17px}
  .stats span{font-size:12px;color:var(--mut)}
  .pad{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;max-width:300px;margin:4px auto 16px;touch-action:none}
  .pad button{aspect-ratio:1;font-size:28px;border-radius:14px;border:1px solid var(--line);background:#212836;color:var(--txt);
              cursor:pointer;touch-action:none;transition:background .08s,transform .08s}
  .pad button.active{background:var(--acc);border-color:var(--acc);transform:scale(.96)}
  .pad .stop{font-size:15px;font-weight:700;background:#3a1f24;border-color:#5a2a32}
  .pad .diag{font-size:20px;color:var(--mut)}
  label{display:flex;justify-content:space-between;font-size:13px;color:var(--mut);margin-bottom:6px}
  input[type=range]{width:100%;accent-color:var(--acc)}
  .row{display:flex;gap:10px;margin-top:14px}
  .row button{flex:1;padding:10px;border-radius:10px;border:1px solid var(--line);background:#212836;color:var(--txt);font-size:14px;cursor:pointer}
  .row button.on{background:#f5c542;color:#111;border-color:#f5c542}
  .hint{font-size:12px;color:var(--mut);text-align:center;margin-top:12px}
</style>
</head>
<body>
<header>
  <h1>🤖 Robô Garçom IoT</h1>
  <span class="pill"><span id="dot" class="dot"></span><span id="conn">conectando…</span></span>
</header>
<main>
  <section class="card">
    <div class="video">
      <img id="cam" alt="Vídeo ao vivo da câmera">
      <div id="camMsg" class="msg">Carregando vídeo…</div>
    </div>
    <div class="stats">
      <div><b id="fps">–</b><span>FPS</span></div>
      <div><b id="lat">–</b><span>latência ms</span></div>
      <div><b id="cli">–</b><span>clientes</span></div>
      <div><b id="up">–</b><span>ligado há</span></div>
    </div>
  </section>

  <section class="card">
    <div class="pad" id="pad">
      <button class="diag" data-dir="forward_left" aria-label="Frente e esquerda">◤</button>
      <button data-dir="forward" aria-label="Frente">▲</button>
      <button class="diag" data-dir="forward_right" aria-label="Frente e direita">◥</button>
      <button data-dir="left" aria-label="Esquerda">◀</button>
      <button class="stop" data-dir="stop" aria-label="Parar">PARAR</button>
      <button data-dir="right" aria-label="Direita">▶</button>
      <button class="diag" data-dir="backward_left" aria-label="Trás e esquerda">◣</button>
      <button data-dir="backward" aria-label="Trás">▼</button>
      <button class="diag" data-dir="backward_right" aria-label="Trás e direita">◢</button>
    </div>
    <label for="speed"><span>Velocidade</span><span id="speedVal">70%</span></label>
    <input id="speed" type="range" min="10" max="100" step="5" value="70">
    <div class="row">
      <button id="flash">💡 Flash</button>
      <button id="reload">🔄 Recarregar vídeo</button>
    </div>
    <p class="hint">Segure os botões para mover. Teclado: W A S D ou setas (duas juntas = curva) · Espaço = parar</p>
  </section>
</main>

<script>
(() => {
  const $ = (id) => document.getElementById(id);
  const HEARTBEAT_MS = 200;
  let current = 'stop', timer = null, inFlight = false, speed = 70, flashOn = false;

  // ---------- Vídeo (porta do painel + 1: 81 no robô, 8081 no simulador) ----------
  const cam = $('cam'), camMsg = $('camMsg');
  const streamPort = location.port ? Number(location.port) + 1 : 81;
  function startVideo() {
    camMsg.style.display = 'flex'; camMsg.textContent = 'Carregando vídeo…';
    cam.src = `http://${location.hostname}:${streamPort}/stream?t=${Date.now()}`;
  }
  cam.onload = () => { camMsg.style.display = 'none'; };
  cam.onerror = () => { camMsg.style.display = 'flex'; camMsg.textContent = 'Vídeo indisponível — tentando de novo…';
                        setTimeout(startVideo, 2000); };
  $('reload').onclick = startVideo;
  startVideo();

  // ---------- Comandos de movimento ----------
  function setOnline(ok) { $('dot').classList.toggle('on', ok); $('conn').textContent = ok ? 'conectado' : 'sem conexão'; }

  async function send(dir, isHeartbeat) {
    if (isHeartbeat && inFlight) return;          // não empilha requisições se a rede estiver lenta
    inFlight = true;
    const t0 = performance.now();
    try {
      const r = await fetch(`/cmd?dir=${dir}&speed=${speed}`, { cache: 'no-store' });
      if (r.ok) { $('lat').textContent = Math.round(performance.now() - t0); setOnline(true); }
    } catch (e) { setOnline(false); }
    finally { inFlight = false; }
  }

  function highlight(dir) {
    document.querySelectorAll('#pad button[data-dir]').forEach(b =>
      b.classList.toggle('active', b.dataset.dir === dir && dir !== 'stop'));
  }

  function start(dir) {
    if (dir === 'stop') return haltAll();   // botão PARAR também "esquece" as teclas seguradas
    if (current === dir) return;
    current = dir; highlight(dir); send(dir, false);
    clearInterval(timer); timer = setInterval(() => send(current, true), HEARTBEAT_MS);
  }

  function halt() {
    clearInterval(timer); timer = null;
    current = 'stop'; highlight('stop'); send('stop', false);
  }

  // Pointer events = mouse + toque com o mesmo código.
  document.querySelectorAll('#pad button[data-dir]').forEach(btn => {
    btn.addEventListener('pointerdown', (e) => { e.preventDefault(); btn.setPointerCapture(e.pointerId); start(btn.dataset.dir); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(ev =>
      btn.addEventListener(ev, () => { if (current === btn.dataset.dir) halt(); }));
    btn.addEventListener('contextmenu', (e) => e.preventDefault());
  });

  // Teclado: guarda TODAS as teclas seguradas e combina (W + D = curva para frente e direita).
  const KEYS = { ArrowUp:'forward', w:'forward', ArrowDown:'backward', s:'backward',
                 ArrowLeft:'left', a:'left', ArrowRight:'right', d:'right', ' ':'stop' };
  const keyName = (e) => e.key.length === 1 ? e.key.toLowerCase() : e.key;
  const held = new Set();
  let keyboardDriving = false;
  function keyboardDir() {
    const has = (d) => [...held].some(k => KEYS[k] === d);
    const v = (has('forward') ? 1 : 0) - (has('backward') ? 1 : 0);   // teclas opostas se anulam
    const h = (has('right') ? 1 : 0) - (has('left') ? 1 : 0);
    const side = h > 0 ? 'right' : h < 0 ? 'left' : '';
    if (v > 0) return side ? 'forward_' + side : 'forward';
    if (v < 0) return side ? 'backward_' + side : 'backward';
    return side || 'stop';
  }
  function applyKeys() {
    const d = keyboardDir();
    if (d === 'stop') { if (keyboardDriving) { keyboardDriving = false; halt(); } return; }
    keyboardDriving = true; start(d);
  }
  addEventListener('keydown', (e) => {
    const d = KEYS[keyName(e)]; if (!d) return;
    e.preventDefault();
    if (d === 'stop') return haltAll();
    // Repetição automática (tecla segurada) não conta: depois de PARAR,
    // o robô só volta a andar se a tecla for solta e apertada de novo.
    if (e.repeat) return;
    held.add(keyName(e)); applyKeys();
  });
  addEventListener('keyup', (e) => {
    const d = KEYS[keyName(e)]; if (!d || d === 'stop') return;
    held.delete(keyName(e)); applyKeys();
  });

  // PARAR, Espaço, perda de foco ou troca de aba -> para e esquece as teclas seguradas.
  function haltAll() { held.clear(); keyboardDriving = false; halt(); }
  addEventListener('blur', haltAll);
  document.addEventListener('visibilitychange', () => { if (document.hidden) haltAll(); });

  // ---------- Velocidade e flash ----------
  $('speed').oninput = (e) => { speed = +e.target.value; $('speedVal').textContent = speed + '%'; };
  $('flash').onclick = async () => {
    try {
      const r = await fetch(`/flash?on=${flashOn ? 0 : 1}`, { cache: 'no-store' });
      flashOn = (await r.text()) === 'on';
      $('flash').classList.toggle('on', flashOn);
    } catch (e) { setOnline(false); }
  };

  // ---------- Telemetria ----------
  function fmtUptime(s) { const m = Math.floor(s / 60); return m < 60 ? `${m}m${s % 60}s` : `${Math.floor(m / 60)}h${m % 60}m`; }
  async function poll() {
    try {
      const st = await (await fetch('/status', { cache: 'no-store' })).json();
      $('fps').textContent = st.fps.toFixed(1);
      $('cli').textContent = st.clients;
      $('up').textContent = fmtUptime(st.uptime_s);
      flashOn = st.flash; $('flash').classList.toggle('on', flashOn);
      setOnline(true);
    } catch (e) { setOnline(false); }
  }
  setInterval(poll, 2000); poll();
})();
</script>
</body>
</html>
)rawliteral";
