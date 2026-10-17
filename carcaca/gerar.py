"""Gera a carcaca (conceito B) a partir de medidas.txt.

Uma bandeja grande em cima de uma balanca: a celula de carga fica presa na
"base da balanca" (anel na coluna) e segura a "aranha" (suporte em X), que
segura a bandeja. A bandeja nao encosta em mais nada. O botao verde fica no
"nariz" da aranha, com o "capo" escondendo o corpo dele e os fios.
Coluna recuada (coluna_pos_y), pe antitombo e portinhas de encaixe.
A versao de 2 bandejas fica na marca Git bandejito-2-bandejas.

Saidas:
  step/<peca>.step   -> para abrir no Fusion 360 (solidos de verdade)
  step/montagem.step -> todas as pecas na posicao montada
  stl/<peca>.stl     -> para o fatiador da impressora 3D
Tambem copia as medidas para os valores padrao de robo_garcom_carcaca.scad,
para o OpenSCAD continuar mostrando o mesmo modelo.

Uso: .venv\\Scripts\\python.exe gerar.py   (ou dois cliques em GERAR.bat)
"""
import math
import re
import sys
from pathlib import Path

import cadquery as cq

PASTA = Path(__file__).resolve().parent


# ---------------------------------------------------------------------
# Medidas
# ---------------------------------------------------------------------
def ler_medidas(caminho):
    m = {}
    for n, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        dentro_aspas = False  # corta o comentario no 1o "#" fora de aspas
        for i, ch in enumerate(linha):
            if ch == '"':
                dentro_aspas = not dentro_aspas
            elif ch == "#" and not dentro_aspas:
                linha = linha[:i]
                break
        if not linha.strip():
            continue
        if "=" not in linha:
            sys.exit(f"[ERRO] medidas.txt, linha {n}: falta o '=' -> {linha.strip()}")
        chave, valor = (p.strip() for p in linha.split("=", 1))
        if valor.lower() in ("true", "false"):
            m[chave] = valor.lower() == "true"
        elif valor.startswith('"'):
            m[chave] = valor.strip('"')
        else:
            try:
                m[chave] = float(valor.replace(",", "."))
            except ValueError:
                sys.exit(f"[ERRO] medidas.txt, linha {n}: '{valor}' nao e um numero")
    return m


def sincronizar_scad(m, caminho):
    def fmt(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, str):
            return f'"{v}"'
        return f"{v:g}"

    with open(caminho, encoding="utf-8", newline="") as f:
        texto = f.read()
    for chave, valor in m.items():
        texto = re.sub(rf"^{chave} = .*?;", f"{chave} = {fmt(valor)};", texto, flags=re.M)
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


M = ler_medidas(PASTA / "medidas.txt")
globals().update(M)

W, L, H = chassi_largura, chassi_comprimento, saia_altura
coluna_altura = coluna_h1 + coluna_h2 + coluna_h3
fy = cab_profundidade / 2          # eixo da coluna ate a cara (na base)
cab_tras = fy - cab_profundidade   # plano de tras da cabeca
cab_r = 5                          # arredondado da cabeca
cab_piso = 3
cab_ressalto_d = coluna_d3 + 2 * folga + 8
tampa_encaixe = 4
aba_h = 8


