# Carcaça 3D: conceito B · Torre de Serviço

Modelo **paramétrico**: todas as medidas ficam no `medidas.txt`; o `GERAR.bat` gera as peças para o Fusion 360 (STEP), para a impressora (STL e bandejas `.3mf`) e o modelo do OpenSCAD.

![Robô completo](imagens/prototipo_completo.png)

> **Esta é a versão oficial** (desde 2026-10-16): coluna recuada, pilhas na frente, pé antitombo e portinhas de encaixe. A **primeira versão** (coluna no centro, pilhas atrás) não está mais nesta pasta, mas continua guardada no Git, na marca `bandejito-1.0-original` (para ver: `git checkout bandejito-1.0-original -- carcaca` numa cópia do projeto).

## O que mudou em relação à primeira versão

Objetivo: **mais espaço livre na frente das bandejas**. A coluna (a "viga" central) sai do meio e vai para trás.

| | Primeira versão (marca `bandejito-1.0-original`) | **Versão atual** |
|---|---|---|
| Posição da coluna (`coluna_pos_y`) | 0 (centro) | **−50 mm** (21 mm atrás do eixo das rodas) |
| Bandejas (tamanho e lugar) | 136 × 190 e 104 × 146, no centro | **iguais**; só o furo da coluna vai para trás (`bandeja_pos_y = 0`) |
| Área livre na frente, bandeja de baixo | 92 cm² | **158 cm² (+71%)** |
| Área livre na frente, bandeja de cima | 50 cm² | **99 cm² (o dobro)** |
| Sustentação da frente das bandejas | só o colar | colar + **2 espinhas de apoio** (peças novas) |
| Coluna | trecho de baixo redondo | trecho de baixo com **lado reto** (a espinha de baixo não gira) |
| **Pilhas** (suporte 2×18650, a peça mais pesada) | atrás, em y = −50 | **na frente, em y = +58** (centro de massa volta para perto do original) |
| Regulador LM2596 / protoboard / driver | frente / frente / atrás | **atrás à esquerda / meio à direita / atrás à direita** |
| Furos dos fios dos motores na base | x = ±8 | **x = ±30** (os de ±8 ficariam embaixo das pilhas) · MEDIR |
| Como tirar as pilhas | abertura de trás | **abertura lateral** no lado esquerdo (62 × 45 mm, embaixo da bandeja; sem ventilação desse lado) |
| Abertura de trás | pilhas | acesso ao **regulador** (display e trimpot do 5,0 V) |
| Furo da chave liga/desliga (`chave_pos_x`, `chave_pos_y`) | (23, −60) | **(23, 48)**, em cima da chave do suporte das pilhas · MEDIR |
| **Pé antitombo** (`pe_antitombo`, peça nova) | — | embaixo da traseira da base, 6 mm acima do chão, 2 parafusos M3 |
| **Portinhas de encaixe** (`tampa_traseira`, `tampa_lateral`, peças novas) | aberturas sempre abertas | fecham a abertura de trás e a lateral, sem parafuso (aba-gancho em cima + "clique" embaixo) |
| Inclinação da câmera (`inclinacao`) | 15° | **10°** (a borda da bandeja de cima não aparece no vídeo) |
| Bandeja de impressão 1 | cabeça + tampa | cabeça + tampa **+ espinha de baixo + as 2 portinhas** (em pé) |
| Bandeja de impressão 3 | `3_bandeja_baixo_e_coluna` | `3_bandeja_baixo_coluna_e_pe` (**+ pé antitombo**) |
| Bandeja de impressão 4 | `4_bandeja_cima` | `4_bandeja_cima_e_apoio` (**+ espinha de cima**) |
| PLA a mais | — | ~105 g (as duas espinhas + o pé + as duas portinhas) |
| Firmware | arranca com a força toda | **partida suave** (`MOTOR_RAMP_MS = 500` no `src/config.h`), vale para as duas versões |
| Chassi, rodas, motores, cabeça, cores, nome na frente | — | **iguais** |

