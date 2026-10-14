"""Prototipo DEMONSTRATIVO do robo pronto: carcaca + chassi + eletronica + fios.

Nao e para imprimir. Serve para ver no Fusion 360 onde cada peca fica e
por onde passa cada fio (seguindo o manual_montagem_fisica.md, Etapas 6 a 8).

Saida:
  step/prototipo_completo.step   -> abrir no Fusion 360
Opcional (usado para gerar as imagens de conferencia):
  python prototipo.py --stl PASTA   -> uma STL por peca + PASTA/cena.scad (OpenSCAD)

As medidas vem do medidas.txt (via gerar.py). Componentes eletronicos sao
simplificados e as posicoes dos pinos sao ilustrativas: na montagem real,
confira sempre o nome impresso na placa.
"""
import math
import sys
from pathlib import Path

import cadquery as cq

import gerar as g

V = cq.Vector
W, L, H = g.W, g.L, g.H


# ---------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------
def bloco(cx, cy, z0, sx, sy, sz):
    """Caixa centrada em XY, com a base em z0."""
    return cq.Solid.makeBox(sx, sy, sz, V(cx - sx / 2, cy - sy / 2, z0))


def cil(r, h, base, direcao=(0, 0, 1)):
    return cq.Solid.makeCylinder(r, h, V(*base), V(*direcao))


def junta(*solidos):
    return cq.Compound.makeCompound([s for s in solidos if s is not None])


def gira_x(p, graus):
    a = math.radians(graus)
    x, y, z = p
    return (x, y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a))


# Quadro da placa (o mesmo do gerar.py) levado ate a cabeca montada
CAB_Z0 = g.cabeca_z0


def placa_para_robo(p):
    x, y, z = gira_x(p, -g.inclinacao)
    return (x, y + g.fy - g.parede - 1 + g.coluna_pos_y, z + g.olho_z + CAB_Z0)


def forma_placa_para_robo(s):
    return (s.rotate(V(0, 0, 0), V(1, 0, 0), -g.inclinacao)
            .translate(V(0, g.fy - g.parede - 1 + g.coluna_pos_y, g.olho_z + CAB_Z0)))


# ---------------------------------------------------------------------
# Fios: tubos que seguem uma lista de pontos, com conector "dupont" nas pontas
# ---------------------------------------------------------------------
R_FIO = 0.75
conectores = []


def fio(pontos, pontas=(True, True)):
    pts = [V(*p) for p in pontos]
    pecas = []
    for a, b in zip(pts, pts[1:]):
        d = b - a
        if d.Length > 1e-6:
            pecas.append(cq.Solid.makeCylinder(R_FIO, d.Length, a, d.normalized()))
    for p in pts[1:-1]:
        pecas.append(cq.Solid.makeSphere(R_FIO, p, angleDegrees1=-90, angleDegrees2=90))
    # Conector: capa preta de 10 mm ao longo do 1o/ultimo trecho
    for usar, a, b in ((pontas[0], pts[0], pts[1]), (pontas[1], pts[-1], pts[-2])):
        d = b - a
        if usar and d.Length >= 10:
            conectores.append(cq.Solid.makeCylinder(1.3, 10, a, d.normalized()))
    return junta(*pecas)


def rota(a, b, z):
    """Caminho em 'L': sobe de a ate z, anda em x, depois em y, desce ate b."""
    return [a, (a[0], a[1], z), (b[0], a[1], z), (b[0], b[1], z), b]


# ---------------------------------------------------------------------
# Posicoes da eletronica (as mesmas da "eletronica" do .scad). O corpo do
# chassi tem so 10 cm de largura: suporte das pilhas deitado no meio, de
# frente para tras (as pilhas saem pela abertura de tras); regulador e
# protoboard lado a lado na frente; driver ao lado do suporte, perto dos motores.
# ---------------------------------------------------------------------
BAT = (0, -50)          # suporte 2x18650: 41 x 78 x 25
LM = (-27, 48)          # LM2596: 35 x 66
PB = (27, 52)           # mini protoboard: 34 x 45 x 8,5
DRV = (32, -38)         # MX1508: 21 x 24
FURO_FIOS_X = 8         # furos na base por onde os fios dos motores sobem (x = +-8)
PB_TOPO = 8.5
COL_Z0 = g.coluna_z0    # base da coluna (dentro da saia)