# ---------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------
def caixa(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rrect(x, y, h, r):
    """Caixa centrada em XY com cantos verticais arredondados."""
    r = min(r, x / 2 - 0.01, y / 2 - 0.01)
    return cq.Workplane("XY").box(x, y, h, centered=(True, True, False)).edges("|Z").fillet(r)


def rcaixa(x0, x1, y0, y1, z0, z1, r):
    """Caixa com todas as arestas arredondadas."""
    return caixa(x0, x1, y0, y1, z0, z1).edges().fillet(r)


def cilindro(d, h, base=(0, 0, 0), direcao=(0, 0, 1)):
    return cq.Workplane("XY").add(cq.Solid.makeCylinder(d / 2, h, cq.Vector(*base), cq.Vector(*direcao)))


def dforma(d, h, extra=0.0):
    """Cilindro com um lado reto (encaixe que nao gira)."""
    return cilindro(d + 2 * extra, h).intersect(caixa(-d, d, -d, d / 2 - encaixe_corte + extra, -1, h + 1))


def quadro_placa(obj):
    """Leva do quadro da placa (origem = frente da lente) para a cabeca."""
    return obj.rotate((0, 0, 0), (1, 0, 0), -inclinacao).translate((0, fy - parede - 1, olho_z))


# ---------------------------------------------------------------------
# Contorno do chassi (visto de cima): corpo estreito com a frente curva
# e traseira larga em leque. Origem no meio do chassi, +y = frente.
# ---------------------------------------------------------------------
def contorno():
    w, xt = W / 2, chassi_largura_traseira / 2
    yf = L / 2 - frente_curva            # cantos da frente
    yb = -L / 2 + traseira_inicio        # onde o leque começa
    ytt = yb - 6                         # topo das pontas do leque
    yt = -L / 2 + traseira_ponta         # pontas do leque
    return (cq.Workplane("XY").moveTo(-w, yf).threePointArc((0, L / 2), (w, yf))
            .lineTo(w, yb).lineTo(xt, ytt).lineTo(xt, yt)
            .threePointArc((0, -L / 2), (-xt, yt))
            .lineTo(-xt, ytt).lineTo(-w, yb).close())


def prisma(h, recuo=0.0, z=0.0, raio=None):
    """Contorno do chassi extrudado; recuo > 0 encolhe (para dentro)."""
    wp = contorno()
    if recuo:
        wp = wp.offset2D(-recuo, kind="arc")
    p = wp.extrude(h)
    r = saia_raio_canto if raio is None else raio
    if r > 0.5:
        try:
            p = p.edges("|Z").fillet(r)
        except Exception:
            pass   # algum canto apertado demais para arredondar: fica vivo
    return p.translate((0, 0, z))


# ---------------------------------------------------------------------
# Saia
# ---------------------------------------------------------------------
def furo(sx, sy):
    """sy = +1: par da frente; sy = -1: par de trás."""
    if sy > 0:
        return (sx * furo_frente_x, furo_frente_y)
    return (sx * furo_tras_x, furo_tras_y)


def saia():
    R0, rin = saia_recuo, saia_raio_canto - parede   # a saia fica R0 para dentro da borda da base
    corpo = prisma(H, R0).cut(prisma(H - saia_teto + 1, R0 + parede, -1, rin))
    vao = prisma(H - saia_teto, R0 + parede, raio=rin)   # espaço de dentro

    # Abas de fixacao com rampa de 45 graus (imprime sem suporte): de cada
    # furo, uma rampa sobe em diagonal para fora até encostar na parede.
    abas = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy = furo(sx, sy)
            dist = 30
            cx, cy = hx + sx * dist / math.sqrt(2), hy + sy * dist / math.sqrt(2)
            ang = math.degrees(math.atan2(cy - hy, cx - hx))
            base = (cq.Workplane("XY").center((hx + cx) / 2, (hy + cy) / 2)
                    .slot2D(dist + 12, 12, ang).extrude(aba_h))
            rampa = cq.Workplane("XY").add(cq.Solid.makeLoft([
                cq.Wire.makeCircle(6, cq.Vector(hx, hy, aba_h), cq.Vector(0, 0, 1)),
                cq.Wire.makeCircle(6, cq.Vector(cx, cy, aba_h + dist), cq.Vector(0, 0, 1)),
            ]))
            aba = base.union(rampa)
            abas = aba if abas is None else abas.union(aba)
    corpo = corpo.union(abas.intersect(vao))

    # Encaixe da coluna (por dentro do teto)
    corpo = corpo.union(cilindro(coluna_d1 + 2 * folga + 8, encaixe_prof + 3,
                                 (0, coluna_pos_y, H - encaixe_prof - 3)))

    cortes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy = furo(sx, sy)
            cortes.append(cilindro(furo_parafuso, aba_h + 1, (hx, hy, -1)))
    cortes.append(dforma(coluna_d1, encaixe_prof + 1, folga).translate((0, coluna_pos_y, H - encaixe_prof)))
    cortes.append(cilindro(canal_fios, 10, (0, coluna_pos_y, H - encaixe_prof - 5)))
    # Rodas (ficam do lado de fora do corpo; só cortam a saia se encostarem nela)
    larg = roda_largura + 2 * roda_folga
    if roda_pos_x - larg / 2 < W / 2 - R0:
        print(f"[AVISO] a roda (com a folga) encosta na parede da saia: vai abrir um recorte na lateral. "
              f"Aumente saia_recuo ou confira roda_pos_x")
    for sx in (-1, 1):
        cortes.append(cilindro(roda_diametro + 2 * roda_folga, larg,
                               (sx * roda_pos_x - larg / 2, roda_pos_y, roda_eixo_z), (1, 0, 0)))
    if abertura_traseira:   # atravessa a parede curva de trás
        cortes.append(caixa(-abertura_traseira_largura / 2, abertura_traseira_largura / 2,
                            -L / 2 - 1, -L / 2 + traseira_ponta + parede + 2, -1, abertura_traseira_altura))
    if abertura_lateral:    # v2: pilhas na frente saem pelo lado (só a parede, embaixo da bandeja)
        xp = abertura_lateral_lado * (W / 2 - R0)
        y0 = abertura_lateral_pos_y - abertura_lateral_largura / 2
        cortes.append(caixa(xp - 2 * parede, xp + 2 * parede, y0, y0 + abertura_lateral_largura,
                            -1, abertura_lateral_altura))
    cortes.append(cilindro(8, saia_teto + 2, (FURO_FIOS[0], FURO_FIOS[1], H - saia_teto - 1)))  # fios da balanca
    if furo_chave:
        cortes.append(rrect(chave_largura, chave_comprimento, saia_teto + 2, 2)
                      .translate((chave_pos_x, chave_pos_y, H - saia_teto - 1)))
    # Ventilacao nas laterais (v2: só no lado sem a abertura lateral)
    for sx in (-1, 1):
        if abertura_lateral and sx == abertura_lateral_lado:
            continue
        for i in range(5):
            y = 25 + i * 13
            xp = sx * (W / 2 - R0)
            cortes.append(caixa(xp - 2 * parede, xp + 2 * parede, y - 2, y + 2, H - 21, H - 7))
    # Nome na frente: a frente é curva, então o texto atravessa a frente toda e
    # só a "casca" de 0,8 mm da parede é cortada (gravação com profundidade igual)
    if nome:
        txt = (cq.Workplane("XY")
               .text(nome, nome_tamanho, frente_curva + 12, font="Arial", kind="bold",
                     halign="center", valign="center")
               .rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180)
               .translate((0, L / 2 + 1 - (frente_curva + 12), H * 0.45)))   # o texto cresce para +y
        bb = txt.val().BoundingBox()
        if bb.xlen > W - 2 * saia_raio_canto - 6:
            print(f"[AVISO] o nome tem {bb.xlen:.0f} mm e a frente {W:.0f} mm: diminua nome_tamanho")
        cortes.append(txt.intersect(prisma(H, R0).cut(prisma(H + 2, R0 + 0.8, -1))))

    for c in cortes:
        corpo = corpo.cut(c)
    # Letras com partes sobrepostas (ex.: cedilha do Ç) podem deixar uma lasca
    # encostada na parede como solido separado: funde tudo de volta
    solidos = corpo.solids().vals()
    if len(solidos) > 1:
        corpo = cq.Workplane("XY").add(solidos[0].fuse(*solidos[1:]).clean())
    return corpo