Mais comparações: [de frente](imagens/v2_2_comparacao_de_frente.png) · [perfil](imagens/v2_3_comparacao_perfil.png) · [área livre de cima](imagens/v2_4_area_livre_de_cima.png) · [eletrônica: pilhas na frente](imagens/v2_5_eletronica_pilhas_na_frente.png) · [abertura lateral e pé](imagens/v2_6_abertura_lateral_e_pe.png) · [portinhas](imagens/v2_7_portinhas.png) · [como a portinha trava](imagens/v2_8_portinha_como_encaixa.png).

> O `manual_montagem_fisica.md` (na raiz do projeto) descreve esta versão (Etapa 8.6: onde fica cada peça).

### As espinhas de apoio

Com a coluna atrás, a frente da bandeja fica longe do apoio. Cada bandeja ganha uma **espinha**: um anel com lado reto que entra na coluna, mais uma aleta de 4 mm ao longo do meio da bandeja, da traseira até 1 cm antes da borda da frente.

- **`apoio_baixo`**: o anel fica apoiado no **teto da saia** (30 mm de altura, num espaço que já era vazio). A aleta tem 30 mm junto da coluna e afina até 6 mm nas pontas.
- **`apoio_cima`**: o anel fica apoiado no **colar da bandeja de baixo**. A aleta é rasa (12 mm junto da coluna e 4 mm nas pontas) para não roubar altura da bandeja de baixo: sobram 30 a 38 mm de vão embaixo dela.
- As duas imprimem **de cabeça para baixo** (a borda que encosta na bandeja fica na mesa), **sem suporte**.

### Conferências feitas (2026-10-16)

| Conferência | Resultado |
|---|---|
| Peças válidas | todas são 1 sólido válido |
| Colisões na montagem | nenhuma peça da carcaça encosta onde não deve; espinhas encostam na saia/colar e nas bandejas (0,0 mm) e têm folga de 0,3 mm na coluna |
| Resistência (copo de 250 g na ponta da bandeja) | espinha de baixo: tensão 0,5 MPa (o PLA aguenta ~50, ou seja, ~100× de sobra), flecha ~0,6 mm · espinha de cima: 2,6 MPa (~19×), flecha ~2 mm |
| Câmera (lente padrão de ~66°) | borda da bandeja de cima a 33° abaixo do horizonte; a imagem vai até ~30,5° → **fora do vídeo** |
| Bandejas de impressão (`.3mf`) | 11 peças com malha fechada, volume positivo, dentro da mesa de 220 mm e em z = 0 |
| Eletrônica nova (pilhas na frente) | nada encosta na saia, na coluna, nas abas dos parafusos nem no pé; só as 2 sobreposições ilustrativas que já existiam na primeira versão (pilha dentro do suporte, motor encostado na base) |
| Pé antitombo | encosta embaixo da base; 34 mm da roda e 47 mm dos motores; encosta no chão com 5,2° de inclinação |
| Portinhas | encostam na saia sem invadir a parede; puxadas 1 mm para fora, batem na parede (travam); nada mais encosta nelas (eletrônica, pé, abas dos parafusos) |
| OpenSCAD | atualizado com a mesma geometria (coluna, bandejas, espinhas, abertura lateral, pé, portinhas e eletrônica) |

### As portinhas de encaixe

![Portinhas abertas e fechadas](imagens/v2_7_portinhas.png)

- **Por fora:** só uma moldura fina (1,5 mm) em volta da abertura e um puxador embaixo. A de trás acompanha a curva da traseira.
- **Por dentro:** uma placa de reforço, uma **aba-gancho** em cima (fica atrás da parede) e **2 ressaltos** de 0,5 mm nas laterais (o "clique"). Na portinha lateral, os ressaltos ficam no meio da altura, porque embaixo, na frente, fica a aba de um parafuso da saia.
- **Fechar:** incline a portinha, encaixe a aba de cima atrás da parede e empurre a parte de baixo até o clique. **Abrir:** puxe o puxador para fora e solte a aba.
- **Ajuste:** se ficar dura, aumente `portinha_folga` (0,25) no `medidas.txt`; se ficar solta, diminua. Para não usar, `portinhas = false`.
- Imprimem **em pé** (a borda de baixo na mesa), sem suporte, ~20 g cada. Vale testar a lateral junto com a saia.

