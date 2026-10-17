// =====================================================================
// Robo Garcom IoT · Carcaca "B · Torre de Servico"
// Modelo parametrico para OpenSCAD (2021.01 ou mais novo). Unidades: mm.
//
// COMO USAR (sem mexer em codigo):
//   1. Abra este arquivo no OpenSCAD.
//   2. Menu Janela (Window) -> desmarque "Ocultar Customizer" (Hide Customizer).
//   3. Mude os numeros no painel da direita.
//   4. Em "peca", escolha qual peca quer ver/exportar.
//   5. F6 (renderizar) e depois F7 (exportar STL).
//
// Medidas marcadas com (MEDIR) sao estimativas dos anuncios: confira
// nas pecas reais antes de imprimir. Imprima a CABECA primeiro, como teste.
// =====================================================================

/* [Peca para ver ou exportar] */
// "montagem" mostra o robo inteiro (nao e para imprimir)
peca = "montagem"; // [montagem, saia, coluna, bandeja, base_balanca, aranha, capo_botao, pe_antitombo, tampa_traseira, tampa_lateral, cabeca, cabeca_tampa]

/* [Chassi: base do kit 2WD, acrilico (MEDIR)] */
// Corpo estreito, de lado a lado (da foto: 10 cm). As rodas ficam do lado de fora
chassi_largura = 100;
// Leque de tras, de ponta a ponta (da foto: 15 cm)
chassi_largura_traseira = 150;
// Da frente ate o meio da traseira (da foto: 21,2 cm)
chassi_comprimento = 212;
// Quanto o meio da frente passa dos cantos (MEDIR)
frente_curva = 6;
// Onde o leque comeca, medido da borda de tras (MEDIR)
traseira_inicio = 33;
// Das pontas do leque ate a borda de tras (MEDIR)
traseira_ponta = 14;
// Furos da saia, em pares esquerda/direita (MEDIR; se nao coincidir, furar com 3 mm, devagar: acrilico racha)
furo_frente_x = 38;
furo_frente_y = 88;
furo_tras_x = 56;
furo_tras_y = -88;
// Furo para parafuso M3 rosqueado direto no plastico
furo_parafuso = 2.8;

/* [Rodas (MEDIR)] */
roda_diametro = 65;
roda_largura = 27;
// Centro da roda ate o meio do robo, de lado (MEDIR)
roda_pos_x = 65;
// Posicao do eixo das rodas: + = frente, - = tras (MEDIR)
roda_pos_y = -29;
// Altura do eixo em relacao ao topo do acrilico (negativo = abaixo) (MEDIR)
roda_eixo_z = -12;
// Espaco livre em volta da roda
roda_folga = 3;

/* [Saia (base)] */
saia_altura = 55;
// A saia fica esse tanto para dentro da borda da base (o pneu nao raspa)
saia_recuo = 2;
saia_raio_canto = 4;
// Espessura das paredes
parede = 2;
saia_teto = 2.5;
// Abertura atras (acesso ao regulador LM2596, display e trimpot)
abertura_traseira = true;
abertura_traseira_largura = 70;
abertura_traseira_altura = 45;
// Abertura lateral para tirar as pilhas (que ficam na frente)
abertura_lateral = true;
// -1 = lado esquerdo, 1 = lado direito
abertura_lateral_lado = -1;
abertura_lateral_pos_y = 56;
abertura_lateral_largura = 62;
abertura_lateral_altura = 45;
// Portinhas de encaixe nas duas aberturas
portinhas = true;
// Folga em volta da portinha (aumente se ficar dura)
portinha_folga = 0.25;
// Furo no teto em cima da chave liga/desliga
furo_chave = true;
// Posicao da chave: + = direita / frente (MEDIR)
chave_pos_x = 23;
chave_pos_y = 48;
chave_largura = 14;
chave_comprimento = 22;
// Nome gravado na frente (deixe vazio para nao gravar)
nome = "Bandejito 1.0";
nome_tamanho = 10;
// Posicao da coluna: + = frente, - = tras (fica atras do centro da bandeja)
coluna_pos_y = -50;