# ---------------------------------------------------------------------
# Coluna
# ---------------------------------------------------------------------
def coluna():
    # Todos os trechos com lado reto: a base da balanca e a cabeca nao giram
    c = (dforma(coluna_d1, coluna_h1)
         .union(dforma(coluna_d2, coluna_h2).translate((0, 0, coluna_h1)))
         .union(dforma(coluna_d3, coluna_h3).translate((0, 0, coluna_h1 + coluna_h2))))
    return c.cut(cilindro(canal_fios, coluna_altura + 2, (0, 0, -1)))


# ---------------------------------------------------------------------
# Bandeja e balanca. Tudo desenhado na posicao montada (origem = meio do
# chassi, z = 0 no topo da base de acrilico); as pecas impressas sao
# levadas para a mesa da impressora em PECAS.
# ---------------------------------------------------------------------
ZB = H + bandeja_altura                       # fundo da bandeja
ZC = H + celula_base                          # embaixo da celula
ZS = ZC + celula_lado                         # em cima da celula = embaixo da aranha
CEL_Y0 = celula_pos_y                         # ponta presa
CEL_Y1 = celula_pos_y + celula_comprimento    # ponta solta
HUB_Y = CEL_Y1 - (celula_furo_1 + celula_furo_2) / 2   # meio dos 2 furos da ponta solta
FUROS_PRESA = (CEL_Y0 + celula_furo_1, CEL_Y0 + celula_furo_2)
FUROS_SOLTA = (CEL_Y1 - celula_furo_1, CEL_Y1 - celula_furo_2)
FURO_COLUNA = coluna_d1 + 2 * bandeja_folga_coluna       # recorte da bandeja em volta da coluna
Y_FRENTE = bandeja_pos_y + bandeja_comprimento / 2
BY = Y_FRENTE + botao_avanco                  # centro do botao
NARIZ_R = 12                                  # raio do "nariz" que segura o botao
PONTAS = [(sx * (bandeja_largura / 2 - aranha_ponta), bandeja_pos_y + sy * (bandeja_comprimento / 2 - aranha_ponta))
          for sy in (-1, 1) for sx in (-1, 1)]