def furo_pb(coluna, linha):
    """Furo da protoboard: coluna 'a'..'j', linha 1..17 (linha 1 = frente)."""
    i = "abcdefghij".index(coluna)
    x = PB[0] - 3.81 - (4 - i) * 2.54 if i < 5 else PB[0] + 3.81 + (i - 5) * 2.54
    y = PB[1] + 20.32 - (linha - 1) * 2.54
    return (x, y, PB_TOPO)


# Driver: barra de pinos "+ - IN1 IN2 IN3 IN4" virada para a protoboard
DRV_TOPO = 2.6
PINO_DRV = {n: (DRV[0] + (i - 2.5) * 2.54, DRV[1] + 10.5, DRV_TOPO + 2.5)
            for i, n in enumerate(["+", "-", "IN1", "IN2", "IN3", "IN4"])}
PAD_DRV = {"A1": (DRV[0] - 6.35, DRV[1] - 10.5, DRV_TOPO), "A2": (DRV[0] - 3.81, DRV[1] - 10.5, DRV_TOPO),
           "B1": (DRV[0] + 3.81, DRV[1] - 10.5, DRV_TOPO), "B2": (DRV[0] + 6.35, DRV[1] - 10.5, DRV_TOPO)}

# LM2596: entrada atras, saida na frente
LM_TOPO = 5.6
BORNE_LM = {"IN+": (LM[0] - 8, LM[1] - 29, LM_TOPO), "IN-": (LM[0] + 8, LM[1] - 29, LM_TOPO),
            "OUT+": (LM[0] - 8, LM[1] + 29, LM_TOPO), "OUT-": (LM[0] + 8, LM[1] + 29, LM_TOPO)}

# ESP32-CAM: fileira de pinos do lado dos motores (posicao ilustrativa)
P_FRENTE = -g.lente_altura
P_TRAS = P_FRENTE - g.placa_esp
P_TOPO = g.lente_do_topo
P_BASE = g.lente_do_topo - g.placa_altura
PINOS_ESP = ["5V", "GND", "IO12", "IO13", "IO15", "IO14", "IO2", "IO4"]


def pino_esp(k, lado=1):
    return (lado * (g.placa_largura / 2 - 1.5), P_TRAS - 2.5, P_BASE + 3 + k * 2.54)