/* [Apoio antitombo] */
// Pezinho embaixo da traseira da base: segura o robo se ele empinar
antitombo = true;
// Distancia da ponta ate o chao com o robo parado
antitombo_folga = 6;
antitombo_pos_y = -95;
antitombo_largura = 60;
// Parafusos M3 de cima para baixo, pela base (MEDIR)
antitombo_furos_x = 22;

/* [Eletronica (so para conferir se cabe; nao imprime)] */
// Mostrar a eletronica na montagem (a saia fica transparente)
mostrar_eletronica = true;
// Suporte 2x18650 (estimado pela foto: 78 x 41 x 22 mm + tampa)
bateria_tam = [41, 78, 25];
// Posicao do centro do suporte (x = lado, y = frente/tras): na frente
bateria_pos = [0, 58];
// Regulador LM2596 com display (66 x 35 x 13 mm, do anuncio): atras
regulador_tam = [35, 66, 13];
regulador_pos = [-27, -55];
// Mini protoboard 170 furos (45 x 34 x 8,5 mm) + altura dos jumpers
protoboard_tam = [34, 45, 22];
protoboard_pos = [27, -5];
// Driver MX1508 (estimado)
driver_tam = [21, 24, 15];
driver_pos = [32, -62];

/* [Coluna] */
// Trecho de baixo (entra na saia; a base da balanca abraca ele)
coluna_d1 = 36;
coluna_h1 = 42;
// Trecho do meio
coluna_d2 = 32;
coluna_h2 = 45;
// Trecho de cima (entra na cabeca)
coluna_d3 = 28;
coluna_h3 = 38;
// Canal oco para os 6 fios
canal_fios = 18;
// Profundidade dos encaixes (saia/coluna e coluna/cabeca)
encaixe_prof = 12;
// Lado reto do encaixe (impede a peca de girar)
encaixe_corte = 2;

/* [Bandeja (uma so) e balanca] */
// A bandeja NAO encosta na coluna: fica solta em cima da "aranha", que fica em cima da balanca
bandeja_largura = 150;
bandeja_comprimento = 190;
bandeja_raio_canto = 16;
bandeja_pos_y = 0;
// Do teto da saia ate o fundo da bandeja (a balanca fica nesse vao)
bandeja_altura = 30;
bandeja_esp = 3;
// Altura da borda (segura o que estiver na bandeja)
bandeja_borda = 6;
// Folga do recorte em volta da coluna
bandeja_folga_coluna = 2.5;
// Celula de carga em barra de 500 g (MEDIR)
celula_comprimento = 80;
celula_lado = 12.7;
celula_furo_1 = 5;
celula_furo_2 = 15;
celula_parafuso = 4;
// Onde comeca a ponta presa (perto da coluna)
celula_pos_y = -28;
// Altura do pe embaixo da ponta presa
celula_base = 8;
// Quanto as pontas da aranha ficam para dentro dos cantos da bandeja
aranha_ponta = 17;
aranha_largura = 8;
// Botao verde no "nariz" da aranha
botao = true;
botao_furo = 12.3;
botao_avanco = 11.5;

/* [Cabeca e ESP32-CAM] */
cab_largura = 52;
cab_profundidade = 48;
cab_altura = 68;
// Quanto a camera olha para baixo (graus)
inclinacao = 10;
placa_largura = 27;
placa_altura = 40.5;
placa_esp = 1.6;
// Distancia da frente da placa ate a frente da lente (MEDIR)
lente_altura = 6;
// Posicao da lente: lado (0 = centro) e distancia da borda de cima da placa (MEDIR)
lente_x = 0;
lente_do_topo = 12;
lente_janela = 10;
// Angulo de visao da camera (graus); a janela abre em cone
campo_visao = 80;
// Altura do "olho" (lente) na cara da cabeca
olho_z = 46;
// Posicao do LED de flash: lado e distancia da borda de cima da placa (MEDIR)
flash_x = -10;
flash_do_topo = 33;
flash_janela_largura = 7;
flash_janela_altura = 11;
// Sorriso gravado na cara
boca = true;

/* [Impressao] */
// Folga de encaixe entre pecas (aumente se ficar apertado)
folga = 0.3;

