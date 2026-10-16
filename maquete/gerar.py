"""Gera os moveis da maquete (salao em miniatura da Fase 5) a partir de medidas.txt.

Pecas (todas imprimiveis SEM suporte):
  tampo_mesa_N     -> de cabeca para baixo (o numero gravado fica na mesa da impressora)
  perna, pe        -> perna em pe, pe deitado (1 de cada por mesa)
  cadeira_assento  -> assento com as 4 pernas, de cabeca para baixo
  cadeira_encosto  -> deitado; encaixa em 2 furos no assento
  balcao_modulo    -> oco, sem fundo e sem a parede de tras, de cabeca para baixo
                      (imprima "balcao_modulos" iguais e coloque lado a lado)

Saidas:
  stl/<peca>.stl                 -> para o fatiador
  step/<peca>.step               -> para o Fusion 360
  step/maquete_completa.step     -> o salao inteiro montado (tapete, fita, moveis e o Bandejito)
Opcional: python gerar.py --stl PASTA -> uma STL por item da maquete montada + PASTA/cena.scad

Uso: ..\\carcaca\\.venv\\Scripts\\python.exe gerar.py   (ou dois cliques em GERAR.bat)
"""
import math
import sys
import time
from pathlib import Path

import cadquery as cq

PASTA = Path(__file__).resolve().parent
PLA = 1.24  # g/cm3


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


M = ler_medidas(PASTA / "medidas.txt")
globals().update(M)
if mesa_formato not in ("redonda", "quadrada"):
    sys.exit(f'[ERRO] medidas.txt: mesa_formato = "{mesa_formato}"; use "redonda" ou "quadrada"')