# ---------------------------------------------------------------------
# Pecas
# ---------------------------------------------------------------------
def chassi():
    """Base do kit (acrilico; marrom = papel protetor), contorno da foto, furos simplificados."""
    placa = g.prisma(3, z=-3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy = g.furo(sx, sy)
            placa = placa.cut(cq.Workplane("XY").add(cil(1.7, 5, (hx, hy, -4))))
    for lado in (-1, 1):   # furos por onde os fios dos motores sobem
        placa = placa.cut(cq.Workplane("XY").add(cil(4, 5, (lado * FURO_FIOS_X, g.roda_pos_y + 55, -4))))
    return placa.val()


def parafusos():
    s = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy = g.furo(sx, sy)
            s += [cil(2.75, 2.5, (hx, hy, -5.5)), cil(1.5, 11, (hx, hy, -3))]
    return junta(*s)


def motor(lado):
    """Motor TT: caixa de reducao amarela + motor metalico; eixo para fora."""
    x0 = lado * 35
    eixo_y, eixo_z = g.roda_pos_y, g.roda_eixo_z
    caixa = bloco(x0, eixo_y + 7.5, eixo_z - 9.4, 21, 37, 18.8)
    return caixa, eixo_y


def motores_amarelos():
    s = []
    for lado in (-1, 1):
        caixa, eixo_y = motor(lado)
        s.append(caixa)
        # suportes em "T" de acrilico nao desenhados; eixo ate a roda
        ate_roda = g.roda_pos_x - g.roda_largura / 2 - 45.5
        s.append(cil(2.7, max(2, ate_roda + 2), (lado * 45.5, eixo_y, g.roda_eixo_z), (lado, 0, 0)))
    return junta(*s)


def motores_metal():
    s = []
    for lado in (-1, 1):
        y0 = g.roda_pos_y + 26
        s.append(cq.Solid.makeCylinder(10, 25, V(lado * 35, y0, g.roda_eixo_z), V(0, 1, 0)))
    return junta(*s)


def terminais_motor(lado):
    y = g.roda_pos_y + 51
    return [(lado * 35 - 4, y, g.roda_eixo_z + 6), (lado * 35 + 4, y, g.roda_eixo_z + 6)]


def capacitores_motor():
    s = []
    for lado in (-1, 1):
        a, b = terminais_motor(lado)
        s.append(cq.Solid.makeCylinder(2.5, 1.5, V(lado * 35, a[1] + 2, a[2] + 3), V(0, 1, 0)))
    return junta(*s)


def rodas(parte):
    s = []
    for lado in (-1, 1):
        cx = lado * g.roda_pos_x   # rodas do lado de fora do corpo estreito
        base = (cx - lado * g.roda_largura / 2, g.roda_pos_y, g.roda_eixo_z)
        if parte == "pneu":
            pneu = cq.Workplane("XY").add(cil(g.roda_diametro / 2, g.roda_largura, base, (lado, 0, 0))).cut(
                cq.Workplane("XY").add(cil(g.roda_diametro / 2 - 9, g.roda_largura + 2,
                                           (base[0] - lado, base[1], base[2]), (lado, 0, 0))))
            s.append(pneu.val())
        else:
            s.append(cil(g.roda_diametro / 2 - 9, g.roda_largura - 1, (base[0] + lado * 0.5, base[1], base[2]), (lado, 0, 0)))
    return junta(*s)


def roda_boba(parte):
    """Rodizio giratorio (2a foto do dono): placa quadrada em 4 espacadores,
    garfo e rodinha, na ponta estreita (frente)."""
    chao = g.roda_eixo_z - g.roda_diametro / 2
    y = L / 2 - 20
    esp = 12                                   # altura dos espacadores
    rd = 13                                    # raio da rodinha
    if parte == "espacadores":
        return junta(*[cil(2.5, esp, (sx * 12, y + sy * 12, -3 - esp)) for sx in (-1, 1) for sy in (-1, 1)])
    z_placa = -3 - esp - 2
    z_eixo = chao + rd
    return junta(bloco(0, y, z_placa, 32, 32, 2), cil(9, 4, (0, y, z_placa - 4)),
                 bloco(-7, y - 4, z_eixo, 2, 12, z_placa - 4 - z_eixo), bloco(7, y - 4, z_eixo, 2, 12, z_placa - 4 - z_eixo),
                 cil(rd, 10, (-5, y - 6, z_eixo), (1, 0, 0)))


def suporte_baterias():
    caixa = cq.Workplane("XY").add(bloco(BAT[0], BAT[1], 0, 41, 78, 20)).cut(
        cq.Workplane("XY").add(bloco(BAT[0], BAT[1], 2, 37, 72, 20)))
    chave = bloco(BAT[0] + 23, BAT[1] - 10, 6, 5, 12, 12)
    return junta(caixa.val(), chave)


def baterias():
    return junta(*[cil(9.2, 65, (BAT[0] + sx * 9.6, BAT[1] - 32.5, 11.2), (0, 1, 0)) for sx in (-1, 1)])


def lm2596(parte):
    x, y = LM
    if parte == "placa":
        return junta(bloco(x, y, 4, 35, 66, 1.6), *[cil(1.5, 4, (x + sx * 14, y + sy * 29, 0))
                                                    for sx in (-1, 1) for sy in (-1, 1)])
    if parte == "componentes":   # indutor, chip e bornes
        return junta(cil(6, 7, (x, y - 14, LM_TOPO)), bloco(x - 8, y + 2, LM_TOPO, 9, 10, 3),
                     *[cil(1.6, 1, b) for b in BORNE_LM.values()])
    if parte == "display":
        return bloco(x + 3, y + 14, LM_TOPO, 22, 13, 7)
    return junta(bloco(x + 11, y + 2, LM_TOPO, 6, 9, 9), cil(1.3, 1.5, (x + 11, y - 1.5, LM_TOPO + 9)))  # trimpot


def protoboard():
    return bloco(PB[0], PB[1], 0, 34, 45, PB_TOPO)


def trilhas_pb():
    """Faixas coloridas = linhas usadas (1 +BAT, 3 GND, 5 +5V, 7 resistor)."""
    faixas = {}
    for linha, metade, cor in ((1, "ae", "vermelho"), (3, "ae", "preto"), (3, "fj", "preto"),
                               (5, "ae", "laranja"), (7, "fj", "roxo")):
        a, b = furo_pb(metade[0], linha), furo_pb(metade[1], linha)
        faixas.setdefault(cor, []).append(bloco((a[0] + b[0]) / 2, a[1], PB_TOPO, b[0] - a[0] + 2.4, 2.0, 0.3))
    return {cor: junta(*s) for cor, s in faixas.items()}


def driver(parte):
    x, y = DRV
    if parte == "placa":
        return bloco(x, y, 1, 21, 24, 1.6)
    if parte == "chip":
        return bloco(x, y - 1, DRV_TOPO, 5, 4, 1.5)
    if parte == "barra":
        return bloco(x, y + 10.5, DRV_TOPO, 15.4, 2.5, 2.5)
    return junta(*[cil(0.32, 9, (p[0], p[1], DRV_TOPO)) for p in PINO_DRV.values()])  # pinos


def capacitor_470():
    a, b = furo_pb("d", 3), furo_pb("d", 5)
    pernas = junta(cil(0.3, 3, a), cil(0.3, 3, b))
    corpo = cil(4, 12, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, PB_TOPO + 3))
    return pernas, corpo