PINO_D, PINO_H = 4, 2.5                       # pinos da aranha que seguram a bandeja
FURO_FIOS = (celula_lado / 2 + 8, CEL_Y0 + 12)   # furo no teto da saia: fios da celula e do botao
ANEL_BASE_D = coluna_d1 + 2 * folga + 6
CAPO_Z0 = ZB - 3 - 24                         # fundo do capo (o botao tem ~21 mm embaixo do painel)


def forma_bandeja(recuo, h):
    """Contorno da bandeja (com o recorte da coluna) encolhido 'recuo' mm, extrudado h."""
    corpo = rrect(bandeja_largura - 2 * recuo, bandeja_comprimento - 2 * recuo, h,
                  bandeja_raio_canto - recuo).translate((0, bandeja_pos_y, 0))
    d = FURO_COLUNA + 2 * recuo
    recorte = (cilindro(d, h + 2, (0, coluna_pos_y, -1))
               .union(caixa(-d / 2, d / 2, -L, coluna_pos_y, -1, h + 1)))
    return corpo.cut(recorte)


def bandeja():
    """Bandeja unica: sem fio e sem parafuso; encaixa nos 4 pinos da aranha."""
    b = forma_bandeja(0, bandeja_esp).union(forma_bandeja(0, bandeja_borda).cut(forma_bandeja(2.4, bandeja_borda + 2)))
    for x, y in PONTAS:
        b = b.cut(cilindro(PINO_D + 0.4, bandeja_esp + 2, (x, y, -1)))
    return b


def base_balanca():
    """Anel na coluna + pe que segura a ponta presa da celula + batente embaixo da ponta solta."""
    b = cilindro(ANEL_BASE_D, 20, (0, coluna_pos_y, H))
    b = b.union(caixa(-8, 8, coluna_pos_y, CEL_Y0 + 20, H, ZC))
    b = b.union(caixa(-3, 3, CEL_Y0 + 19, CEL_Y1 - 2, H, ZC - 3))           # batente (parafuso M3 regula a folga)
    b = b.cut(dforma(coluna_d1, 22, folga).translate((0, coluna_pos_y, H - 1)))
    for y in FUROS_PRESA:
        b = b.cut(cilindro(celula_parafuso + 0.4, celula_base + 2, (0, y, H - 1)))
        b = b.cut(cilindro(8, 4, (0, y, H - 1)))                             # cabeca do parafuso, por baixo
    b = b.cut(cilindro(2.8, 10, (0, HUB_Y, H - 1)))                          # parafuso-batente M3
    return b


def aranha():
    """Suporte em X parafusado na ponta solta da celula; a bandeja so encosta nele.
    O braco da frente vira o nariz do botao (os fios correm num canal por baixo)."""
    h = ZB - ZS
    a = caixa(-12, 12, HUB_Y - 12, HUB_Y + 12, ZS, ZB)
    for x, y in PONTAS + [(0, BY)]:
        larg = 10 if x == 0 else aranha_largura
        ang = math.atan2(y - HUB_Y, x)
        nx, ny = -math.sin(ang) * larg / 2, math.cos(ang) * larg / 2
        braco = (cq.Workplane("XY").polyline([(nx, HUB_Y + ny), (x + nx, y + ny), (x - nx, y - ny), (-nx, HUB_Y - ny)])
                 .close().extrude(h).translate((0, 0, ZS)))
        a = a.union(braco).union(cilindro(larg, h, (x, y, ZS)))
    a = a.union(cilindro(2 * NARIZ_R, h, (0, BY, ZS)))
    for x, y in PONTAS:
        a = a.union(cilindro(PINO_D, PINO_H, (x, y, ZB)))
    if botao:   # aro de protecao (um prato nao aperta sem querer); fica na frente da borda da bandeja
        a = a.union(cilindro(21, 6, (0, BY, ZB)).cut(cilindro(17, 8, (0, BY, ZB - 1))))
    cortes = [
        caixa(-celula_lado / 2 - 1.5, celula_lado / 2 + 1.5, CEL_Y0 - 1, HUB_Y - 12, ZS - 1, ZS + 1.5),  # nao encosta na celula
        cilindro(20, h - 3 + 1, (0, BY, ZS - 1)),                               # vao da porca do botao
        caixa(-2.5, 2.5, HUB_Y + 12 - 1, BY - 8, ZS - 1, ZS + 3.5),             # canal dos fios por baixo
    ]
    if botao:
        cortes.append(cilindro(botao_furo, h + 2, (0, BY, ZS)))
    for y in FUROS_SOLTA:
        cortes.append(cilindro(celula_parafuso + 0.4, h + 2, (0, y, ZS - 1)))
        cortes.append(cilindro(8, 4, (0, y, ZB - 3.5)))                        # cabeca do parafuso, por cima
    for c in cortes:
        a = a.cut(c)
    return a


