# 🛒 Lista de Compras Detalhada: Robô Garçom IoT com Câmera

Protótipo **em miniatura** (cabe sobre uma mesa, ~20 × 15 cm) com foco em **baixo custo**.
Preços aproximados em R$ (Mercado Livre / AliExpress / lojas de eletrônica, out/2026). Variam bastante; use como referência.

**Custo total estimado:** R$ 220 a R$ 380 (sem ferramentas), ou R$ 280 a R$ 480 com ferramentas básicas.

> **✅ Já comprado (dono, 2026-10-16):** kit chassi 2WD (item 2), ESP32-CAM (item 1), driver dos motores (item 3), LM2596 com display (item 4) e suporte 2×18650 (item 5). Ainda conferir: baterias, carregador, jumpers, protoboard, passivos e os parafusos M3 da carcaça (item 13).

---

## 1. Componentes principais (obrigatórios)

| # | Componente | Especificação exata | Qtd | Preço aprox. | Por que este? |
|---|---|---|---|---|---|
| 1 | ✅ **ESP32-CAM + base programadora** | **AI-Thinker ESP32-CAM** com câmera **OV2640** (2 MP) e **4 MB de PSRAM**, vendida em kit **com a placa base "ESP32-CAM-MB"** (Micro-USB ou USB-C, chip **CH340**) | 1 kit | R$ 45 – 75 | A base MB dispensa adaptador FTDI e jumpers para gravar: é plugar e enviar. O projeto depende da pinagem AI-Thinker |
| 2 | ✅ **Kit chassi 2WD miniatura** | Chassi de acrílico ou MDF, 2 rodas + **1 roda boba (rodízio)**, com **2 motores DC amarelos com caixa de redução (TT, 3–6 V, ~1:48)**, 2 rodas de 65 mm, parafusos e espaçadores | 1 | R$ 45 – 80 | Padrão do mercado, barato e fácil de montar |
| 3 | ✅ **Driver ponte H dupla (recomendado)** | **MX1508**, o "mini L298N" (2–10 V, **1,5 A contínuos/canal**, entradas IN1–IN4). Prefira anúncio **"com pinos soldados"** | 1 | R$ 8 – 15 | Pequeno, barato, sem a queda de 2 V do L298N grande e funciona com sinais de 3,3 V |
| 3b | *Alternativa ao item 3* | **L9110S** (HG7881), 2,5–12 V, 0,8 A/canal | 1 | R$ 8 – 15 | Também serve. Pinagem equivalente (A-1A, A-1B, B-1A, B-1B) |
| 4 | ✅ **Regulador step-down (buck)** | **LM2596** ajustável (entrada 4–35 V, saída 1,25–30 V, 3 A), **com display de tensão** de preferência | 1 | R$ 10 – 20 | Entrega 5,0 V estáveis à ESP32-CAM mesmo quando os motores puxam corrente. É o que impede a câmera de travar |
| 5 | ✅ **Suporte para 2 baterias 18650** | Suporte **2×18650 em série** (7,4 V), **com chave liga/desliga** e fios | 1 | R$ 8 – 15 | A chave serve para desligar tudo sem desconectar fios |
| 6 | **Baterias 18650** | 2× Li-ion 18650, **2000–3000 mAh reais**, de marca conhecida (Samsung, LG, Sony/Murata, Panasonic) ou retiradas de pack de notebook em bom estado. **Formato compatível com o suporte** (ponta lisa *flat top* ou com botão *button top*) | 2 | R$ 30 – 80 | ⚠️ Evite as de "9900 mAh": são falsas e podem ser perigosas |
| 7 | **Carregador de 18650** | Carregador dedicado de 2 slots com corte automático em 4,2 V (ex.: Liitokala Lii-202 ou similar) | 1 | R$ 30 – 70 | Nunca carregue 18650 com fonte improvisada |
| 8 | **Jumpers** | Kit 3×40 vias, 20 cm: **Macho-Macho, Fêmea-Fêmea, Macho-Fêmea** | 1 kit | R$ 15 – 30 | Fêmea-Fêmea vai direto nos pinos da ESP32-CAM e do driver |
| 9 | **Mini protoboard** | 170 pontos (SYB-170), com adesivo no fundo | 1–2 | R$ 4 – 10 | Usada como "barramento" de energia (5 V, +BAT e GND comuns) |