def resistor_10k():
    a, b = furo_pb("j", 3), furo_pb("j", 7)
    zc = PB_TOPO + 3
    pernas = junta(fio([a, (a[0], a[1], zc), (a[0], a[1] - 2, zc)], (False, False)),
                   fio([b, (b[0], b[1], zc), (b[0], b[1] + 2, zc)], (False, False)))
    corpo = cq.Solid.makeCylinder(1.2, 6.2, V(a[0], a[1] - 2, zc), V(0, -1, 0))
    return pernas, corpo


def esp32cam(parte):
    pl = g.placa_largura
    if parte == "placa":
        s = cq.Solid.makeBox(pl, g.placa_esp, g.placa_altura, V(-pl / 2, P_TRAS, P_BASE))
    elif parte == "camera":   # modulo da camera + lente
        s = junta(cq.Solid.makeBox(8.5, 4, 8.5, V(g.lente_x - 4.25, P_FRENTE, -4.25)),
                  cq.Solid.makeCylinder(3.5, g.lente_altura - 4, V(g.lente_x, P_FRENTE + 4, 0), V(0, 1, 0)),
                  cq.Solid.makeBox(8, 0.3, P_TOPO - 4.25 + 2, V(g.lente_x - 4, P_FRENTE, 4.25 - 0.01)))
    elif parte == "blindagem":
        s = cq.Solid.makeBox(18, 2.5, 16, V(-9, P_FRENTE, P_BASE + 3))
    elif parte == "flash":
        zf = P_TOPO - g.flash_do_topo
        s = cq.Solid.makeBox(3, 1, 3, V(g.flash_x - 1.5, P_FRENTE, zf - 1.5))
    elif parte == "barras":
        s = junta(*[cq.Solid.makeBox(2.54, 2.5, 8 * 2.54, V(lado * (pl / 2 - 1.5) - 1.27, P_TRAS - 2.5, P_BASE + 3 - 1.27))
                    for lado in (-1, 1)])
    else:  # pinos dourados (saem para tras)
        s = junta(*[cq.Solid.makeCylinder(0.32, 8.5, V(*pino_esp(k, lado)), V(0, -1, 0)).translate(V(0, 2.5, 0))
                    for lado in (-1, 1) for k in range(8)])
    return forma_placa_para_robo(s)