def capo_botao():
    """Copinho que encaixa por baixo do nariz e esconde o corpo do botao e os fios."""
    alto = ZS - CAPO_Z0
    copo = cq.Workplane("XY").add(cq.Solid.makeCone(8, NARIZ_R, alto, cq.Vector(0, BY, CAPO_Z0)))
    copo = copo.cut(cq.Workplane("XY").add(cq.Solid.makeCone(6.5, NARIZ_R - 1.6, alto, cq.Vector(0, BY, CAPO_Z0 + 1.6))))
    encaixe = (cilindro(19.6, 4, (0, BY, ZS - 0.01)).union(cilindro(2 * NARIZ_R, 1.5, (0, BY, ZS - 1.5)))
               .cut(cilindro(16, 8, (0, BY, ZS - 3))))                            # anel que entra no nariz + tampa
    encaixe = encaixe.cut(caixa(-3, 3, BY - 11, BY - 7, ZS - 3, ZS + 5))       # passagem dos fios (para tras)
    return copo.union(encaixe)


def celula():
    """Celula de carga (comprada, NAO imprime): so para a montagem e o prototipo."""
    c = caixa(-celula_lado / 2, celula_lado / 2, CEL_Y0, CEL_Y1, ZC, ZS)
    m = celula_comprimento / 2
    c = c.cut(caixa(-celula_lado, celula_lado, CEL_Y0 + m - 10, CEL_Y0 + m + 10, ZC + 2.5, ZS - 2.5))
    for y in FUROS_PRESA + FUROS_SOLTA:
        c = c.cut(cilindro(celula_parafuso, celula_lado + 2, (0, y, ZC - 1)))
    return c


# ---------------------------------------------------------------------
# Cabeca e tampa
# ---------------------------------------------------------------------
def cab_externo():
    return rcaixa(-cab_largura / 2, cab_largura / 2, cab_tras, fy, 0, cab_altura, cab_r)


def cab_cavidade(f=0.0):
    return rcaixa(-cab_largura / 2 + parede + f, cab_largura / 2 - parede - f,
                  cab_tras - 10, fy - parede - f,
                  cab_piso + f, cab_altura - parede - f, cab_r - parede - f)


def cabeca():
    p_frente = -lente_altura
    p_tras = p_frente - placa_esp
    p_topo = lente_do_topo
    p_base = lente_do_topo - placa_altura

    corpo = cab_externo().cut(cab_cavidade())
    corpo = corpo.union(cilindro(cab_ressalto_d, encaixe_prof + 3).intersect(cab_externo()))

    # Suporte da placa: 4 apoios, guias laterais e batente (vao ate a cara)
    sup = None
    pecas = []
    for sx in (-1, 1):
        for z in (p_base + 1.5, p_topo - 4.5):
            x0 = sx * (placa_largura / 2 - 3) - 1.5
            pecas.append(caixa(x0, x0 + 3, p_frente, p_frente + 20, z, z + 3))
        x0 = placa_largura / 2 + folga if sx > 0 else -placa_largura / 2 - folga - 2
        pecas.append(caixa(x0, x0 + 2, p_tras - 1.5, p_tras + 23.5, p_base - folga - 2, p_base + placa_altura))
    pecas.append(caixa(-placa_largura / 2 - folga - 2, placa_largura / 2 + folga + 2,
                       p_tras - 1.5, p_tras + 23.5, p_base - folga - 2, p_base - folga))
    for p in pecas:
        sup = p if sup is None else sup.union(p)
    sup = quadro_placa(sup).intersect(caixa(-100, 100, -100, fy - parede + 0.01, -100, 300))
    corpo = corpo.union(sup)

    cortes = [
        dforma(coluna_d3, encaixe_prof + 0.01, folga).translate((0, 0, -0.01)),
        cilindro(canal_fios, encaixe_prof + 10),
    ]
    # Janela da lente em cone e janela do flash (no quadro da placa)
    r2 = lente_janela / 2 + 20 * math.tan(math.radians(campo_visao / 2))
    cone = cq.Workplane("XY").add(cq.Solid.makeCone(lente_janela / 2, r2, 20,
                                                    cq.Vector(lente_x, 0, 0), cq.Vector(0, 1, 0)))
    cortes.append(quadro_placa(cone))
    zf = p_topo - flash_do_topo
    cortes.append(quadro_placa(caixa(flash_x - flash_janela_largura / 2, flash_x + flash_janela_largura / 2,
                                     -2, 18, zf - flash_janela_altura / 2, zf + flash_janela_altura / 2)))
    # Frestas no topo
    for i in range(-2, 3):
        yc = cab_tras + cab_profundidade * 0.4
        cortes.append(caixa(i * 7 - 1.5, i * 7 + 1.5, yc - cab_profundidade * 0.225, yc + cab_profundidade * 0.225,
                            cab_altura - parede - 1, cab_altura + 1))
    # Sorriso
    if boca:
        arco = (cq.Workplane("XZ").circle(6.5).circle(5.2).extrude(-1.0)
                .intersect(caixa(-8, 8, -5, 5, -8, -2))
                .translate((0, fy - 0.8, olho_z - 16)))
        cortes.append(arco)

    for c in cortes:
        corpo = corpo.cut(c)
    return corpo