![Como a portinha trava](imagens/v2_8_portinha_como_encaixa.png)

### Estabilidade

O robô se apoia nas rodas (atrás) e na roda boba (na frente). Ele só fica de pé se o **centro de massa** estiver **à frente do eixo das rodas**. Estimativa:

| Situação | Centro de massa à frente do eixo | Empina para trás com... |
|---|---|---|
| Primeira versão, vazio | 23 mm | rampa de ~14° ou arrancada de ~2,4 m/s² |
| Coluna recuada com as pilhas ainda atrás, vazio | 12,5 mm | rampa de ~7° ou arrancada de ~1,3 m/s² |
| **Versão atual (pilhas na frente), vazio** | **21 mm** | rampa de ~12° ou arrancada de ~2,2 m/s² |
| Versão atual, copo de 150 g **na frente** da bandeja de cima | 31 mm | rampa de ~16° ou arrancada de ~2,8 m/s² |
| Versão atual, copo de 150 g **atrás da coluna** (pior caso) | 10 mm | rampa de ~6° ou arrancada de ~1,0 m/s² |

**Três proteções juntas:**
1. **Pilhas na frente**: o centro de massa fica quase igual ao da primeira versão.
2. **Partida suave** no firmware: a roda já parte na força mínima e sobe até a máxima em 0,5 s, em vez de dar o tranco. Parar e frear continuam imediatos.
3. **Pé antitombo**: se mesmo assim ele empinar, o pé encosta no chão a 5,2°, antes do ponto de tombar, e o robô volta para a roda boba.

Mesmo assim, coloque os pedidos de preferência **na frente da coluna**.

## Arquivos

| Arquivo | O que é |
|---|---|
| **`medidas.txt`** | **O painel de números.** Todas as medidas ficam aqui |
| **`GERAR.bat`** | Dois cliques: lê `medidas.txt` e gera tudo de novo (~10 s) |
| `step/*.step` | As 6 peças + `montagem.step` (robô inteiro) para o **Fusion 360** |
| `stl/*.stl` | As 6 peças avulsas para o fatiador (Cura, Bambu Studio, PrusaSlicer) |
| `impressao/` | **Bandejas prontas**: as peças já arrumadas na mesa da impressora (`.3mf` + `.stl`) |
| `bandeja_3mf.py` | Arruma as peças nas bandejas e grava os `.3mf` (usado também pela maquete) |
| `robo_garcom_carcaca.scad` | O mesmo modelo no OpenSCAD (o `GERAR.bat` copia as medidas para ele) |
| `gerar.py` | O programa que desenha as peças (CadQuery, Python) |
| `prototipo.py` | Monta o **protótipo demonstrativo** (robô completo, com eletrônica e fios) em `step/prototipo_completo.step` |
| `imagens/` | Montagem, perfil, eletrônica por dentro, cabeça em corte, saia por baixo |

## Como mudar uma medida (jeito principal)