## 2. Componentes passivos (centavos, mas fazem diferença)

| # | Componente | Especificação | Qtd | Preço aprox. | Função |
|---|---|---|---|---|---|
| 10 | Resistor | **10 kΩ**, 1/4 W (marrom-preto-laranja) | 1 (compre 10) | R$ 2 | Pull-down no **GPIO12**: garante o boot da ESP32-CAM |
| 11 | Capacitor eletrolítico | **470 µF a 1000 µF, 16 V** ou mais | 1–2 | R$ 2 – 5 | "Pulmão" de energia junto ao 5 V da ESP32-CAM. Evita reset quando o Wi-Fi transmite |
| 12 | Capacitor cerâmico | **100 nF (código "104")** | 2 (compre 10) | R$ 2 | Soldado nos terminais de cada motor. Reduz o ruído elétrico que trava a câmera |
| 13 | Parafusos **M3 × 10** (cabeça Phillips) | Para a carcaça impressa: rosqueiam direto no plástico | 4 (versão 1) ou 6 (versão 2: +2 do pé antitombo); compre um saquinho de 20 | R$ 5 | Prendem a saia na base do kit (e o pé antitombo, na versão 2). Filamento PLA: do amigo que imprime |

## 3. Ferramentas

| Ferramenta | Obrigatória? | Preço aprox. | Uso |
|---|---|---|---|
| **Multímetro digital** (DT830B ou similar) | ✅ **Sim** | R$ 30 – 60 | Ajustar o LM2596 para 5,0 V **antes** de ligar na ESP32-CAM e conferir polaridade |
| Chave Phillips pequena e chave de fenda pequena | ✅ Sim | R$ 10 | Montar o chassi, borneiras do driver e trimpot do LM2596 |
| **Cabo USB de DADOS** (Micro-USB ou USB-C, conforme a base MB) | ✅ Sim | R$ 10 – 20 | Muitos cabos de celular só carregam e não transmitem dados |
| Ferro de solda 30–60 W + estanho | ⚠️ Provável | R$ 30 – 60 | Muitos kits trazem os motores **sem fios soldados**. Se o anúncio diz "motor com fios", dá para pular |
| Fita dupla-face espessa / abraçadeiras (enforca-gato) / cola quente | Recomendado | R$ 10 – 25 | Fixar placas e organizar cabos |
| Alicate de corte / desencapador | Recomendado | R$ 15 – 30 | Preparar fios |

## 4. Opcionais para o portfólio

| Item | Para quê |
|---|---|
| Antena externa 2,4 GHz com cabo **IPEX/U.FL** | Mais alcance. Exige mover um resistor 0 Ω SMD na placa, só para quem tem experiência |
| Bandeja/copo leve (impressão 3D ou tampa plástica) | Caracterizar o "garçom" nas fotos e no vídeo do portfólio |
| Espaçadores de nylon M3 | Montagem mais limpa da ESP32-CAM |

---

## 5. Fase 5: o garçom autônomo (sensores, voz e botão)

Tudo o que falta para o robô **sair do balcão sozinho, seguir a fita, parar e virar de frente para a mesa certa, falar a mensagem, esperar o botão verde e voltar**, como já funciona no simulador. Detalhes em `GUIA_PASSO_A_PASSO.md`, Fase 5.

> ⏳ **Quando comprar:** o ideal é depois que o robô andar pelo celular (Checkpoint da Fase 3), para não gastar antes de saber que a base funciona. Se quiser adiantar por causa do prazo de entrega, os itens 5.1 a 5.4 são os mais importantes. Nada daqui muda a montagem da Fase 3: só **acrescenta** peças.

