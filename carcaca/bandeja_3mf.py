"""Bandejas de impressao: varias pecas posicionadas na mesa da impressora.

Usado pelo gerar.py da carcaca e da maquete. Para cada bandeja grava:
  <nome>.3mf -> projeto para o fatiador (Cura, PrusaSlicer, Bambu Studio, Orca):
                cada peca separada, ja no lugar
  <nome>.stl -> a bandeja inteira num arquivo so (reserva, para fatiadores antigos)

As pecas chegam na posicao de impressao (z >= 0) e sao centralizadas em (x, y)
da mesa, cuja origem e o canto (0, 0).
"""
import zipfile
from xml.sax.saxutils import quoteattr

import cadquery as cq

MARGEM = 2.0   # distancia minima ate a borda da mesa
VAO = 3.0      # distancia minima entre pecas


def posicionar(forma, x, y, giro=0.0):
    s = forma.val() if isinstance(forma, cq.Workplane) else forma
    if giro:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), giro)
    # Limites medidos na propria malha: a caixa do OpenCASCADE e um pouco folgada
    # (deixaria a peca ~0,1 mm acima da mesa)
    vs = s.tessellate(0.05, 0.2)[0]
    x0, x1 = min(v.x for v in vs), max(v.x for v in vs)
    y0, y1 = min(v.y for v in vs), max(v.y for v in vs)
    z0 = min(v.z for v in vs)
    return s.translate(cq.Vector(x - (x0 + x1) / 2, y - (y0 + y1) / 2, -z0))


def conferir(pecas, mesa):
    """Lista de problemas: peca fora da mesa ou encostada em outra."""
    problemas = []
    for nome, s in pecas:
        bb = s.BoundingBox()
        if bb.xmin < MARGEM or bb.ymin < MARGEM or bb.xmax > mesa - MARGEM or bb.ymax > mesa - MARGEM:
            problemas.append(f"{nome} sai da mesa de {mesa:.0f} mm")
    for i, (n1, s1) in enumerate(pecas):
        for n2, s2 in pecas[i + 1:]:
            if s1.distance(s2) < VAO:
                problemas.append(f"{n1} encosta em {n2}")
    return problemas


def salvar(caminho, pecas, tolerancia=0.02):
    """Grava <caminho>.3mf (uma peca por objeto) e <caminho>.stl (tudo junto)."""
    objetos, itens = [], []
    for i, (nome, s) in enumerate(pecas, 1):
        verts, tris = s.tessellate(tolerancia, 0.1)
        # Tira triangulos de area zero (aparecem nos polos dos cantos esfericos)
        tris = [(a, b, c) for a, b, c in tris if (verts[b] - verts[a]).cross(verts[c] - verts[a]).Length > 1e-9]
        v = "".join(f'<vertex x="{p.x:.4f}" y="{p.y:.4f}" z="{p.z:.4f}"/>' for p in verts)
        t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
        objetos.append(f'<object id="{i}" name={quoteattr(nome)} type="model"><mesh>'
                       f'<vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>')
        itens.append(f'<item objectid="{i}"/>')
    modelo = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<model unit="millimeter" xml:lang="pt-BR" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
              f'<resources>{"".join(objetos)}</resources><build>{"".join(itens)}</build></model>')
    tipos = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(f"{caminho}.3mf", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", tipos)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", modelo)
    cq.exporters.export(cq.Workplane("XY").add(cq.Compound.makeCompound([s for _, s in pecas])),
                        f"{caminho}.stl", tolerance=tolerancia, angularTolerance=0.1)
    # STEP da bandeja: as mesmas pecas, solidas, no mesmo lugar (Fusion, Bambu Studio, Orca)
    bandeja_step(pecas).save(f"{caminho}.step")


COR_PECA = cq.Color(0.79, 0.44, 0.23)
COR_MESA = cq.Color(0.6, 0.6, 0.6)


def bandeja_step(pecas, nome="bandeja_de_impressao", com_mesa=None):
    """Montagem STEP com uma peca por componente. com_mesa = lado da mesa (so para conferir)."""
    a = cq.Assembly(name=nome)
    if com_mesa:
        a.add(cq.Workplane("XY").box(com_mesa, com_mesa, 1, centered=False).translate((0, 0, -1)),
              name="mesa_da_impressora_REFERENCIA_nao_imprimir", color=COR_MESA)
    for n, s in pecas:
        a.add(cq.Workplane("XY").add(s), name=n, color=COR_PECA)
    return a


def montar(pasta, bandejas, mesa):
    """bandejas: lista de (nome_do_arquivo, [(nome_da_peca, forma, x, y, giro), ...]) com x, y
    pensados para uma mesa de 220 mm; numa mesa maior as posicoes se espalham na proporcao."""
    pasta.mkdir(exist_ok=True)
    for velho in list(pasta.glob("*.3mf")) + list(pasta.glob("*.stl")) + list(pasta.glob("*.step")):
        velho.unlink()
    k = mesa / 220.0
    erros = 0
    feitas = []
    for nome, lista in bandejas:
        pecas = [(n, posicionar(f, x * k, y * k, g)) for n, f, x, y, g in lista]
        problemas = conferir(pecas, mesa)
        if problemas:
            erros += 1
            print(f"[ERRO] bandeja {nome}: " + "; ".join(problemas))
            continue
        salvar(str(pasta / nome), pecas)
        feitas.append((nome, pecas))
        print(f"          {nome}: {len(pecas)} peca(s)")
    # Todas as bandejas lado a lado, cada uma sobre uma mesa cinza: so para conferir no Fusion
    todas = cq.Assembly(name="todas_as_bandejas")
    passo = mesa + 60
    for i, (nome, pecas) in enumerate(feitas):
        pos = cq.Location(cq.Vector((i % 3) * passo, -(i // 3) * passo, 0))
        todas.add(bandeja_step(pecas, nome, com_mesa=mesa), name=nome, loc=pos)
    todas.save(str(pasta / "0_TODAS_AS_BANDEJAS_so_para_conferir.step"))
    return erros