# Apoio antitombo (v2): aba parafusada embaixo da base + parede + ponta redonda
# (desliza se encostar no chao). Ja desenhado na posicao montada.
CHAO_Z = roda_eixo_z - roda_diametro / 2          # chao, em relacao ao topo da base


def pe_antitombo():
    yc, w = antitombo_pos_y, antitombo_largura
    base_z = -3                                   # embaixo da base de acrilico (3 mm)
    r = 5
    zc = CHAO_Z + antitombo_folga + r             # centro da ponta redonda
    aba = caixa(-w / 2, w / 2, yc - 8, yc + 8, base_z - 4, base_z)
    parede_pe = caixa(-w / 2, w / 2, yc - 3, yc + 3, zc, base_z - 3.99)
    p = aba.union(parede_pe).union(cilindro(2 * r, w, (-w / 2, yc, zc), (1, 0, 0)))
    try:
        p = p.edges("|X").fillet(1.5)             # quinas da aba e da parede arredondadas
    except Exception:
        pass
    for sx in (-1, 1):
        p = p.cut(cilindro(furo_parafuso, 12, (sx * antitombo_furos_x, yc, base_z - 11.99)))
    return p


def cabeca_tampa():
    placa = (rcaixa(-cab_largura / 2, cab_largura / 2, cab_tras - 10, fy, 0, cab_altura, cab_r)
             .intersect(caixa(-100, 100, cab_tras - 2, cab_tras, -100, 300)))
    encaixe = cab_cavidade(folga).intersect(caixa(-100, 100, cab_tras - 0.01, cab_tras + tampa_encaixe, -100, 300))
    pino = (quadro_placa(caixa(-3, 3, -lente_altura - placa_esp - 60, -lente_altura - placa_esp,
                               lente_do_topo - placa_altura / 2 - 3, lente_do_topo - placa_altura / 2 + 3))
            .intersect(caixa(-100, 100, cab_tras - 1, 100, -100, 300)))
    return placa.union(encaixe).union(pino)


# ---------------------------------------------------------------------
# Geracao
# ---------------------------------------------------------------------
coluna_z0 = H - encaixe_prof
cabeca_z0 = coluna_z0 + coluna_altura - encaixe_prof

PECAS = {
    # nome: (funcao, posicao de impressao, posicao na montagem)
    "saia": (saia,
             lambda o: o.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, H)),
             lambda o: o),
    "coluna": (coluna, lambda o: o,
               lambda o: o.translate((0, coluna_pos_y, coluna_z0))),
    "bandeja": (bandeja, lambda o: o, lambda o: o.translate((0, 0, ZB))),
    "base_balanca": (base_balanca, lambda o: o.translate((0, 0, -H)), lambda o: o),
    "aranha": (aranha, lambda o: o.translate((0, 0, -ZS)), lambda o: o),
    "cabeca": (cabeca,
               lambda o: o.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, fy)),
               lambda o: o.translate((0, coluna_pos_y, cabeca_z0))),
    "cabeca_tampa": (cabeca_tampa,
                     lambda o: o.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 0, 2 - cab_tras)),
                     lambda o: o.translate((0, coluna_pos_y, cabeca_z0))),
}
if botao:
    PECAS["capo_botao"] = (capo_botao, lambda o: o.translate((0, 0, -CAPO_Z0)), lambda o: o)
