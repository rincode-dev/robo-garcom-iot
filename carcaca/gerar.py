"""Gera a carcaca (conceito B) a partir de medidas.txt.

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
if bandeja_formato not in ("retangular", "redonda"):
    sys.exit(f'[ERRO] medidas.txt: bandeja_formato = "{bandeja_formato}"; use "retangular" ou "redonda"')

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
# Saia
# ---------------------------------------------------------------------
def furo(sx, sy):
    return (sx * furos_dist_x / 2, furos_desloc_y + sy * furos_dist_y / 2)


def saia():
    corpo = rrect(W, L, H, saia_raio_canto).cut(
        rrect(W - 2 * parede, L - 2 * parede, H - saia_teto + 1, saia_raio_canto - parede).translate((0, 0, -1)))

    # Abas de fixacao com rampa de 45 graus (imprime sem suporte)
    abas = None
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx, hy = furo(sx, sy)
            cx, cy = sx * W / 2, sy * L / 2
            dist = math.hypot(cx - hx, cy - hy)
            ang = math.degrees(math.atan2(cy - hy, cx - hx))
            base = (cq.Workplane("XY").center((hx + cx) / 2, (hy + cy) / 2)
                    .slot2D(dist + 12, 12, ang).extrude(aba_h))
            rampa = cq.Workplane("XY").add(cq.Solid.makeLoft([
                cq.Wire.makeCircle(6, cq.Vector(hx, hy, aba_h), cq.Vector(0, 0, 1)),
                cq.Wire.makeCircle(6, cq.Vector(cx, cy, aba_h + dist), cq.Vector(0, 0, 1)),
            ]))
            aba = base.union(rampa)
            abas = aba if abas is None else abas.union(aba)
    corpo = corpo.union(abas.intersect(rrect(W, L, H - saia_teto, saia_raio_canto)))

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
    # Rodas
    larg = roda_largura + 2 * roda_folga + 1
    for sx in (-1, 1):
        cx = sx * (W / 2 - (roda_largura + 2 * roda_folga) / 2 + 0.5)
        cortes.append(cilindro(roda_diametro + 2 * roda_folga, larg, (cx - larg / 2, roda_pos_y, roda_eixo_z), (1, 0, 0)))
    if abertura_traseira:
        cortes.append(caixa(-abertura_traseira_largura / 2, abertura_traseira_largura / 2,
                            -L / 2 - 1, -L / 2 + parede + 1, -1, abertura_traseira_altura))
    if furo_chave:
        cortes.append(rrect(chave_largura, chave_comprimento, saia_teto + 2, 2)
                      .translate((chave_pos_x, chave_pos_y, H - saia_teto - 1)))
    # Ventilacao nas laterais
    for sx in (-1, 1):
        for i in range(5):
            y = 25 + i * 13
            cortes.append(caixa(sx * W / 2 - 2 * parede, sx * W / 2 + 2 * parede, y - 2, y + 2, H - 21, H - 7))
    # Nome na frente
    if nome:
        txt = (cq.Workplane("XY")
               .text(nome, nome_tamanho, 1.5, font="Arial", kind="bold", halign="center", valign="center")
               .rotate((0, 0, 0), (1, 0, 0), 90).rotate((0, 0, 0), (0, 0, 1), 180)
               .translate((0, L / 2 - 0.8, H * 0.45)))
        cortes.append(txt)

    for c in cortes:
        corpo = corpo.cut(c)
    # Letras com partes sobrepostas (ex.: cedilha do Ç) podem deixar uma lasca
    # encostada na parede como solido separado: funde tudo de volta
    solidos = corpo.solids().vals()
    if len(solidos) > 1:
        corpo = cq.Workplane("XY").add(solidos[0].fuse(*solidos[1:]).clean())
    return corpo


# ---------------------------------------------------------------------
# Coluna e bandejas
# ---------------------------------------------------------------------
def coluna():
    # Trechos do meio e de cima com lado reto: as bandejas nao giram
    c = (dforma(coluna_d1, encaixe_prof + 0.01)
         .union(cilindro(coluna_d1, coluna_h1 - encaixe_prof, (0, 0, encaixe_prof)))
         .union(dforma(coluna_d2, coluna_h2).translate((0, 0, coluna_h1)))
         .union(dforma(coluna_d3, coluna_h3).translate((0, 0, coluna_h1 + coluna_h2))))
    return c.cut(cilindro(canal_fios, coluna_altura + 2, (0, 0, -1)))


def bandeja(largura, comprimento, d, coluna_d):
    def forma(recuo, h, z=0.0):
        if bandeja_formato == "redonda":
            return cilindro(d - 2 * recuo, h, (0, 0, z))
        return rrect(largura - 2 * recuo, comprimento - 2 * recuo, h, bandeja_raio_canto - recuo).translate((0, 0, z))

    b = (forma(0, bandeja_esp)
         .union(forma(0, bandeja_borda).cut(forma(2.4, bandeja_borda + 2, -1)))
         .union(cilindro(coluna_d + 2 * folga + 8, bandeja_esp + bandeja_colar)))
    return b.cut(dforma(coluna_d, bandeja_esp + bandeja_colar + 2, folga).translate((0, 0, -1)))


def bandeja_baixo():
    return bandeja(bandeja_baixo_largura, bandeja_baixo_comprimento, bandeja_baixo_d, coluna_d2)


def bandeja_cima():
    return bandeja(bandeja_cima_largura, bandeja_cima_comprimento, bandeja_cima_d, coluna_d3)


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
    "bandeja_baixo": (bandeja_baixo, lambda o: o,
                      lambda o: o.translate((0, coluna_pos_y, coluna_z0 + coluna_h1))),
    "bandeja_cima": (bandeja_cima, lambda o: o,
                     lambda o: o.translate((0, coluna_pos_y, coluna_z0 + coluna_h1 + coluna_h2))),
    "cabeca": (cabeca,
               lambda o: o.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, fy)),
               lambda o: o.translate((0, coluna_pos_y, cabeca_z0))),
    "cabeca_tampa": (cabeca_tampa,
                     lambda o: o.rotate((0, 0, 0), (1, 0, 0), 90).translate((0, 0, 2 - cab_tras)),
                     lambda o: o.translate((0, coluna_pos_y, cabeca_z0))),
}

CORES = {"saia": (0.91, 0.89, 0.82), "coluna": (0.85, 0.82, 0.74), "bandeja_baixo": (0.79, 0.44, 0.23),
         "bandeja_cima": (0.79, 0.44, 0.23), "cabeca": (0.95, 0.93, 0.89), "cabeca_tampa": (0.54, 0.52, 0.47)}


def main():
    (PASTA / "step").mkdir(exist_ok=True)
    (PASTA / "stl").mkdir(exist_ok=True)
    print(f"[CARCACA] {len(M)} medidas lidas de medidas.txt")
    montagem = cq.Assembly(name="robo_garcom")
    erros = 0
    for nome_peca, (func, impressao, montada) in PECAS.items():
        print(f"[CARCACA] gerando {nome_peca}...", flush=True)
        obj = func()
        solidos = obj.solids().vals()
        valido = len(solidos) == 1 and solidos[0].isValid()
        if not valido:
            erros += 1
            print(f"[ERRO] {nome_peca}: {len(solidos)} solido(s), valido={solidos[0].isValid() if solidos else False}")
        p = impressao(obj)
        cq.exporters.export(p, str(PASTA / "step" / f"{nome_peca}.step"))
        cq.exporters.export(p, str(PASTA / "stl" / f"{nome_peca}.stl"), tolerance=0.02, angularTolerance=0.1)
        bb = p.val().BoundingBox()
        print(f"           {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, volume {p.val().Volume()/1000:.1f} cm3")
        montagem.add(montada(obj), name=nome_peca, color=cq.Color(*CORES[nome_peca]))
    montagem.save(str(PASTA / "step" / "montagem.step"))
    sincronizar_scad(M, PASTA / "robo_garcom_carcaca.scad")
    print("[CARCACA] OpenSCAD atualizado com as mesmas medidas")
    if erros:
        sys.exit(f"[ERRO] {erros} peca(s) com problema. Confira as medidas.")
    print("[CARCACA] pronto: step\\ (Fusion 360) e stl\\ (impressora)")


if __name__ == "__main__":
    main()