# ---------------------------------------------------------------------
# Fiacao (manual_montagem_fisica.md, Etapas 6 a 8)
# ---------------------------------------------------------------------
def fios():
    f = {}

    # Bateria -> protoboard (fios do proprio suporte)
    bat_mais = (BAT[0] + 5, BAT[1] + 39, 10)
    bat_menos = (BAT[0] - 5, BAT[1] + 39, 10)
    f["01_bateria_mais_linha1"] = ("vermelho", fio(rota(bat_mais, furo_pb("a", 1), 21), (False, True)))
    f["02_bateria_menos_linha3"] = ("preto", fio(rota(bat_menos, furo_pb("a", 3), 19.5), (False, True)))
    # LM2596
    f["03_lm_IN_mais_linha1"] = ("vermelho", fio(rota(BORNE_LM["IN+"], furo_pb("b", 1), 24)))
    f["04_lm_IN_menos_linha3"] = ("preto", fio(rota(BORNE_LM["IN-"], furo_pb("b", 3), 22.5)))
    f["05_lm_OUT_mais_5V_linha5"] = ("laranja", fio(rota(BORNE_LM["OUT+"], furo_pb("a", 5), 16.5)))
    f["06_lm_OUT_menos_linha3"] = ("preto", fio(rota(BORNE_LM["OUT-"], furo_pb("c", 3), 15)))
    # Ponte entre as duas metades da linha 3 (GND)
    a, b = furo_pb("e", 3), furo_pb("f", 3)
    f["07_ponte_GND_3e_3f"] = ("preto", fio([a, (a[0], a[1], a[2] + 4), (b[0], b[1], b[2] + 4), b], (False, False)))
    # Driver
    f["08_driver_mais_linha1"] = ("vermelho", fio(rota(PINO_DRV["+"], furo_pb("c", 1), 27)))
    f["09_driver_menos_linha3"] = ("preto", fio(rota(PINO_DRV["-"], furo_pb("g", 3), 25.5)))
    f["10_driver_IN4_linha7"] = ("roxo", fio(rota(PINO_DRV["IN4"], furo_pb("h", 7), 18)))
    # Motores -> driver (soldados nas duas pontas): por baixo da base ate o
    # furo do meio, sobem e vao ate os pads do driver
    for lado, saida, nome in ((-1, "A", "esquerdo"), (1, "B", "direito")):
        for i, (t, cor) in enumerate(zip(terminais_motor(lado), ("vermelho", "preto"))):
            pad = PAD_DRV[f"{saida}{i + 1}"]
            zf = 5 + i * 1.8
            yf = t[1] + 4
            hx = lado * FURO_FIOS_X + (i - 0.5) * 2
            pts = [t, (t[0], yf, t[2]), (hx, yf, t[2]), (hx, yf, zf), (pad[0], yf, zf),
                   (pad[0], pad[1], zf), pad]
            f[f"11_motor_{nome}_{'ab'[i]}_saida_{saida}"] = (cor, fio(pts, (False, False)))

    # ESP32-CAM -> desce pelo canal da coluna -> protoboard / driver
    ligacoes = [  # (pino, destino, cor, altura do trecho horizontal)
        ("5V", furo_pb("b", 5), "laranja", 38),
        ("GND", furo_pb("h", 3), "preto", 36.5),
        ("IO12", furo_pb("g", 7), "roxo", 35),
        ("IO13", PINO_DRV["IN3"], "azul", 33.5),
        ("IO15", PINO_DRV["IN2"], "verde", 32),
        ("IO14", PINO_DRV["IN1"], "amarelo", 30.5),
    ]
    for n, (pino, destino, cor, zh) in enumerate(ligacoes):
        k = PINOS_ESP.index(pino)
        p0 = pino_esp(k)
        p1 = (p0[0], p0[1] - 13, p0[2])
        a0, a1 = placa_para_robo(p0), placa_para_robo(p1)
        ang = math.radians(60 * n)
        bx, by = 4.5 * math.cos(ang), g.coluna_pos_y + 4.5 * math.sin(ang)
        topo = CAB_Z0 + g.cab_piso + 4
        pts = [a0, a1, (bx, by, a1[2]), (bx, by, topo), (bx, by, zh),
               (destino[0], by, zh), (destino[0], destino[1], zh), destino]
        f[f"12_esp_{pino}"] = (cor, fio(pts))
    return f