if antitombo:   # em pe na mesa (o perfil para baixo): imprime sem suporte
    PECAS["pe_antitombo"] = (pe_antitombo, lambda o: o.rotate((0, 0, 0), (0, 1, 0), 90), lambda o: o)


# ---------------------------------------------------------------------
# Portinhas de encaixe (v2): fecham a abertura de tras e a lateral.
# Por fora: moldura de 1,5 mm (nao deixa entrar demais). Por dentro: placa de
# reforco, aba-gancho em cima (entra atras da parede: encaixe inclinado) e
# 2 ressaltos embaixo que dao o "clique" atras da parede. Puxador embaixo.
# Desenhadas na posicao montada; imprimem em pe (a borda de baixo na mesa).
# ---------------------------------------------------------------------
TAMPA_FOLGA = portinha_folga   # do medidas.txt
TAMPA_MOLDURA = 4        # quanto a moldura passa da abertura (lados e em cima)
TAMPA_ESP_FORA = 1.5     # espessura da moldura por fora
TAMPA_ESP_DENTRO = 1.2   # placa de reforco por dentro
TAMPA_ABA = 4            # quanto a aba-gancho sobe atras da parede
TAMPA_RESSALTO = 0.5     # quanto o ressalto passa da beirada da abertura


def casca(a, b, z0, z1):
    """Faixa do contorno da saia entre os recuos a e b (a < b), de z0 a z1."""
    return prisma(z1 - z0, saia_recuo + a, z0).cut(prisma(z1 - z0 + 2, saia_recuo + b, z0 - 1))


def tampa(eixo, u0, u1, v0, v1, altura, z_clique=3):
    """eixo 'x': abertura de tras (a largura corre em x); 'y': lateral (largura em y).
    u0..u1 = largura da abertura; v0..v1 = faixa do outro eixo que pega so a parede certa.
    z_clique = altura dos ressaltos (longe das abas dos parafusos da saia)."""
    f, m = TAMPA_FOLGA, TAMPA_MOLDURA
    def caixa_uv(a0, a1, z0, z1):
        return caixa(a0, a1, v0, v1, z0, z1) if eixo == "x" else caixa(v0, v1, a0, a1, z0, z1)
    tampao = casca(-0.01, parede, 0, altura - f).intersect(caixa_uv(u0 + f, u1 - f, 0, altura - f))
    moldura = casca(-TAMPA_ESP_FORA, 0, 0, altura + m).intersect(caixa_uv(u0 - m, u1 + m, 0, altura + m))
    reforco = casca(parede - 0.01, parede + f + TAMPA_ESP_DENTRO, 0, altura - f).intersect(
        caixa_uv(u0 + f, u1 - f, 0, altura - f))
    aba = casca(parede + f, parede + f + TAMPA_ESP_DENTRO, altura - 8, altura + TAMPA_ABA).intersect(
        caixa_uv(u0 + 8, u1 - 8, altura - 8, altura + TAMPA_ABA))
    t = moldura.union(tampao).union(reforco).union(aba)
    for a0, a1 in ((u0 - TAMPA_RESSALTO, u0 + f + 3), (u1 - f - 3, u1 + TAMPA_RESSALTO)):   # ressaltos do clique
        t = t.union(casca(parede + f, parede + f + TAMPA_ESP_DENTRO, z_clique, z_clique + 6)
                    .intersect(caixa_uv(a0, a1, z_clique, z_clique + 6)))
    meio = (u0 + u1) / 2                                                                     # puxador
    t = t.union(casca(-TAMPA_ESP_FORA - 3, -TAMPA_ESP_FORA + 0.01, 0, 5).intersect(caixa_uv(meio - 10, meio + 10, 0, 5)))
    return t


def tampa_traseira():
    a = abertura_traseira_largura / 2
    return tampa("x", -a, a, -L / 2 - 6, -L / 2 + traseira_ponta + parede + 8, abertura_traseira_altura)


def tampa_lateral():
    xp = abertura_lateral_lado * (W / 2 - saia_recuo)
    y0 = abertura_lateral_pos_y - abertura_lateral_largura / 2
    return tampa("y", y0, y0 + abertura_lateral_largura, xp - 8, xp + 8, abertura_lateral_altura,
                 z_clique=24)   # embaixo, na frente, fica a aba do parafuso da saia


if portinhas and abertura_traseira:
    PECAS["tampa_traseira"] = (tampa_traseira, lambda o: o, lambda o: o)
if portinhas and abertura_lateral:
    PECAS["tampa_lateral"] = (tampa_lateral, lambda o: o, lambda o: o)