/* [Hidden] */
$fn = 64;
W = chassi_largura;
L = chassi_comprimento;
H = saia_altura;
coluna_altura = coluna_h1 + coluna_h2 + coluna_h3;
fy = cab_profundidade / 2;             // eixo da coluna ate a cara (na base)
cab_r = 5;                             // arredondado da cabeca
cab_piso = 3;
cab_ressalto_d = coluna_d3 + 2*folga + 8;
tampa_encaixe = 4;

// ---------------------------------------------------------------------
// Utilitarios
// ---------------------------------------------------------------------
module rrect(x, y, h, r) {
    r2 = min(r, x/2 - 0.01, y/2 - 0.01);
    hull() for (sx = [-1, 1], sy = [-1, 1])
        translate([sx*(x/2 - r2), sy*(y/2 - r2), 0]) cylinder(r = r2, h = h);
}

module rcaixa(x0, x1, y0, y1, z0, z1, r) {
    hull() for (x = [x0 + r, x1 - r], y = [y0 + r, y1 - r], z = [z0 + r, z1 - r])
        translate([x, y, z]) sphere(r = r, $fn = 24);
}

// Cilindro com um lado reto (encaixe que nao gira)
module dforma(d, h, extra = 0) {
    intersection() {
        cylinder(d = d + 2*extra, h = h);
        translate([-d, -d, -1]) cube([2*d, d + d/2 - encaixe_corte + extra, h + 2]);
    }
}

module acima(z = 0) { translate([-200, -200, z]) cube([400, 400, 400]); }

// Contorno do chassi visto de cima: corpo estreito com a frente curva e
// traseira larga em leque (o mesmo do gerar.py). +y = frente.
// Arco simetrico que passa por (-a, y1), (0, y2) e (a, y1)
function arco_sim(a, y1, y2, esq_para_dir = true, n = 24) =
    let(c = (y2*y2 - y1*y1 - a*a) / (2*(y2 - y1)), r = abs(y2 - c), s = sign(y2 - c))
    [for (i = [0 : n]) let(x = esq_para_dir ? -a + 2*a*i/n : a - 2*a*i/n)
        [x, c + s*sqrt(max(0, r*r - x*x))]];

module contorno2d() {
    w = W/2; xt = chassi_largura_traseira/2;
    yb = -L/2 + traseira_inicio;
    offset(r = saia_raio_canto) offset(delta = -saia_raio_canto)
        polygon(concat(arco_sim(w, L/2 - frente_curva, L/2),
                       [[w, yb], [xt, yb - 6]],
                       arco_sim(xt, -L/2 + traseira_ponta, -L/2, false),
                       [[-xt, yb - 6], [-w, yb]]));
}

// Contorno extrudado; recuo > 0 encolhe para dentro
module prisma(h, recuo = 0) { linear_extrude(h) offset(delta = -recuo) contorno2d(); }

// ---------------------------------------------------------------------
// Saia (base): parafusada no chassi, cobre a eletronica
// ---------------------------------------------------------------------
// sy = +1: par da frente; sy = -1: par de tras
function furo(sx, sy) = sy > 0 ? [sx*furo_frente_x, furo_frente_y, 0] : [sx*furo_tras_x, furo_tras_y, 0];