def cilindro(d, h, z=0.0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((0, 0, z))


def caixa(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


# ---------------------------------------------------------------------
# Mesa: tampo + perna + pe (encaixe por pressao)
# ---------------------------------------------------------------------
FURO = perna_d + 2 * folga          # furo dos encaixes
COLAR = FURO + 8                    # parede de 4 mm em volta do furo
PERNA_L = mesa_altura - tampo_esp - pe_esp


def tampo(n):
    """Na posicao de uso: face de cima em z = tampo_esp, colar do encaixe por baixo."""
    if mesa_formato == "redonda":
        t = cilindro(mesa_diametro, tampo_esp)
    else:
        t = (cq.Workplane("XY").rect(mesa_diametro, mesa_diametro).extrude(tampo_esp)
             .edges("|Z").fillet(tampo_raio_canto))
    t = t.faces(">Z").edges().chamfer(0.8)                       # borda de cima suave
    t = t.union(cilindro(COLAR, encaixe_prof, -encaixe_prof))    # colar por baixo
    t = t.cut(cilindro(FURO, encaixe_prof, -encaixe_prof))       # furo da perna (para no tampo)
    if numero_tamanho > 0:
        num = (cq.Workplane("XY").text(str(n), numero_tamanho, numero_prof + 1, font="Arial", kind="bold",
                                       halign="center", valign="center")
               .translate((0, 0, tampo_esp - numero_prof)))
        t = t.cut(num)
    return t


def perna():
    return cilindro(perna_d, PERNA_L).faces(">Z or <Z").edges().chamfer(0.8)   # pontas que entram facil


def pe():
    p = cilindro(pe_d, pe_esp).faces(">Z").edges().fillet(2)
    p = p.union(cilindro(COLAR, encaixe_prof, pe_esp))
    return p.cut(cilindro(FURO, encaixe_prof + 1, pe_esp))


def mesa_montada(n):
    return [("pe", pe(), "madeira_escura"),
            ("perna", perna().translate((0, 0, pe_esp)), "madeira_escura"),
            ("tampo", tampo(n).translate((0, 0, mesa_altura - tampo_esp)), "madeira")]


# ---------------------------------------------------------------------
# Cadeira: assento com 4 pernas + encosto que encaixa em 2 furos
# Posicao de uso: frente para -y, encosto em +y.
# ---------------------------------------------------------------------
CW, CH, CP = cadeira_largura, cadeira_assento_h, cadeira_perna
POSTE = CP - 2.5                    # poste do encosto (entra no furo da perna de tras)
FURO_POSTE = POSTE + 2 * folga
PROF_POSTE = 12
XP = CW / 2 - 3 - CP / 2            # centro das pernas
YP = CW / 2 - 3 - CP / 2


def cadeira_assento():
    a = (cq.Workplane("XY").rect(CW, CW).extrude(assento_esp).edges("|Z").fillet(4)
         .translate((0, 0, CH - assento_esp)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            a = a.union(caixa(sx * XP - CP / 2, sx * XP + CP / 2, sy * YP - CP / 2, sy * YP + CP / 2,
                              0, CH - assento_esp + 0.01))
    for sx in (-1, 1):   # furos dos postes do encosto (de cima do assento para dentro da perna de tras)
        a = a.cut(caixa(sx * XP - FURO_POSTE / 2, sx * XP + FURO_POSTE / 2, YP - FURO_POSTE / 2, YP + FURO_POSTE / 2,
                        CH - PROF_POSTE, CH + 1))
    return a


def cadeira_encosto():
    """Na posicao de uso. A placa fica rente a face de tras dos postes (imprime deitada)."""
    z0, z1 = CH - PROF_POSTE + 0.5, CH + encosto_h
    y_tras = YP + POSTE / 2
    e = None
    for sx in (-1, 1):
        p = caixa(sx * XP - POSTE / 2, sx * XP + POSTE / 2, YP - POSTE / 2, y_tras, z0, z1)
        e = p if e is None else e.union(p)
    zp = CH + encosto_h * 0.45
    e = e.union(caixa(-XP - POSTE / 2, XP + POSTE / 2, y_tras - encosto_esp, y_tras, zp, z1))
    if encosto_vao:
        hv, wv = (z1 - zp) * 0.45, 2 * XP - POSTE - 14
        zc = (zp + z1) / 2
        e = e.cut(caixa(-wv / 2, wv / 2, y_tras - encosto_esp - 1, y_tras + 1, zc - hv / 2, zc + hv / 2)
                  .edges("|Y").fillet(min(4, hv / 2 - 0.1)))
    return e


def cadeira_montada():
    return [("cadeira_assento", cadeira_assento(), "madeira_escura"),
            ("cadeira_encosto", cadeira_encosto(), "madeira")]


# ---------------------------------------------------------------------
# Balcao: casca fina e ripada, sem fundo e sem a parede de tras.
# Posicao de uso: x = profundidade (0 = fundo, frente em +x), y = comprimento.
# ---------------------------------------------------------------------
BD, BL, BH, BP = balcao_profundidade, balcao_comprimento, balcao_altura, balcao_parede
BZT = BH - balcao_tampo_esp          # onde o tampo comeca


def ripas(parede):
    """Frestas verticais que atravessam uma parede: 'frente', 'esquerda' ou 'direita'."""
    if ripa_vao <= 0:
        return []
    comprimento = BL if parede == "frente" else BD
    passo = ripa_largura + ripa_vao
    n = int((comprimento - 16 - ripa_vao) // passo) + 1
    inicio = (comprimento - (n * ripa_vao + (n - 1) * ripa_largura)) / 2
    cortes = []
    for i in range(n):
        a = inicio + i * passo
        if parede == "frente":
            cortes.append(caixa(BD - BP - 1, BD + 1, a, a + ripa_vao, 16, BZT - 16))
        elif parede == "esquerda":
            cortes.append(caixa(a, a + ripa_vao, -1, BP + 1, 16, BZT - 16))
        else:
            cortes.append(caixa(a, a + ripa_vao, BL - BP - 1, BL + 1, 16, BZT - 16))
    return cortes


def balcao_modulo():
    a = balcao_aba
    b = caixa(0, BD + a, -a, BL + a, BZT, BH)                                  # tampo com aba
    b = b.union(caixa(BD - BP, BD, 0, BL, 0, BZT + 0.01))                      # frente
    b = b.union(caixa(0, BD, 0, BP, 0, BZT + 0.01))                            # lateral
    b = b.union(caixa(0, BD, BL - BP, BL, 0, BZT + 0.01))                      # lateral
    b = b.union(caixa(0, BP, 0, BL, BZT - 15, BZT + 0.01))                     # travessa de tras (firmeza)
    for c in ripas("frente") + ripas("esquerda") + ripas("direita"):
        b = b.cut(c)
    return b


# ---------------------------------------------------------------------
# Pecas para imprimir
# ---------------------------------------------------------------------
def virar(obj, altura):
    """De cabeca para baixo: o que estava em z = altura vai para a mesa da impressora."""
    return obj.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, altura))


def deitar_encosto(obj):
    y_tras = YP + POSTE / 2
    return obj.rotate((0, 0, 0), (1, 0, 0), -90).translate((0, 0, y_tras))


def pecas():
    n_mesas = int(mesas)
    p = {f"tampo_mesa_{n}": (virar(tampo(n), tampo_esp), 1) for n in range(1, n_mesas + 1)}
    p["perna"] = (perna(), n_mesas)
    p["pe"] = (pe(), n_mesas)
    n_cad = int(cadeiras_por_mesa) * n_mesas
    if n_cad:
        p["cadeira_assento"] = (virar(cadeira_assento(), CH), n_cad)
        p["cadeira_encosto"] = (deitar_encosto(cadeira_encosto()), n_cad)
    p["balcao_modulo"] = (virar(balcao_modulo(), BH), int(balcao_modulos))
    return p


# ---------------------------------------------------------------------
# Maquete completa (mesmas medidas do simulador e do GUIA, Fase 5)
# Coordenadas em mm: x ao longo da fita (balcao em x = 0), y = 0 na borda de baixo.
# ---------------------------------------------------------------------
TAPETE = (2000, 1500)
LY = 700                                    # linha da fita
MESAS_POS = [(700, 980), (1150, 420), (1600, 980)]   # mesas 1, 2 e 3 (a 28 cm da linha)
FITA = [(200, 1840, LY - 9.5, LY + 9.5), (200, 240, LY - 40, LY + 40), (1800, 1840, LY - 40, LY + 40)] + \
       [(x - 9.5, x + 9.5, LY - 40, LY + 40) for x in (780, 1230, 1680)] + \
       [(x - 9.5, x + 9.5, LY + 50, LY + 170) for x in (645, 1545)] + \
       [(1095 - 9.5, 1095 + 9.5, LY - 170, LY - 50)]
# Ramais (as 3 ultimas tiras): tracos de 12 cm do lado da mesa, de 5 a 17 cm da linha,
# 13,5 cm ANTES da marca (onde fica o eixo das rodas quando a barra de sensores esta
# na marca). O robo gira no lugar ate o sensor do meio achar o ramal: fica de frente
# para a mesa. Mesmo desenho do simulador (RAMAL_INI/RAMAL_FIM em server.js).
POSE_ROBO = (375, LY)                       # eixo das rodas do robo no balcao (virado para +x)

CORES = {"madeira": (0.66, 0.48, 0.31), "madeira_escura": (0.50, 0.33, 0.18), "balcao": (0.62, 0.40, 0.20),
         "tapete": (0.93, 0.92, 0.87), "fita": (0.10, 0.10, 0.11)}


def itens_maquete():
    """Lista (nome, forma ja posicionada, cor)."""
    itens = [("tapete", caixa(0, TAPETE[0], 0, TAPETE[1], -3, 0), "tapete")]
    fita = None
    for x0, x1, y0, y1 in FITA:
        f = caixa(x0, x1, y0, y1, 0, 0.6)
        fita = f if fita is None else fita.union(f)
    itens.append(("fita", fita, "fita"))
    for i in range(int(balcao_modulos)):     # modulos lado a lado, centrados na linha
        y0 = LY - balcao_modulos * BL / 2 + i * BL
        itens.append((f"balcao_{i + 1}", balcao_modulo().translate((0, y0, 0)), "balcao"))
    r_cad = (mesa_diametro / 2 if mesa_formato == "redonda" else mesa_diametro / 2) + CW / 2 + 12
    for n, (x, y) in enumerate(MESAS_POS[:int(mesas)], 1):
        for nome, forma, cor in mesa_montada(n):
            itens.append((f"mesa_{n}_{nome}", forma.translate((x, y, 0)), cor))
        longe = 1 if y > LY else -1          # cadeiras do lado oposto a fita
        k = int(cadeiras_por_mesa)
        angulos = [0] if k == 1 else [(-40 + 80 * j / (k - 1)) for j in range(k)]
        for j, ang in enumerate(angulos):
            dx, dy = math.sin(math.radians(ang)), longe * math.cos(math.radians(ang))
            giro = math.degrees(math.atan2(-dx, dy))   # encosto (+y da cadeira) para fora da mesa
            for nome, forma, cor in cadeira_montada():
                f = forma.rotate((0, 0, 0), (0, 0, 1), giro).translate((x + dx * r_cad, y + dy * r_cad, 0))
                itens.append((f"mesa_{n}_cadeira_{j + 1}_{nome.split('_')[1]}", f, cor))
    return itens


def bandejito():
    """O prototipo completo do robo (carcaca/prototipo.py), parado no balcao virado para as mesas."""
    sys.path.insert(0, str(PASTA.parent / "carcaca"))
    import prototipo                         # usa o gerar.py e o medidas.txt da carcaca
    grupos = prototipo.montar()
    loc = cq.Location(cq.Vector(POSE_ROBO[0] - prototipo.g.roda_pos_y, POSE_ROBO[1],
                                prototipo.g.roda_diametro / 2 - prototipo.g.roda_eixo_z), cq.Vector(0, 0, 1), -90)
    return grupos, prototipo.CORES, prototipo.como_shape, loc


sys.path.insert(0, str(PASTA.parent / "carcaca"))
import bandeja_3mf   # noqa: E402  (bandejas de impressao, compartilhado com a carcaca)


def bandejas():
    """Pecas arrumadas nas bandejas (posicoes para uma mesa de 220 mm)."""
    p = {nome: obj for nome, (obj, _) in pecas().items()}
    padrao = (int(mesas), int(cadeiras_por_mesa), int(balcao_modulos)) == (3, 2, 2)
    if not padrao:
        # Quantidades diferentes do padrao: uma peca por bandeja (sempre cabe)
        lista, n = [], 1
        for nome, (obj, qtd) in pecas().items():
            for k in range(1, qtd + 1):
                lista.append((f"{n:02d}_{nome}_{k}", [(nome, obj, 110, 110, 0)]))
                n += 1
        return lista
    t, pe_, pn = p["pe"], p["pe"], p["perna"]
    a, e, b = p["cadeira_assento"], p["cadeira_encosto"], p["balcao_modulo"]
    return [
        ("1_tampo_mesa_1", [("tampo_mesa_1", p["tampo_mesa_1"], 110, 110, 0)]),
        ("2_tampo_mesa_2", [("tampo_mesa_2", p["tampo_mesa_2"], 110, 110, 0)]),
        ("3_tampo_mesa_3", [("tampo_mesa_3", p["tampo_mesa_3"], 110, 110, 0)]),
        ("4_2_pes_e_3_pernas", [("pe_1", pe_, 58, 58, 0), ("pe_2", pe_, 162, 162, 0),
                                ("perna_1", pn, 160, 30, 0), ("perna_2", pn, 195, 30, 0), ("perna_3", pn, 30, 190, 0)]),
        ("5_1_pe_e_3_assentos", [("pe_3", t, 58, 58, 0), ("assento_1", a, 160, 60, 0),
                                 ("assento_2", a, 60, 160, 0), ("assento_3", a, 160, 160, 0)]),
        ("6_3_assentos_e_1_encosto", [("assento_4", a, 50, 50, 0), ("assento_5", a, 140, 50, 0),
                                      ("assento_6", a, 50, 140, 0), ("encosto_1", e, 150, 155, 0)]),
        ("7_4_encostos", [("encosto_2", e, 45, 57, 0), ("encosto_3", e, 125, 57, 0),
                          ("encosto_4", e, 45, 165, 0), ("encosto_5", e, 125, 165, 0)]),
        ("8_1_encosto", [("encosto_6", e, 110, 110, 0)]),
        ("9_balcao_2_modulos", [("balcao_1", b, 55, 110, 0), ("balcao_2", b, 160, 110, 0)]),
    ]


def main():
    t0 = time.time()
    (PASTA / "stl").mkdir(exist_ok=True)
    (PASTA / "step").mkdir(exist_ok=True)
    print(f"[MAQUETE] {len(M)} medidas lidas de medidas.txt")
    # Quanto da peca macica a impressora gasta de verdade (3 paredes, 15% de preenchimento):
    # pecas grossas ficam quase ocas; pecas finas (cadeira, balcao) saem praticamente macicas
    FATOR = {"tampo": 0.45, "perna": 0.32, "pe": 0.35, "cadeira_assento": 0.75, "cadeira_encosto": 1.0,
             "balcao_modulo": 1.0}
    grupos_g = {"mesas": 0.0, "cadeiras": 0.0, "balcao": 0.0}
    erros = 0
    for nome, (obj, qtd) in pecas().items():
        solidos = obj.solids().vals()
        if len(solidos) != 1 or not solidos[0].isValid():
            erros += 1
            print(f"[ERRO] {nome}: {len(solidos)} solido(s)")
        cq.exporters.export(obj, str(PASTA / "stl" / f"{nome}.stl"), tolerance=0.02, angularTolerance=0.1)
        cq.exporters.export(obj, str(PASTA / "step" / f"{nome}.step"))
        bb = obj.val().BoundingBox()
        fator = next(f for k, f in FATOR.items() if nome.startswith(k))
        g = obj.val().Volume() / 1000 * PLA * fator * qtd
        grupos_g["cadeiras" if nome.startswith("cadeira") else "balcao" if nome.startswith("balcao") else "mesas"] += g
        print(f"          {nome}: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm, imprimir {qtd}x (~{g:.0f} g)")
    print("[MAQUETE] PLA estimado: " + " | ".join(f"{k} ~{v:.0f} g" for k, v in grupos_g.items())
          + f" | total ~{sum(grupos_g.values()):.0f} g (o fatiador da o valor exato)")

    print(f"[MAQUETE] bandejas de impressao (mesa de {mesa_impressora:.0f} mm) em impressao\\:")
    erros += bandeja_3mf.montar(PASTA / "impressao", bandejas(), mesa_impressora)

    print("[MAQUETE] montando o salao completo (inclui o Bandejito)...", flush=True)
    raiz = cq.Assembly(name="maquete_completa")
    itens = itens_maquete()
    moveis = cq.Assembly(name="1_salao")
    for nome, forma, cor in itens:
        moveis.add(forma, name=nome, color=cq.Color(*CORES[cor]))
    raiz.add(moveis, name="1_salao")
    grupos, cores_robo, como_shape, loc = bandejito()
    robo = cq.Assembly(name="2_bandejito")
    for nome_grupo, lista in grupos.items():
        sub = cq.Assembly(name=nome_grupo)
        for nome, forma, cor in lista:
            sub.add(como_shape(forma), name=nome, color=cq.Color(*cores_robo[cor]))
        robo.add(sub, name=nome_grupo)
    raiz.add(robo, name="2_bandejito", loc=loc)
    raiz.save(str(PASTA / "step" / "maquete_completa.step"))
    print(f"[MAQUETE] step\\maquete_completa.step ({len(itens)} itens + o robo)")

    if "--stl" in sys.argv:
        pasta = Path(sys.argv[sys.argv.index("--stl") + 1])
        pasta.mkdir(parents=True, exist_ok=True)
        linhas = []
        for nome, forma, cor in itens:
            arq = pasta / f"{nome}.stl"
            cq.exporters.export(forma, str(arq), tolerance=0.1, angularTolerance=0.2)
            r, gg, b = CORES[cor]
            linhas.append(f'color([{r},{gg},{b}]) import("{arq.as_posix()}");')
        (pasta / "cena.scad").write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print(f"[MAQUETE] STLs + cena.scad em {pasta}")

    if erros:
        sys.exit(f"[ERRO] {erros} peca(s) com problema. Confira as medidas.")
    print(f"[MAQUETE] pronto em {time.time() - t0:.0f} s: impressao\\ (bandejas prontas), stl\\ (pecas avulsas)"
          f" e step\\ (Fusion 360)")


if __name__ == "__main__":
    main()