# ---------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------
CORES = {
    "creme": (0.91, 0.89, 0.82), "creme2": (0.85, 0.82, 0.74), "terracota": (0.79, 0.44, 0.23),
    "cinza": (0.54, 0.52, 0.47), "branco": (0.96, 0.96, 0.94), "mdf": (0.78, 0.60, 0.38),
    "amarelo_tt": (0.98, 0.80, 0.10), "metal": (0.75, 0.75, 0.78), "borracha": (0.12, 0.12, 0.12),
    "latao": (0.80, 0.65, 0.30), "preto": (0.10, 0.10, 0.10), "azul_bat": (0.15, 0.35, 0.80),
    "azul_pcb": (0.10, 0.30, 0.65), "vermelho_pcb": (0.75, 0.10, 0.10), "verde_pcb": (0.05, 0.35, 0.20),
    "dourado": (0.90, 0.75, 0.25), "display": (0.85, 0.05, 0.05), "trimpot": (0.15, 0.40, 0.90),
    "bege": (0.85, 0.75, 0.55), "azul_cap": (0.10, 0.15, 0.45), "laranja_cap": (0.95, 0.55, 0.10),
    "vermelho": (0.90, 0.10, 0.10), "laranja": (1.0, 0.50, 0.0), "roxo": (0.55, 0.20, 0.75),
    "azul": (0.10, 0.40, 0.95), "verde": (0.10, 0.70, 0.20), "amarelo": (1.0, 0.90, 0.0), "flex": (0.65, 0.40, 0.10),
}