module saia() {
    aba_h = 8;
    d = 30;   // alcance da rampa de cada aba, em diagonal para fora
    difference() {
        union() {
            difference() {
                prisma(H, saia_recuo);
                translate([0, 0, -1]) prisma(H - saia_teto + 1, saia_recuo + parede);
            }
            // Abas de fixacao (com rampa de 45 graus: imprime sem suporte)
            intersection() {
                prisma(H - saia_teto, saia_recuo + parede);
                for (sx = [-1, 1], sy = [-1, 1]) hull() {
                    translate(furo(sx, sy)) cylinder(r = 6, h = aba_h);
                    translate(furo(sx, sy) + [sx*d/sqrt(2), sy*d/sqrt(2), 0]) cylinder(r = 1, h = aba_h + d);
                }
            }
            // Encaixe da coluna (por dentro do teto)
            translate([0, coluna_pos_y, H - encaixe_prof - 3])
                cylinder(d = coluna_d1 + 2*folga + 8, h = encaixe_prof + 3);
        }
        // Furos dos parafusos
        for (sx = [-1, 1], sy = [-1, 1])
            translate(furo(sx, sy) + [0, 0, -1]) cylinder(d = furo_parafuso, h = aba_h + 1);
        // Encaixe da coluna + passagem dos fios
        translate([0, coluna_pos_y, H - encaixe_prof]) dforma(coluna_d1, encaixe_prof + 1, folga);
        translate([0, coluna_pos_y, H - encaixe_prof - 5]) cylinder(d = canal_fios, h = 10);
        // Rodas (ficam do lado de fora; so cortam a saia se encostarem nela)
        for (sx = [-1, 1])
            translate([sx*roda_pos_x, roda_pos_y, roda_eixo_z]) rotate([0, 90, 0])
                cylinder(d = roda_diametro + 2*roda_folga, h = roda_largura + 2*roda_folga, center = true);
        // Abertura traseira (baterias): atravessa a parede curva de tras
        if (abertura_traseira)
            translate([-abertura_traseira_largura/2, -L/2 - 1, -1])
                cube([abertura_traseira_largura, traseira_ponta + parede + 3, abertura_traseira_altura + 1]);
        // Fios da balanca e do botao
        translate([FURO_FIOS[0], FURO_FIOS[1], H - saia_teto - 1]) cylinder(d = 8, h = saia_teto + 2);
        // Chave liga/desliga
        if (furo_chave)
            translate([chave_pos_x, chave_pos_y, H - saia_teto - 1])
                rrect(chave_largura, chave_comprimento, saia_teto + 2, 2);
        // Abertura lateral (pilhas na frente)
        if (abertura_lateral)
            translate([abertura_lateral_lado*(W/2 - saia_recuo) - 2*parede,
                       abertura_lateral_pos_y - abertura_lateral_largura/2, -1])
                cube([4*parede, abertura_lateral_largura, abertura_lateral_altura + 1]);
        // Ventilacao nas laterais (so no lado sem a abertura lateral)
        for (sx = [-1, 1], i = [0 : 4])
            if (!(abertura_lateral && sx == abertura_lateral_lado))
                translate([sx*(W/2 - saia_recuo), 25 + i*13, H - 14])
                    cube([parede*4, 4, 14], center = true);
        // Nome na frente: a frente e curva, entao so a "casca" de 0,8 mm e gravada
        if (nome != "")
            intersection() {
                translate([0, L/2 + 1 - (frente_curva + 12), H*0.45]) rotate([90, 0, 180])
                    linear_extrude(frente_curva + 12)
                        text(nome, size = nome_tamanho, halign = "center", valign = "center",
                             font = "Liberation Sans:style=Bold");
                difference() { prisma(H, saia_recuo); translate([0, 0, -1]) prisma(H + 2, saia_recuo + 0.8); }
            }
    }
}

// ---------------------------------------------------------------------
// Coluna oca: tres trechos, cada um mais fino (as bandejas descem por cima)
// ---------------------------------------------------------------------
module coluna() {
    difference() {
        union() {
            // Todos os trechos com lado reto: a base da balanca e a cabeca nao giram
            dforma(coluna_d1, coluna_h1);
            translate([0, 0, coluna_h1]) dforma(coluna_d2, coluna_h2);
            translate([0, 0, coluna_h1 + coluna_h2]) dforma(coluna_d3, coluna_h3);
        }
        translate([0, 0, -1]) cylinder(d = canal_fios, h = coluna_altura + 2);
    }
}

// ---------------------------------------------------------------------
// Bandeja e balanca (o mesmo do gerar.py). Tudo na posicao montada:
// bandeja -> aranha -> celula de carga -> base da balanca -> coluna e saia
// ---------------------------------------------------------------------
ZB = H + bandeja_altura;
ZC = H + celula_base;
ZS = ZC + celula_lado;
CEL_Y0 = celula_pos_y;
CEL_Y1 = celula_pos_y + celula_comprimento;
HUB_Y = CEL_Y1 - (celula_furo_1 + celula_furo_2)/2;
FURO_COLUNA = coluna_d1 + 2*bandeja_folga_coluna;
BY = bandeja_pos_y + bandeja_comprimento/2 + botao_avanco;
NARIZ_R = 12;
PONTAS = [for (sy = [-1, 1], sx = [-1, 1]) [sx*(bandeja_largura/2 - aranha_ponta), bandeja_pos_y + sy*(bandeja_comprimento/2 - aranha_ponta)]];
FURO_FIOS = [celula_lado/2 + 8, CEL_Y0 + 12];
CAPO_Z0 = ZB - 3 - 24;