### 5.1 Cérebro extra e sensores (o essencial)

| # | Item | Como buscar / especificação | Qtd | Preço aprox. | Para quê | Passo |
|---|---|---|---|---|---|---|
| 5.1 | **ESP32 DevKit V1** | "ESP32 DevKit V1 30 pinos" (chip ESP32-WROOM-32, USB **CH340** ou CP2102; USB-C se tiver). **Não é a ESP32-CAM** | 1 | R$ 35–45 | O "segundo cérebro": motores, sensores, voz e botão. A ESP32-CAM fica só com vídeo, Wi-Fi e página. As duas conversam por 2 fios (serial) | 5.2 |
| 5.2 | **Módulo seguidor de linha de 5 canais** | "módulo sensor seguidor de linha 5 canais TCRT5000" com **saída digital** (D1–D5) e um trimpot de sensibilidade por canal; alimentação **3,3–5 V** | 1 | R$ 15–25 | Enxergar a fita preta. ⚠️ Ligue no **3V3 da DevKit** (com 5 V as saídas passam do que a ESP32 aguenta) | 5.4 |
| 5.3 | **Sensor de distância a laser VL53L0X** | "VL53L0X módulo GY-530" (I2C, 2,8–5 V, até ~1,2 m) | 1 | R$ 15–20 | Freio automático: para a 15 cm de uma pessoa ou objeto e segue quando sai (vale também no modo manual) | 5.3 |
| 5.4 | **Jumpers fêmea-fêmea extras** | 20 cm, 1 fileira de 40 | 1 | R$ 8–12 | Os sensores e módulos têm pinos machos; a DevKit também | 5.2–5.6 |
| 5.5 | **Mini protoboard extra** | SYB-170 (igual à do item 9) | 1 | R$ 4–8 | Barramento de **3,3 V** e GND para os sensores | 5.2 |

### 5.2 Voz e botão (a parte "garçom")

| # | Item | Como buscar / especificação | Qtd | Preço aprox. | Para quê | Passo |
|---|---|---|---|---|---|---|
| 5.6 | **DFPlayer Mini** | "DFPlayer Mini MP3" (o módulo já tem amplificador de até 3 W) | 1 | R$ 12–20 | Tocar "Mesa 2, seu pedido chegou!" | 5.6 |
| 5.7 | **Cartão microSD** | Qualquer um **até 32 GB** (formatado em FAT32). Serve um antigo de celular | 1 | R$ 0–20 | Guardar os arquivos `0001.mp3` (mesa 1), `0002.mp3`, `0003.mp3` | 5.6 |
| 5.8 | **Alto-falante pequeno** | "alto-falante 8 ohms 2 W 40 mm" (de 28 a 40 mm; 0,5 a 3 W) | 1 | R$ 5–10 | A "boca" do robô | 5.6 |
| 5.9 | **Botão verde** | "push button 12 mm verde momentâneo" (de painel, com porca) ou "chave táctil 12 × 12 com capa verde". **O arcade de 30 mm é grande demais** para a cabeça de 5 cm | 1 (compre 2) | R$ 3–8 | O cliente aperta quando retira o pedido; o robô volta ao balcão | 5.6 |
| 5.10 | Resistor **1 kΩ** | 1/4 W (marrom-preto-vermelho) | 1 (compre 10) | centavos | Entre a DevKit e o DFPlayer (evita chiado) | 5.6 |

### 5.3 Fixação na carcaça

| # | Item | Especificação | Qtd | Preço aprox. | Para quê |
|---|---|---|---|---|---|
| 5.11 | Espaçadores **M3** de nylon ou latão | Kit sortido (fêmea-fêmea, 5 a 15 mm) com parafusos e porcas M3 | 1 kit | R$ 15–25 | Deixar a barra de sensores **5–10 mm acima do chão**, na frente da roda boba, e prender a DevKit |
| 5.12 | Fita dupla-face espessa | Já está nas ferramentas | — | — | DFPlayer e alto-falante dentro da saia |

