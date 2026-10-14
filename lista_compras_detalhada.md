# 🛒 Lista de Compras Detalhada: Robô Garçom IoT com Câmera

Protótipo **em miniatura** (cabe sobre uma mesa, ~20 × 15 cm) com foco em **baixo custo**.
Preços aproximados em R$ (Mercado Livre / AliExpress / lojas de eletrônica, out/2026). Variam bastante; use como referência.

**Custo total estimado:** R$ 220 a R$ 380 (sem ferramentas), ou R$ 280 a R$ 480 com ferramentas básicas.

---

## 1. Componentes principais (obrigatórios)

| # | Componente | Especificação exata | Qtd | Preço aprox. | Por que este? |
|---|---|---|---|---|---|
| 1 | **ESP32-CAM + base programadora** | **AI-Thinker ESP32-CAM** com câmera **OV2640** (2 MP) e **4 MB de PSRAM**, vendida em kit **com a placa base "ESP32-CAM-MB"** (Micro-USB ou USB-C, chip **CH340**) | 1 kit | R$ 45 – 75 | A base MB dispensa adaptador FTDI e jumpers para gravar: é plugar e enviar. O projeto depende da pinagem AI-Thinker |
| 2 | **Kit chassi 2WD miniatura** | Chassi de acrílico 2 rodas + **1 roda boba (rodízio)**, com **2 motores DC amarelos com caixa de redução (TT, 3–6 V, ~1:48)**, 2 rodas de 65 mm, parafusos e espaçadores | 1 | R$ 45 – 80 | Padrão do mercado, barato e fácil de montar |
| 3 | **Driver ponte H dupla (recomendado)** | **MX1508**, o "mini L298N" (2–10 V, **1,5 A contínuos/canal**, entradas IN1–IN4). Prefira anúncio **"com pinos soldados"** | 1 | R$ 8 – 15 | Pequeno, barato, sem a queda de 2 V do L298N grande e funciona com sinais de 3,3 V |
| 3b | *Alternativa ao item 3* | **L9110S** (HG7881), 2,5–12 V, 0,8 A/canal | 1 | R$ 8 – 15 | Também serve. Pinagem equivalente (A-1A, A-1B, B-1A, B-1B) |
| 4 | **Regulador step-down (buck)** | **LM2596** ajustável (entrada 4–35 V, saída 1,25–30 V, 3 A), **com display de tensão** de preferência | 1 | R$ 10 – 20 | Entrega 5,0 V estáveis à ESP32-CAM mesmo quando os motores puxam corrente. É o que impede a câmera de travar |
| 5 | **Suporte para 2 baterias 18650** | Suporte **2×18650 em série** (7,4 V), **com chave liga/desliga** e fios | 1 | R$ 8 – 15 | A chave serve para desligar tudo sem desconectar fios |
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

## 5. Compras futuras: Fase 5 (autonomia), ainda NÃO comprar

Só depois que o robô estiver funcionando no modo manual (Checkpoint da Fase 3). Detalhes em `GUIA_PASSO_A_PASSO.md`, Fase 5.

| Item | Para quê | Preço aprox. |
|---|---|---|
| **ESP32 DevKit V1** (30 pinos, USB) | Segundo cérebro: motores + sensores | R$ 35–45 |
| **Sensor de distância a laser VL53L0X** (módulo I2C) | Freio automático diante de obstáculos | R$ 15–20 |
| **Barra de sensores de linha com 5× TCRT5000** | Seguir a fita no chão | R$ 15–25 |
| Fita isolante **preta**, 19 mm | O caminho do circuito | R$ 5 |
| Placas de EVA ou cartolina branca (~2 × 1,5 m, o mesmo tamanho do salão do simulador) | O "salão" em miniatura | R$ 15–30 |
| *(opcional)* Sensor de cor **TCS34725** | Reconhecer a mesa pela cor da marca | R$ 20–25 |
| *(opcional)* Botão de pressão (push button) | Confirmar "Entregue" no próprio robô | R$ 1 |

Total aproximado: **R$ 70–120**.

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