module forma_bandeja(recuo, h) difference() {
    translate([0, bandeja_pos_y, 0]) rrect(bandeja_largura - 2*recuo, bandeja_comprimento - 2*recuo, h, bandeja_raio_canto - recuo);
    d = FURO_COLUNA + 2*recuo;
    translate([0, coluna_pos_y, -1]) cylinder(d = d, h = h + 2);
    translate([-d/2, -L, -1]) cube([d, L + coluna_pos_y, h + 2]);
}
module bandeja() difference() {
    union() {
        forma_bandeja(0, bandeja_esp);
        difference() { forma_bandeja(0, bandeja_borda); translate([0, 0, -1]) forma_bandeja(2.4, bandeja_borda + 2); }
    }
    for (p = PONTAS) translate([p[0], p[1], -1]) cylinder(d = 4.4, h = bandeja_esp + 2);
}
module base_balanca() difference() {
    union() {
        translate([0, coluna_pos_y, H]) cylinder(d = coluna_d1 + 2*folga + 6, h = 20);
        translate([-8, coluna_pos_y, H]) cube([16, CEL_Y0 + 20 - coluna_pos_y, ZC - H]);
        translate([-3, CEL_Y0 + 19, H]) cube([6, CEL_Y1 - 2 - CEL_Y0 - 19, ZC - 3 - H]);   // batente
    }
    translate([0, coluna_pos_y, H - 1]) dforma(coluna_d1, 22, folga);
    for (y = [CEL_Y0 + celula_furo_1, CEL_Y0 + celula_furo_2]) {
        translate([0, y, H - 1]) cylinder(d = celula_parafuso + 0.4, h = celula_base + 2);
        translate([0, y, H - 1]) cylinder(d = 8, h = 4);
    }
    translate([0, HUB_Y, H - 1]) cylinder(d = 2.8, h = 10);   // parafuso-batente M3
}
module braco(x, y, larg, h) hull() {
    translate([0, HUB_Y, 0]) cylinder(d = larg, h = h);
    translate([x, y, 0]) cylinder(d = larg, h = h);
}
module aranha() {
    h = ZB - ZS;
    difference() {
        union() {
            translate([-12, HUB_Y - 12, ZS]) cube([24, 24, h]);
            translate([0, 0, ZS]) {
                for (p = PONTAS) braco(p[0], p[1], aranha_largura, h);
                braco(0, BY, 10, h);
                translate([0, BY, 0]) cylinder(r = NARIZ_R, h = h);
            }
            for (p = PONTAS) translate([p[0], p[1], ZB]) cylinder(d = 4, h = 2.5);
            if (botao) translate([0, BY, ZB]) difference() { cylinder(d = 21, h = 6); translate([0, 0, -1]) cylinder(d = 17, h = 8); }
        }
        translate([-celula_lado/2 - 1.5, CEL_Y0 - 1, ZS - 1]) cube([celula_lado + 3, HUB_Y - 12 - CEL_Y0 + 1, 2.5]);
        translate([0, BY, ZS - 1]) cylinder(d = 20, h = h - 2);
        if (botao) translate([0, BY, ZS]) cylinder(d = botao_furo, h = h + 2);
        translate([-2.5, HUB_Y + 11, ZS - 1]) cube([5, BY - 8 - HUB_Y - 11, 4.5]);   // canal dos fios
        for (y = [CEL_Y1 - celula_furo_1, CEL_Y1 - celula_furo_2]) {
            translate([0, y, ZS - 1]) cylinder(d = celula_parafuso + 0.4, h = h + 2);
            translate([0, y, ZB - 3.5]) cylinder(d = 8, h = 4);
        }
    }
}
module capo_botao() {
    alto = ZS - CAPO_Z0;
    difference() {
        translate([0, BY, CAPO_Z0]) cylinder(r1 = 8, r2 = NARIZ_R, h = alto);
        translate([0, BY, CAPO_Z0 + 1.6]) cylinder(r1 = 6.5, r2 = NARIZ_R - 1.6, h = alto);
    }
    difference() {
        union() {
            translate([0, BY, ZS - 0.01]) cylinder(d = 19.6, h = 4);
            translate([0, BY, ZS - 1.5]) cylinder(r = NARIZ_R, h = 1.5);
        }
        translate([0, BY, ZS - 3]) cylinder(d = 16, h = 8);
        translate([-3, BY - 11, ZS - 3]) cube([6, 4, 8]);
    }
}
// Celula de carga (comprada, NAO imprime)
module celula() difference() {
    translate([-celula_lado/2, CEL_Y0, ZC]) cube([celula_lado, celula_comprimento, celula_lado]);
    translate([-celula_lado, CEL_Y0 + celula_comprimento/2 - 10, ZC + 2.5]) cube([2*celula_lado, 20, celula_lado - 5]);
    for (y = [CEL_Y0 + celula_furo_1, CEL_Y0 + celula_furo_2, CEL_Y1 - celula_furo_1, CEL_Y1 - celula_furo_2])
        translate([0, y, ZC - 1]) cylinder(d = celula_parafuso, h = celula_lado + 2);
}