def montar():
    conectores.clear()
    pos = {nome: montada for nome, (_, _, montada) in g.PECAS.items()}
    car = {nome: pos[nome](func()) for nome, (func, _, _) in g.PECAS.items()}
    cap_pernas, cap_corpo = capacitor_470()
    res_pernas, res_corpo = resistor_10k()
    f = fios()

    grupos = {
        "1_carcaca": [
            ("saia", car["saia"], "creme"), ("coluna", car["coluna"], "creme2"),
            ("bandeja_baixo", car["bandeja_baixo"], "terracota"), ("bandeja_cima", car["bandeja_cima"], "terracota"),
            ("cabeca", car["cabeca"], "branco"), ("cabeca_tampa", car["cabeca_tampa"], "cinza"),
        ],
        "2_chassi_rodas_motores": [
            ("chassi_base", chassi(), "mdf"), ("parafusos_M3", parafusos(), "metal"),
            ("motores_caixa_reducao", motores_amarelos(), "amarelo_tt"), ("motores_metal", motores_metal(), "metal"),
            ("capacitores_100nF_motores", capacitores_motor(), "laranja_cap"),
            ("rodas_pneu", rodas("pneu"), "borracha"), ("rodas_cubo", rodas("cubo"), "amarelo_tt"),
            ("roda_boba", roda_boba("corpo"), "metal"), ("roda_boba_espacadores", roda_boba("espacadores"), "latao"),
        ],
        "3_energia": [
            ("suporte_2x18650_com_chave", suporte_baterias(), "preto"), ("baterias_18650", baterias(), "azul_bat"),
            ("LM2596_placa", lm2596("placa"), "azul_pcb"), ("LM2596_componentes", lm2596("componentes"), "preto"),
            ("LM2596_display_5V", lm2596("display"), "display"), ("LM2596_trimpot", lm2596("trimpot"), "trimpot"),
            ("protoboard", protoboard(), "branco"),
            ("capacitor_470uF_pernas", cap_pernas, "metal"), ("capacitor_470uF", cap_corpo, "azul_cap"),
        ],
        "4_controle": [
            ("MX1508_placa", driver("placa"), "vermelho_pcb"), ("MX1508_chip", driver("chip"), "preto"),
            ("MX1508_barra_pinos", driver("barra"), "preto"), ("MX1508_pinos", driver("pinos"), "dourado"),
            ("resistor_10k_pernas", res_pernas, "metal"), ("resistor_10k", res_corpo, "bege"),
            ("ESP32CAM_placa", esp32cam("placa"), "verde_pcb"), ("ESP32CAM_camera", esp32cam("camera"), "preto"),
            ("ESP32CAM_blindagem", esp32cam("blindagem"), "metal"), ("ESP32CAM_flash", esp32cam("flash"), "branco"),
            ("ESP32CAM_barras_pinos", esp32cam("barras"), "preto"), ("ESP32CAM_pinos", esp32cam("pinos"), "dourado"),
        ],
        "5_fios": [(f"fio_{nome}", forma, cor) for nome, (cor, forma) in f.items()],
    }
    for cor, forma in trilhas_pb().items():
        grupos["3_energia"].append((f"protoboard_trilha_{cor}", forma, cor))
    grupos["5_fios"].append(("conectores_dupont", junta(*conectores), "preto"))
    return grupos


def como_shape(obj):
    return obj.val() if isinstance(obj, cq.Workplane) and len(obj.vals()) == 1 else (
        cq.Compound.makeCompound(obj.vals()) if isinstance(obj, cq.Workplane) else obj)


def main():
    grupos = montar()
    raiz = cq.Assembly(name="prototipo_bandejito")
    total = 0
    for nome_grupo, pecas in grupos.items():
        sub = cq.Assembly(name=nome_grupo)
        for nome, forma, cor in pecas:
            sub.add(como_shape(forma), name=nome, color=cq.Color(*CORES[cor]))
            total += 1
        raiz.add(sub, name=nome_grupo)
    destino = g.PASTA / "step" / "prototipo_completo.step"
    raiz.save(str(destino))
    print(f"[PROTOTIPO] {total} pecas em {len(grupos)} grupos -> {destino.relative_to(g.PASTA)}")

    if "--stl" in sys.argv:
        pasta = Path(sys.argv[sys.argv.index("--stl") + 1])
        pasta.mkdir(parents=True, exist_ok=True)
        linhas = []
        for nome_grupo, pecas in grupos.items():
            for nome, forma, cor in pecas:
                arq = pasta / f"{nome_grupo}__{nome}.stl"
                cq.exporters.export(cq.Workplane("XY").add(como_shape(forma)), str(arq),
                                    tolerance=0.05, angularTolerance=0.2)
                r, gg, b = CORES[cor]
                linhas.append(f'if (mostrar_{nome_grupo}) color([{r},{gg},{b}], alfa_{nome_grupo}) '
                              f'import("{arq.as_posix()}");')
        cab = "".join(f"mostrar_{n} = true;\nalfa_{n} = 1;\n" for n in grupos)
        (pasta / "cena.scad").write_text(cab + "\n".join(linhas) + "\n", encoding="utf-8")
        print(f"[PROTOTIPO] STLs + cena.scad em {pasta}")


if __name__ == "__main__":
    main()