1. Abra `medidas.txt` no Bloco de Notas (dois cliques).
2. Mude o número depois do `=`. Pode usar vírgula ou ponto: `40,5` ou `40.5`.
3. Salve (**Ctrl+S**).
4. Dê dois cliques em **`GERAR.bat`**. Uma janela preta mostra cada peça sendo gerada e termina com `pronto`.
5. Os arquivos novos estão em `step\` (Fusion) e `stl\` (impressora).

> Se aparecer `[ERRO]`, a mensagem diz a linha de `medidas.txt` com problema (ex.: faltou o `=` ou tem letra no lugar do número).

## Abrir no Fusion 360

1. No Fusion: **Arquivo → Abrir → Abrir do meu computador** (*Open from my computer*).
2. Escolha `step\montagem.step` (robô inteiro) ou uma peça, por exemplo `step\cabeca.step`.
3. As peças chegam como **sólidos de verdade** (faces, furos e curvas editáveis). Dá para medir, cortar e empurrar/puxar faces.
4. O STEP não guarda a lista de medidas. Para mudar um número, use o `medidas.txt` + `GERAR.bat` e abra o STEP novo.

> As peças avulsas (`saia.step`, `cabeca.step`...) vêm na **posição de impressão**. O `montagem.step` vem com tudo no lugar.

> ⚠️ Mudanças feitas **dentro** do Fusion não voltam para o `medidas.txt`. Se gerar de novo, elas são substituídas.

## As 11 peças

| Peça | Tamanho (mm) | Como imprimir |
|---|---|---|
| `apoio_baixo.stl` | 43 × 166 × 30 | De cabeça para baixo (borda reta na mesa), sem suporte |
| `apoio_cima.stl` | 39 × 132 × 34 | De cabeça para baixo (borda reta na mesa), sem suporte |
| `pe_antitombo.stl` | 36 × 16 × 60 | Em pé (o perfil na mesa), sem suporte |
| `tampa_traseira.stl` | 78 × 11 × 49 | Em pé (a borda de baixo na mesa), sem suporte |
| `tampa_lateral.stl` | 8 × 70 × 49 | Em pé (a borda de baixo na mesa), sem suporte |
| `cabeca.stl` | 52 × 68 × 48 | **Imprima primeiro (teste).** Cara virada para a mesa |
| `cabeca_tampa.stl` | 52 × 68 × 38 | Tampa deitada na mesa |
| `coluna.stl` | Ø36 × 125 | Em pé |
| `bandeja_baixo.stl` | 136 × 190 × 11 | Deitada. Cabe numa mesa de 220 × 220 mm |
| `bandeja_cima.stl` | 104 × 146 × 11 | Deitada |
| `saia.stl` | 150 × 212 × 55 | De cabeça para baixo (teto na mesa). Precisa de uma mesa de pelo menos 220 × 220 mm |

Altura total montada: cerca de **224 mm**.
Configuração sugerida: PLA, camada de 0,2 mm, 3 paredes, preenchimento de 15%, **sem suportes**.

## Bandejas prontas para imprimir (pasta `impressao\`)

Cada arquivo é **uma impressão**, com as peças já arrumadas numa mesa de **22 × 22 cm**, na ordem combinada:

![Bandejas de impressão](impressao/bandejas.png)

| Arquivo | O que imprime |
|---|---|
| `1_cabeca_e_tampa_TESTE` | Cabeça + tampa (**imprima primeiro**, como teste, depois de medir a placa) + espinha de baixo + as 2 portinhas |
| `2_saia` | A saia (depois de medir a base do kit) |
| `3_bandeja_baixo_coluna_e_pe` | Bandeja de baixo + coluna + pé antitombo |
| `4_bandeja_cima_e_apoio` | Bandeja de cima + espinha de cima |

- Abra o **`.3mf`** no fatiador: as peças chegam separadas e no lugar. O **`.stl`** de mesmo nome é a bandeja inteira num arquivo só (reserva).
- O **`.step`** de mesmo nome tem as mesmas peças sólidas e posicionadas: abre no **Fusion 360**, no **Bambu Studio** e no **Orca Slicer**.
- **`0_TODAS_AS_BANDEJAS_so_para_conferir.step`**: todas as bandejas lado a lado, sobre mesas cinza, só para conferir no Fusion (não imprimir).
- Mesa maior? Mude `mesa_impressora` no `medidas.txt` e rode o `GERAR.bat`.
- ⚠️ Enquanto houver medidas "MEDIR" no `medidas.txt`, estas bandejas são só para conferência: **não imprima a saia nem a cabeça antes de medir as peças reais**.

## Bandejas: retangulares ou redondas

As bandejas são **retangulares com cantos arredondados** (desde 2026-10-13), na proporção 1 : 1,4:

| | Redondas (antes) | Retangulares (agora) |
|---|---|---|
| Bandeja de baixo | Ø130 · ≈133 cm² | 136 × 190 · ≈256 cm² (**1,9×**) |
| Bandeja de cima | Ø100 · ≈79 cm² | 104 × 146 · ≈150 cm² (**1,9×**) |

Elas são mais largas que o corpo da base (10 cm), como a bandeja de um garçom, mas não passam da largura das rodas (~16 cm).
Para voltar às redondas, troque em `medidas.txt` para `bandeja_formato = "redonda"` e rode o `GERAR.bat`.

## Protótipo demonstrativo (robô completo com eletrônica e fios)

`step/prototipo_completo.step` mostra o robô **pronto**: carcaça, chassi, rodas, motores, baterias, LM2596, protoboard, driver, ESP32-CAM e **todos os fios**, seguindo o `manual_montagem_fisica.md` (Etapas 6 a 8). **Não é para imprimir.** Serve para entender onde fica cada coisa e por onde passa cada fio. O `GERAR.bat` gera esse arquivo de novo junto com as peças.

| Robô pronto | Carcaça transparente |
|---|---|
| ![](imagens/prototipo_completo.png) | ![](imagens/prototipo_transparente.png) |

| Fiação (sem a carcaça) | Visto de cima | ESP32-CAM na cabeça |
|---|---|---|
| ![](imagens/prototipo_fiacao.png) | ![](imagens/prototipo_cima.png) | ![](imagens/prototipo_cabeca.png) |

### Como ver no Fusion 360

1. **Arquivo → Abrir → Abrir do meu computador** → `step\prototipo_completo.step`.
2. À esquerda fica o **Navegador** (*Browser*). Abra **Componentes**: o robô está dividido em 5 grupos:
   `1_carcaca` · `2_chassi_rodas_motores` · `3_energia` · `4_controle` · `5_fios`.
3. Clique no **olho** 👁 ao lado de `1_carcaca` para escondê-la. Aparece tudo o que fica por dentro.
4. Abra um grupo (setinha ▸) para esconder ou mostrar peças avulsas, por exemplo um fio só.
5. Para medir: **Inspecionar → Medir** (tecla **I**).

### Legenda dos fios (cor no modelo → ligação)

| Cor | Fio no modelo | Liga | Passo do manual |
|---|---|---|---|
| 🔴 Vermelho | `01`, `03`, `08` | Bateria (+), LM2596 IN+, driver + → **linha 1 (+BAT 7,4 V)** | 6.1, 6.3, 7.2 |
| ⚫ Preto | `02`, `04`, `06`, `09` | Bateria (−), LM2596 IN− e OUT−, driver − → **linha 3 (GND)** | 6.2, 6.4, 6.6, 7.2 |
| ⚫ Preto curto | `07` | Ponte 3e → 3f: liga as duas metades da linha 3 (GND tem muitos fios) | 6, observação |
| 🟠 Laranja | `05` | LM2596 OUT+ (5,0 V) → **linha 5 (+5V)** | 6.5 |
| 🟠 Laranja | `12_esp_5V` | ESP32-CAM **5V** → linha 5 | 8.5 |
| ⚫ Preto | `12_esp_GND` | ESP32-CAM **GND** → linha 3 (metade f-j) | 8.5 |
| 🟡 Amarelo | `12_esp_IO14` | IO14 → driver **IN1** (motor esquerdo) | 8.3 |
| 🟢 Verde | `12_esp_IO15` | IO15 → driver **IN2** (motor esquerdo) | 8.3 |
| 🔵 Azul | `12_esp_IO13` | IO13 → driver **IN3** (motor direito) | 8.3 |
| 🟣 Roxo | `12_esp_IO12` + `10` | IO12 → **linha 7** → driver **IN4**, com o resistor 10 kΩ da linha 7 ao GND | 8.4 |
| 🔴⚫ Finos | `11_motor_...` | Motor esquerdo → **MOTOR-A**, motor direito → **MOTOR-B** (soldados) | 7.2 |

Na protoboard, as faixas coloridas marcam as linhas usadas: vermelha = linha 1, preta = linha 3, laranja = linha 5, roxa = linha 7. O capacitor de 470 µF (cilindro azul-escuro) fica entre a linha 5 (+) e a linha 3 (−).

Os 6 fios da ESP32-CAM **descem por dentro da coluna oca**. Esconda `1_carcaca` para vê-los.

### O que é só ilustrativo

- Os componentes são **blocos simplificados**, com medidas de anúncio ou estimadas.
- **A ordem dos pinos da ESP32-CAM e do driver no modelo é ilustrativa.** Na montagem real, confira sempre pelo **nome impresso** na placa (manual, 8.1).
- O contorno da base veio da foto do anúncio (comprimento e larguras são as cotas da foto). As curvas da frente e de trás, as posições da eletrônica, das rodas, dos furos e da chave são estimativas marcadas "MEDIR" no `medidas.txt`: confira com régua antes de imprimir a saia.
- Frente do robô = **lado para onde a câmera olha** (onde está o nome). Nesta carcaça, os motores ficam **atrás** e a roda boba na frente.

## Como montar

0. **Antes da saia:** parafuse o **pé antitombo** embaixo da traseira da base com 2 parafusos M3 × 10, de cima para baixo (a ponta redonda para baixo, atrás das rodas). Monte a eletrônica nas posições da tabela "O que muda": **pilhas na frente**, com a chave do suporte do lado direito, embaixo do furo da chave da saia.
1. A saia é parafusada no chassi com **4 parafusos M3 de baixo para cima**: passam pelos furos da base e rosqueiam direto no plástico (furo de 2,8 mm). A base tem muitos furos; se nenhum coincidir com os da saia, dá para furar a base com broca de 3 mm (acrílico racha: devagar, sem pressão, com fita crepe por cima e madeira por baixo).
2. A coluna encaixa na saia, perto da traseira. O lado reto impede que ela gire.
3. Desça a **espinha de baixo** pela coluna até ela assentar no teto da saia, com a aleta comprida apontando para a frente.
4. A bandeja de baixo desce pela coluna até o 1º degrau, apoiada na espinha. O furo das bandejas também tem um lado reto: gire a bandeja até ele "cair" na coluna. A parte grande da bandeja fica **na frente** da coluna.
5. Desça a **espinha de cima** até ela assentar no colar da bandeja de baixo, com a aleta comprida para a frente. Depois coloque a bandeja de cima, que desce até o 2º degrau.
6. A ESP32-CAM entra pela parte de trás da cabeça, encostada nos 4 apoios. A tampa de trás encaixa por pressão e o pino dela segura a placa.
7. A cabeça encaixa no topo da coluna. Os 6 fios sobem pelo canal oco (18 mm).

## Ver no OpenSCAD (alternativa, com o Customizer)

1. Abra `robo_garcom_carcaca.scad` no OpenSCAD.
2. Menu **Janela** (*Window*) → desmarque **Ocultar Customizer** (*Hide Customizer*).
3. Mude o número, aperte **F5** para ver.
4. Em **peca**, escolha a peça. Aperte **F6** (renderizar) e depois **F7** (exportar STL).

> O Customizer muda as medidas **só na tela**: não altera o `medidas.txt`. Se gostar de um valor, copie-o para o `medidas.txt` e rode o `GERAR.bat`.

> Nunca use "escala" (110%) no fatiador: ela muda também os furos e os encaixes.

## Medidas: o que já é real e o que falta medir

| Medida | Situação |
|---|---|
| Base (acrílico com papel protetor marrom): 212 mm de comprimento, corpo de 100 mm, leque de 150 mm | ✅ Da foto do anúncio (2026-10-14) |
| Curva da frente, começo do leque e pontas do leque | 🟡 Estimados pela foto (MEDIR) |
| Regulador 66 × 35 × 13 mm | ✅ Do anúncio |
| Protoboard 45 × 34 × 8,5 mm | ✅ Do anúncio |
| ESP32-CAM 27 × 40,5 mm | ✅ Medida padrão da placa |
| Suporte 2×18650 ≈ 78 × 41 × 25 mm | 🟡 Calculado pela foto (pilha 18 × 65 mm) |
| **Furos da saia na base** (frente ±38/+88, trás ±56/−88) | ⚠️ **MEDIR** (ou furar a base) |
| **Posição e altura do eixo das rodas** | ⚠️ **MEDIR** (as 3 fotos dão entre ~12,3 e ~13,5 cm da frente; modelo usa 13,5. Rodas a ±65 mm do meio) |
| **Posição da chave liga/desliga** | ⚠️ **MEDIR** |
| **Posição da lente e do LED de flash na placa** | ⚠️ **MEDIR** (antes de imprimir a cabeça) |