// ---------------------------------------------------------------------
// Cabeca: caixa reta; a ESP32-CAM fica atras da "cara", inclinada para baixo.
// Quadro da placa: origem = centro da frente da lente; y = direcao para onde a
// camera olha; z = para cima ao longo da placa.
// ---------------------------------------------------------------------
cab_tras = fy - cab_profundidade;          // plano de tras da cabeca

module quadro_placa() {
    translate([0, fy - parede - 1, olho_z]) rotate([-inclinacao, 0, 0]) children();
}
module antes_da_cara() { translate([-100, -100, -100]) cube([200, 100 + fy - parede + 0.01, 400]); }

module cab_externo() {
    rcaixa(-cab_largura/2, cab_largura/2, cab_tras, fy, 0, cab_altura, cab_r);
}
module cab_cavidade(f = 0) {
    rcaixa(-cab_largura/2 + parede + f, cab_largura/2 - parede - f,
           cab_tras - 10, fy - parede - f,
           cab_piso + f, cab_altura - parede - f, cab_r - parede - f);
}

module cabeca() {
    p_frente = -lente_altura;               // frente da placa (quadro da placa)
    p_tras = p_frente - placa_esp;
    p_topo = lente_do_topo;
    p_base = lente_do_topo - placa_altura;
    difference() {
        union() {
            difference() { cab_externo(); cab_cavidade(); }
            // Ressalto que recebe a coluna
            intersection() {
                cab_externo();
                cylinder(d = cab_ressalto_d, h = encaixe_prof + 3);
            }
            // Suporte da placa: apoios, guias laterais e batente (vao ate a cara)
            intersection() {
                antes_da_cara();
                quadro_placa() {
                    for (sx = [-1, 1], z = [p_base + 1.5, p_topo - 4.5])
                        translate([sx*(placa_largura/2 - 3) - 1.5, p_frente, z]) cube([3, 20, 3]);
                    for (sx = [-1, 1])
                        translate([sx > 0 ? placa_largura/2 + folga : -placa_largura/2 - folga - 2,
                                   p_tras - 1.5, p_base - folga - 2])
                            cube([2, 25, placa_altura + folga + 2]);
                    translate([-placa_largura/2 - folga - 2, p_tras - 1.5, p_base - folga - 2])
                        cube([placa_largura + 2*folga + 4, 25, 2]);
                }
            }
        }
        // Encaixe da coluna + passagem dos fios
        translate([0, 0, -0.01]) dforma(coluna_d3, encaixe_prof + 0.01, folga);
        cylinder(d = canal_fios, h = encaixe_prof + 10);
        quadro_placa() {
            // Janela da lente (em cone, para nao cortar o campo de visao)
            rotate([-90, 0, 0])
                cylinder(d1 = lente_janela, d2 = lente_janela + 2*20*tan(campo_visao/2), h = 20);
            // Janela do flash
            translate([flash_x - flash_janela_largura/2, -2, p_topo - flash_do_topo - flash_janela_altura/2])
                cube([flash_janela_largura, 20, flash_janela_altura]);
        }
        // Frestas de ventilacao no topo
        for (i = [-2 : 2])
            translate([i*7, cab_tras + cab_profundidade*0.4, cab_altura - parede/2])
                cube([3, cab_profundidade*0.45, parede + 2], center = true);
        // Sorriso
        if (boca)
            translate([0, fy + 0.01, olho_z - 16]) rotate([90, 0, 0]) linear_extrude(0.8)
                intersection() {
                    difference() { circle(r = 6.5); circle(r = 5.2); }
                    translate([-8, -8]) square([16, 6]);
                }
    }
}