> As peças impressas para esta fase (suporte da barra de sensores, janelinha do VL53L0X na frente da saia, furos do alto-falante e do botão) o Claude desenha quando as peças chegarem, com as medidas reais.

### 5.4 A pista (o "salão" em miniatura)

| # | Item | Especificação | Qtd | Preço aprox. | Para quê |
|---|---|---|---|---|---|
| 5.13 | **Fita isolante preta FOSCA**, 19 mm | Prefira a fosca: a brilhante reflete o infravermelho e o sensor pode achar que é chão | 1 rolo (~3 m usados) | R$ 5–10 | Linha de 164 cm + 3 marcas + 3 ramais + 2 blocos |
| 5.14 | **Placas de EVA branco** (ou cartolina branca) | EVA 40 × 60 cm, 2 mm. Para 2 × 1,5 m: **~13 placas** | 13 | R$ 25–45 | O chão claro do salão (o sensor precisa do contraste branco × preto) |
| 5.15 | Fita crepe larga | — | 1 | R$ 5–8 | Unir as placas **por baixo** (sem degrau por cima) |
| — | Mesas, cadeiras e balcão | Impressos em 3D (pasta `maquete/`, ~760 g de PLA) ou caixas e potes | — | — | O cenário |

### 5.5 Opcionais e futuros

| Item | Para quê | Preço aprox. |
|---|---|---|
| *(opcional)* Sensor de cor **TCS34725** | Reconhecer a mesa pela cor da marca (alternativa a contar marcas) | R$ 20–25 |
| *(Fase 6, NÃO comprar ainda)* 2 sensores de velocidade com disco encoder (LM393) | Odometria: andar sem fita | R$ 10–20 |

**Total aproximado da Fase 5:** **R$ 140–250** (5.1 a 5.4), sem a impressão da maquete.

### ✅ Checklist ao receber as peças da Fase 5

- [ ] A DevKit liga pela USB e aparece como porta COM (CH340 ou CP2102) no Gerenciador de Dispositivos.
- [ ] O módulo de linha tem **5 saídas** (D1–D5 ou OUT1–OUT5), VCC e GND. Com ele ligado em 3,3 V, os LEDs de cada canal acendem/apagam ao passar sobre a fita preta (ajuste no trimpot).
- [ ] O VL53L0X tem os pinos VIN, GND, SCL e SDA.
- [ ] O DFPlayer toca um `0001.mp3` de teste (o Claude passa o código de teste no Passo 5.6).
- [ ] O botão faz "clique" e tem 2 terminais (ou 4, ligados aos pares).

---

## ✅ Checklist ao receber os componentes

- [ ] A ESP32-CAM tem o adesivo/serigrafia **"AI-Thinker"** ou "ESP32-CAM" e o cabo flat da câmera está **encaixado e travado**.
- [ ] A câmera é **OV2640** (vem escrito no cabo flat ou no anúncio).
- [ ] A base MB tem botões **IO0** e **RST** e conector USB.
- [ ] Os motores giram ao encostar os fios em uma pilha AA de 1,5 V (teste rápido).
- [ ] As baterias 18650 medem entre **3,6 V e 4,2 V** cada no multímetro. Abaixo de 3,0 V, não use.
- [ ] O driver é MX1508 ou L9110S, com 4 entradas de controle e 2 saídas de motor.

## 💡 Dicas de compra

1. **Busque pelo termo exato:** `"ESP32-CAM-MB kit OV2640"`. Assim a base vem junto.
2. **Compre 2 ESP32-CAM** se o orçamento permitir (~R$ 40 a mais). É comum uma vir com defeito ou queimar por erro de fiação no primeiro projeto.
3. Prefira **kits de chassi com motores já soldados**.
4. Peça o **LM2596 com display**: você vê a tensão de saída sem precisar do multímetro toda hora.
5. **Não compre o L298N grande (vermelho, com dissipador):** desperdiça ~2 V, é pesado e grande para um chassi miniatura.