CORES = {"saia": (0.91, 0.89, 0.82), "coluna": (0.85, 0.82, 0.74), "bandeja": (0.79, 0.44, 0.23),
         "base_balanca": (0.85, 0.82, 0.74), "aranha": (0.85, 0.82, 0.74), "capo_botao": (0.85, 0.82, 0.74),
         "pe_antitombo": (0.85, 0.82, 0.74), "tampa_traseira": (0.91, 0.89, 0.82),
         "tampa_lateral": (0.91, 0.89, 0.82), "cabeca": (0.95, 0.93, 0.89), "cabeca_tampa": (0.54, 0.52, 0.47)}


def main():
    (PASTA / "step").mkdir(exist_ok=True)
    (PASTA / "stl").mkdir(exist_ok=True)
    print(f"[CARCACA] {len(M)} medidas lidas de medidas.txt")
    montagem = cq.Assembly(name="robo_garcom")
    erros = 0
    impressas = {}
    for nome_peca, (func, impressao, montada) in PECAS.items():
        print(f"[CARCACA] gerando {nome_peca}...", flush=True)
        obj = func()
        solidos = obj.solids().vals()
        valido = len(solidos) == 1 and solidos[0].isValid()
        if not valido:
            erros += 1
            print(f"[ERRO] {nome_peca}: {len(solidos)} solido(s), valido={solidos[0].isValid() if solidos else False}")
        p = impressao(obj)
        impressas[nome_peca] = p
        cq.exporters.export(p, str(PASTA / "step" / f"{nome_peca}.step"))
        cq.exporters.export(p, str(PASTA / "stl" / f"{nome_peca}.stl"), tolerance=0.02, angularTolerance=0.1)
        bb = p.val().BoundingBox()
        print(f"           {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, volume {p.val().Volume()/1000:.1f} cm3")
        montagem.add(montada(obj), name=nome_peca, color=cq.Color(*CORES[nome_peca]))
    montagem.add(celula(), name="celula_de_carga_500g_COMPRADA", color=cq.Color(0.78, 0.80, 0.82))
    montagem.save(str(PASTA / "step" / "montagem.step"))
    for velho in (PASTA / "step").glob("*.step"):   # pecas que nao existem mais
        if velho.stem not in PECAS and velho.stem not in ("montagem", "prototipo_completo"):
            velho.unlink()
            print(f"[CARCACA] apagado step\\{velho.name} (peca que nao existe mais)")
    for velho in (PASTA / "stl").glob("*.stl"):
        if velho.stem not in PECAS:
            velho.unlink()
            print(f"[CARCACA] apagado stl\\{velho.name} (peca que nao existe mais)")
    sincronizar_scad(M, PASTA / "robo_garcom_carcaca.scad")
    print("[CARCACA] OpenSCAD atualizado com as mesmas medidas")

    # Bandejas de impressao (ordem combinada: cabeca primeiro, como teste)
    import bandeja_3mf
    print(f"[CARCACA] bandejas de impressao (mesa de {mesa_impressora:.0f} mm) em impressao\\:")
    p = impressas
    erros += bandeja_3mf.montar(PASTA / "impressao", [
        ("1_cabeca_e_tampa_TESTE", [("cabeca", p["cabeca"], 60, 110, 0),
                                    ("cabeca_tampa", p["cabeca_tampa"], 150, 110, 0)]
                                   + ([("tampa_traseira", p["tampa_traseira"], 60, 182, 0)] if "tampa_traseira" in p else [])
                                   + ([("tampa_lateral", p["tampa_lateral"], 160, 182, 90)] if "tampa_lateral" in p else [])
                                   + ([("capo_botao", p["capo_botao"], 110, 30, 0)] if "capo_botao" in p else [])),
        ("2_saia", [("saia", p["saia"], 110, 110, 0)]),
        ("3_bandeja_coluna_e_pe", [("bandeja", p["bandeja"], 80, 110, 0),
                                   ("coluna", p["coluna"], 185, 150, 0)]
                                  + ([("pe_antitombo", p["pe_antitombo"], 185, 45, 0)] if antitombo else [])),
        ("4_aranha_e_base_da_balanca", [("aranha", p["aranha"], 68, 110, 0),
                                        ("base_balanca", p["base_balanca"], 180, 110, 0)]),
    ], mesa_impressora)
    if erros:
        sys.exit(f"[ERRO] {erros} peca(s) ou bandeja(s) com problema. Confira as medidas.")
    print("[CARCACA] pronto: step\\ (Fusion 360), stl\\ (pecas avulsas) e impressao\\ (bandejas prontas)")


if __name__ == "__main__":
    main()