// Tampa de tras: encaixa por pressao e empurra a placa contra os apoios
// ---------------------------------------------------------------------
// Apoio antitombo: aba parafusada embaixo da base + parede +
// ponta redonda que fica antitombo_folga acima do chao (desenhado montado)
// ---------------------------------------------------------------------
chao_z = roda_eixo_z - roda_diametro/2;
module pe_antitombo() {
    yc = antitombo_pos_y; w = antitombo_largura; r = 5;
    zc = chao_z + antitombo_folga + r;   // centro da ponta redonda
    difference() {
        union() {
            translate([-w/2, yc - 8, -7]) cube([w, 16, 4]);              // aba embaixo da base (3 mm)
            translate([-w/2, yc - 3, zc]) cube([w, 6, -7 - zc + 0.01]);  // parede
            translate([-w/2, yc, zc]) rotate([0, 90, 0]) cylinder(r = r, h = w);
        }
        for (sx = [-1, 1]) translate([sx*antitombo_furos_x, yc, -15]) cylinder(d = furo_parafuso, h = 12.01);
    }
}

// ---------------------------------------------------------------------
// Portinhas de encaixe: moldura por fora, placa de reforco por
// dentro, aba-gancho em cima (atras da parede), 2 ressaltos do "clique" e
// puxador embaixo. Desenhadas montadas; imprimem em pe.
// ---------------------------------------------------------------------
module casca(a, b, z0, z1)
    translate([0, 0, z0]) difference() {
        prisma(z1 - z0, saia_recuo + a);
        translate([0, 0, -1]) prisma(z1 - z0 + 2, saia_recuo + b);
    }
module caixa_uv(eixo, a0, a1, v0, v1, z0, z1) {
    if (eixo == "x") translate([a0, v0, z0]) cube([a1 - a0, v1 - v0, z1 - z0]);
    else translate([v0, a0, z0]) cube([v1 - v0, a1 - a0, z1 - z0]);
}
module tampa(eixo, u0, u1, v0, v1, altura, z_clique = 3) {
    f = portinha_folga; m = 4; fora = 1.5; dentro = 1.2; aba = 4; ressalto = 0.5;
    meio = (u0 + u1) / 2;
    intersection() { casca(-0.01, parede, 0, altura - f); caixa_uv(eixo, u0 + f, u1 - f, v0, v1, 0, altura - f); }   // tampao
    intersection() { casca(-fora, 0, 0, altura + m); caixa_uv(eixo, u0 - m, u1 + m, v0, v1, 0, altura + m); }       // moldura
    intersection() { casca(parede - 0.01, parede + f + dentro, 0, altura - f);                                     // reforco
                     caixa_uv(eixo, u0 + f, u1 - f, v0, v1, 0, altura - f); }
    intersection() { casca(parede + f, parede + f + dentro, altura - 8, altura + aba);                             // aba-gancho
                     caixa_uv(eixo, u0 + 8, u1 - 8, v0, v1, altura - 8, altura + aba); }
    for (a = [[u0 - ressalto, u0 + f + 3], [u1 - f - 3, u1 + ressalto]])                                           // clique
        intersection() { casca(parede + f, parede + f + dentro, z_clique, z_clique + 6);
                         caixa_uv(eixo, a[0], a[1], v0, v1, z_clique, z_clique + 6); }
    intersection() { casca(-fora - 3, -fora + 0.01, 0, 5); caixa_uv(eixo, meio - 10, meio + 10, v0, v1, 0, 5); }   // puxador
}
module tampa_traseira()
    tampa("x", -abertura_traseira_largura/2, abertura_traseira_largura/2,
          -L/2 - 6, -L/2 + traseira_ponta + parede + 8, abertura_traseira_altura);
module tampa_lateral() {
    xp = abertura_lateral_lado * (W/2 - saia_recuo);
    y0 = abertura_lateral_pos_y - abertura_lateral_largura/2;
    tampa("y", y0, y0 + abertura_lateral_largura, xp - 8, xp + 8, abertura_lateral_altura, 24);
}

module cabeca_tampa() {
    // Placa externa
    intersection() {
        rcaixa(-cab_largura/2, cab_largura/2, cab_tras - 10, fy, 0, cab_altura, cab_r);
        translate([-100, cab_tras - 2, -100]) cube([200, 2, 300]);
    }
    // Encaixe (fica dentro da abertura)
    intersection() {
        cab_cavidade(folga);
        translate([-100, cab_tras - 0.01, -100]) cube([200, tampa_encaixe, 300]);
    }
    // Pino que segura a placa (no meio, longe dos pinos laterais)
    intersection() {
        translate([-100, cab_tras - 1, -100]) cube([200, 100, 300]);
        quadro_placa()
            translate([-3, -lente_altura - placa_esp - 60, lente_do_topo - placa_altura/2 - 3])
                cube([6, 60, 6]);
    }
}

// ---------------------------------------------------------------------
// Posicoes na montagem
// ---------------------------------------------------------------------
coluna_z0 = H - encaixe_prof;
cabeca_z0 = coluna_z0 + coluna_altura - encaixe_prof;

module montagem() {
    // Chassi e rodas (so referencia, nao imprime)
    %translate([0, 0, -3]) prisma(3);
    %for (sx = [-1, 1])
        translate([sx*roda_pos_x, roda_pos_y, roda_eixo_z]) rotate([0, 90, 0])
            cylinder(d = roda_diametro, h = roda_largura, center = true);
    // Eletronica (so referencia)
    if (mostrar_eletronica) for (e = [[bateria_tam, bateria_pos, "#222222"], [regulador_tam, regulador_pos, "#1f4fa0"],
              [protoboard_tam, protoboard_pos, "#f4f4f4"], [driver_tam, driver_pos, "#b02020"]])
        color(e[2]) translate([e[1][0] - e[0][0]/2, e[1][1] - e[0][1]/2, 0]) cube(e[0]);
    color("#e8e2d0", mostrar_eletronica ? 0.35 : 1) saia();
    if (antitombo) color("#d9d2bd") pe_antitombo();
    if (portinhas && abertura_traseira) color("#e8e2d0") tampa_traseira();
    if (portinhas && abertura_lateral) color("#e8e2d0") tampa_lateral();
    color("#d9d2bd") base_balanca();
    color("#c9ccd1") celula();
    color("#d9d2bd") aranha();
    if (botao) color("#d9d2bd") capo_botao();
    color("#c96f3b") translate([0, 0, ZB]) bandeja();
    translate([0, coluna_pos_y, 0]) {
        color("#d9d2bd") translate([0, 0, coluna_z0]) coluna();
        translate([0, 0, cabeca_z0]) {
            color("#f2eee3") cabeca();
            color("#8a8577") cabeca_tampa();
        }
    }
}

// ---------------------------------------------------------------------
// Pecas na posicao de impressao
// ---------------------------------------------------------------------
if (peca == "montagem") montagem();
else if (peca == "saia") translate([0, 0, H]) rotate([180, 0, 0]) saia();    // teto na mesa
else if (peca == "coluna") coluna();
else if (peca == "bandeja") bandeja();
else if (peca == "base_balanca") translate([0, 0, -H]) base_balanca();
else if (peca == "aranha") translate([0, 0, -ZS]) aranha();
else if (peca == "capo_botao") translate([0, 0, -CAPO_Z0]) capo_botao();
else if (peca == "pe_antitombo")                                                           // em pe, perfil na mesa
    translate([0, -antitombo_pos_y, antitombo_largura/2]) rotate([0, 90, 0]) pe_antitombo();
else if (peca == "tampa_traseira") tampa_traseira();                                      // ja em pe (borda de baixo na mesa)
else if (peca == "tampa_lateral") tampa_lateral();
else if (peca == "cabeca") translate([0, 0, fy]) rotate([-90, 0, 0]) cabeca();           // cara na mesa
else if (peca == "cabeca_tampa")                                                           // tampa na mesa
    translate([0, 0, 2 - cab_tras]) rotate([90, 0, 0]) cabeca_tampa();
