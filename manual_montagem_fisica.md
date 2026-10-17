# 🔧 Manual de Montagem Física: Robô Garçom IoT com Câmera

Guia **cronológico**, do zero ao robô andando com vídeo ao vivo no celular.
Escrito para quem **sabe programar, mas nunca mexeu com eletrônica**.

> **Regra de ouro:** só faça ou desfaça ligações com a **chave da bateria DESLIGADA** e o **cabo USB desconectado**.

**Tempo estimado:** 3 a 5 horas na primeira vez.

---

## Índice

0. [Conceitos mínimos de eletrônica (leia antes!)](#etapa-0)
1. [Preparar o computador](#etapa-1)
2. [Teste de bancada: só a ESP32-CAM](#etapa-2)
3. [Montagem mecânica do chassi](#etapa-3)
4. [Preparar os motores](#etapa-4)
5. [Preparar e calibrar a alimentação](#etapa-5)
6. [Barramentos de energia na protoboard](#etapa-6)
7. [Ligar o driver de motor](#etapa-7)
8. [Ligar a ESP32-CAM](#etapa-8)
9. [Revisão antes de energizar](#etapa-9)
10. [Primeira energização (rodas no ar)](#etapa-10)
11. [Calibração de direção](#etapa-11)
12. [Atualizações por Wi-Fi (OTA)](#etapa-12)
13. [Solução de problemas](#etapa-13)
14. [Dicas para o portfólio](#etapa-14)

---

<a id="etapa-0"></a>
## Etapa 0: Conceitos mínimos de eletrônica

Pense nisto como o "README" da eletricidade:

| Conceito | Analogia de software | Na prática aqui |
|---|---|---|
| **Tensão (V)** | O "tipo" do dado: tem que ser compatível | ESP32-CAM recebe **5 V** no pino 5V. Motores aguentam ~6 V. Bateria fornece 7,4–8,4 V |
| **Corrente (A)** | A "banda" consumida | Câmera + Wi-Fi puxam picos de ~500 mA. Cada motor, até ~1 A ao arrancar |
| **GND (terra)** | O "ponto de referência" comum, como o fuso horário UTC | **Todos os GNDs precisam estar ligados entre si.** Sem GND comum, os sinais da ESP32 não significam nada para o driver |
| **Polaridade** | Inverter `+` e `−` é como um `rm -rf` | Fio **vermelho = +**, **preto = − (GND)**. Inverter pode queimar a placa na hora |
| **Curto-circuito** | Loop infinito que derrete coisas | Nunca deixe `+` encostar direto no `−` |
| **PWM** | Ligar/desligar muito rápido para simular "meio ligado" | É assim que controlamos a velocidade dos motores |
| **Ponte H (driver)** | Um "adaptador" ou proxy | A ESP32 fornece só ~20 mA por pino. O driver recebe esse sinal fraco e entrega a corrente forte da bateria aos motores |

### Por que alimentação separada?

Motores DC são "ruidosos": ao arrancar, puxam muita corrente e derrubam a tensão por milissegundos. A ESP32-CAM é sensível. Se a tensão cair, ela **reinicia** (*brownout*) ou a **câmera trava**. Por isso:

```
Bateria 7,4 V ─┬──▶ Driver ──▶ Motores        (caminho "sujo", corrente alta)
               └──▶ Regulador LM2596 ──▶ 5,0 V ──▶ ESP32-CAM   (caminho "limpo", estabilizado)
               GND comum a todos
```

### Cuidados com baterias 18650

- São baterias de lítio de alta capacidade. Em curto, esquentam muito e podem pegar fogo.
- Respeite a polaridade no suporte: o lado **plano** é o `−` e o lado com **ressalto** é o `+`. O suporte tem `+`/`−` gravado.
- Carregue **só** no carregador próprio, fora da montagem, e nunca deixe carregando sem supervisão.
- Abaixo de **3,0 V por célula**, pare de usar e recarregue.

---

<a id="etapa-1"></a>
## Etapa 1: Preparar o computador

VS Code, PlatformIO e compilador **já foram instalados** na Fase 1 do `GUIA_PASSO_A_PASSO.md`. Falta só uma coisa, que depende da placa ter chegado:

**Driver USB CH340** (Windows): conecte a base ESP32-CAM-MB, **sem** a ESP32-CAM encaixada, com o cabo USB. Abra o *Gerenciador de Dispositivos* (clique com o botão direito no Menu Iniciar → Gerenciador de Dispositivos) → *Portas (COM e LPT)*.
- Se aparecer `USB-SERIAL CH340 (COMx)`, está pronto. Anote o número `COMx`.
- Se aparecer um dispositivo com ⚠️ amarelo, baixe o driver CH341SER no site do fabricante (WCH) e instale.
- Se **nada** aparecer, o cabo provavelmente é só de carga. Troque por um cabo de dados.

---

<a id="etapa-2"></a>
## Etapa 2: Teste de bancada (só a ESP32-CAM)

**Objetivo:** confirmar que placa, câmera, Wi-Fi e dashboard funcionam **antes** de qualquer fiação. Se algo falhar aqui, o problema não é a montagem.

1. **Confira o cabo flat da câmera.** Na ESP32-CAM, o conector preto tem uma trava que levanta. A fita da câmera deve estar totalmente inserida e a trava, abaixada. Depois, a câmera pode ser dobrada e presa sobre o módulo.
2. **Encaixe a ESP32-CAM na base MB**, câmera para cima, alinhando os rótulos dos pinos. Ela só encaixa alinhada em uma orientação.
3. Conecte o USB ao PC.
4. No VS Code, abra o terminal do PlatformIO (ícone 🐜 → *New Terminal*) e rode:
   ```
   pio run -e esp32cam -t upload
   ```
   - Se travar em `Connecting........_____`: **segure o botão IO0** da base MB, **aperte e solte RST**, e então **solte IO0**. O upload deve começar.
5. Ao terminar (`SUCCESS`), abra o monitor serial:
   ```
   pio device monitor -e esp32cam
   ```
   Aperte **RST** na placa. Você deve ver:
   ```
   === Robo Garcom IoT ===
   [MOT] Motores prontos
   [CAM] Camera OV2640 pronta
   [NET] Rede "RoboGarcom-IoT" criada. IP: 192.168.4.1
   [WEB] Dashboard: http://192.168.4.1/
   [SYS] Pronto! Conecte-se ao Wi-Fi e abra http://192.168.4.1
   ```
6. No **celular**, conecte ao Wi-Fi **`RoboGarcom-IoT`** (senha **`garcom1234`**). O celular pode avisar "sem internet". Escolha **manter conectado**.
7. Abra o navegador em **http://192.168.4.1**. Você deve ver o vídeo ao vivo. Teste o botão 💡 Flash.
8. ✅ Passou? Desconecte o USB e **retire a ESP32-CAM da base MB** com cuidado, puxando reto e balançando levemente. Ela vai para o robô; a base MB fica guardada para emergências. As próximas atualizações serão via Wi-Fi (Etapa 12).

> ⚠️ Se aparecer `[CAM] ERRO 0x105` ou `0x20004`: o cabo flat está mal encaixado. Desligue, reencaixe e tente de novo.

---

<a id="etapa-3"></a>
## Etapa 3: Montagem mecânica do chassi

Os kits variam um pouco, mas a sequência é sempre esta:

1. **Remova o papel protetor marrom** do acrílico (ambos os lados; água morna ajuda). No kit escolhido, a base parece madeira nas fotos do anúncio, mas as linhas vermelhas e as letras impressas mostram que é **acrílico com papel protetor**. Para conferir: raspe um cantinho com a unha; se o marrom descolar, é papel.
   > Se o kit vier com um **suporte de 4 pilhas AA**, não use: 4 AA dão ~6 V, pouco para o regulador entregar 5 V estáveis. O projeto usa as 2 baterias 18650 (7,4 V).
   > **Formato da base do kit escolhido:** corpo estreito de 10 cm com a frente arredondada e traseira larga "em leque" de 15 cm; 21,2 cm de comprimento. As rodas ficam **do lado de fora** do corpo estreito, perto do leque. A roda boba (rodízio giratório) vai embaixo da ponta estreita (a **frente**); os motores vão embaixo da base, com os discos pretos nos recortes em "+".
2. **Fixe os motores** na placa de baixo usando as peças de acrílico em "T" (2 por motor) e os parafusos longos M3×30. O eixo do motor aponta **para fora**. Os dois motores ficam espelhados, com os terminais elétricos voltados **para dentro** do chassi.
3. **Encaixe as rodas** nos eixos amarelos (encaixe por pressão, é duro mesmo). Não force o motor contra a mesa; segure a roda e o motor juntos.
4. **Instale a roda boba** (rodízio) na extremidade oposta aos motores, usando os espaçadores de latão. Esse lado é a **frente** do robô; os motores ficam **atrás**.
   > **Frente = lado para onde a câmera olha.** Neste projeto, a câmera (e a cabeça da carcaça 3D, com o nome "Bandejito 1.0") fica virada para o lado da roda boba. Robôs com tração traseira e roda boba na frente são comuns e andam bem. Se as rodas girarem ao contrário, isso se corrige na Etapa 11, sem mexer na montagem.
5. **Ainda não instale a placa de cima** (se houver). Vamos fixar componentes primeiro.

---

<a id="etapa-4"></a>
## Etapa 4: Preparar os motores

1. Se os motores **não vieram com fios**: solde um fio **vermelho** em um terminal e um **preto** no outro, em cada motor (~15 cm). Nesse caso a cor é só convenção, porque motor DC não tem polaridade fixa; inverter os fios só inverte o sentido de giro.
2. **Solde um capacitor cerâmico de 100 nF ("104")** entre os dois terminais de cada motor. Ele não tem polaridade. Isso reduz o ruído elétrico que pode travar a câmera.
3. Passe os fios pelos furos do chassi para a parte de cima. Use furos **ao lado** de onde ficarão as pilhas, a cerca de **3 cm do meio** para cada lado e uns 5 cm à frente do eixo das rodas: o meio da frente fica todo ocupado pelo suporte das pilhas (veja a Etapa 8.6). Se nenhum furo do kit cair ali, use o mais próximo.
4. Identifique: **motor esquerdo** e **motor direito**, olhando o robô **por trás**, com a frente (lado da roda boba, para onde a câmera vai olhar) para longe de você. Marque com fita crepe "E" e "D".

---

<a id="etapa-5"></a>
## Etapa 5: Preparar e calibrar a alimentação

### 5.1 Baterias

1. Meça cada 18650 com o multímetro em **DCV 20 V**. Valores esperados: 3,6–4,2 V. Se estiverem baixas, carregue antes.
2. Com a **chave do suporte DESLIGADA**, insira as baterias respeitando `+`/`−` gravados no suporte.
3. Ligue a chave e meça entre os fios vermelho e preto do suporte: **7,2–8,4 V**. Desligue a chave.

### 5.2 Ajustar o LM2596 para 5,0 V (CRÍTICO)

> ⚠️ **O LM2596 vem de fábrica com tensão de saída aleatória, às vezes 12 V ou mais.** Ligá-lo na ESP32-CAM sem ajustar **queima a placa**.

1. Ligue o suporte de baterias **apenas** no LM2596, **sem nada na saída**:
   - Fio vermelho da bateria → `IN+`
   - Fio preto da bateria → `IN−`
2. Ligue a chave. Meça a saída `OUT+`/`OUT−` com o multímetro, ou leia o display se o seu tiver.
3. Gire o **parafuso do trimpot** (cubo azul) com a chave de fenda pequena:
   - Sentido anti-horário costuma **baixar** a tensão. Pode precisar de **10 a 20 voltas** antes de começar a mudar.
4. Ajuste até **5,0 V a 5,1 V**.
5. Desligue a chave. Marque o LM2596 com fita: **"5V AJUSTADO, NÃO MEXER"**.

---

<a id="etapa-6"></a>
## Etapa 6: Barramentos de energia na protoboard

A mini protoboard serve como **"hub" de energia**, para que vários fios se encontrem num ponto só.

### Como a mini protoboard funciona

```
     a b c d e   f g h i j
 1   ● ● ● ● ●   ● ● ● ● ●     Cada LINHA de 5 furos (a-e) é conectada internamente.
 2   ● ● ● ● ●   ● ● ● ● ●     O lado f-j é OUTRA conexão independente.
 3   ● ● ● ● ●   ● ● ● ● ●     Linhas diferentes NÃO se conectam.
 …
```

### Defina 3 "trilhas"

| Linhas da protoboard | Nome | Conecta |
|---|---|---|
| Linha 1 (a-e) | **+BAT** (7,4 V) | Saída da chave da bateria, `IN+` do LM2596, `+`/VCC do driver |
| Linha 3 (a-e) | **GND** (comum) | `−` da bateria, `IN−`/`OUT−` do LM2596, GND do driver, GND da ESP32-CAM, resistor 10 kΩ, `−` do capacitor |
| Linha 5 (a-e) | **+5V** | `OUT+` do LM2596, 5V da ESP32-CAM, `+` do capacitor |

> Se faltarem furos na trilha GND (ela recebe muitos fios), use também a linha 3 do lado f-j, ligando as duas metades com um jumper macho-macho de 3-c para 3-f.

### Ligações desta etapa (chave DESLIGADA)

1. Fio **vermelho** do suporte de bateria → **linha 1 (+BAT)**
2. Fio **preto** do suporte → **linha 3 (GND)**
3. LM2596 `IN+` → **linha 1 (+BAT)**
4. LM2596 `IN−` → **linha 3 (GND)**
5. LM2596 `OUT+` → **linha 5 (+5V)**
6. LM2596 `OUT−` → **linha 3 (GND)**
7. **Capacitor eletrolítico 470–1000 µF**: perna **longa (+)** → linha 5 (+5V), perna **curta, com faixa branca "−"** → linha 3 (GND).
   > ⚠️ Capacitor eletrolítico **tem polaridade**. Ao contrário, ele estufa e pode estourar.

---

<a id="etapa-7"></a>
## Etapa 7: Ligar o driver de motor

### 7.1 Identifique os pinos do seu driver

**MX1508 (recomendado):**
```
  ┌───────────────────────────┐
  │ MOTOR-A        MOTOR-B    │  ← saídas para os motores (2 furos/bornes cada)
  │                           │
  │  +  −  IN1 IN2 IN3 IN4    │  ← alimentação e entradas de controle
  └───────────────────────────┘
```
(Em alguns MX1508 a alimentação aparece como `VCC`/`GND` ou `+`/`−`. Se os pinos vieram soltos, solde a barra de pinos antes.)

**L9110S (alternativa):** `B-IA`, `B-IB`, `GND`, `VCC`, `A-IA`, `A-IB` + bornes Motor A / Motor B.

### 7.2 Ligações (chave DESLIGADA)

| De | Para | Fio sugerido |
|---|---|---|
| Driver `+` / `VCC` | Protoboard **linha 1 (+BAT)** | Vermelho, macho-fêmea |
| Driver `−` / `GND` | Protoboard **linha 3 (GND)** | Preto, macho-fêmea |
| **Motor ESQUERDO** (2 fios) | Driver **MOTOR-A** (L9110S: Motor A) | Fios do motor |
| **Motor DIREITO** (2 fios) | Driver **MOTOR-B** (L9110S: Motor B) | Fios do motor |

> Por que o driver recebe 7,4 V se os motores são de 6 V? O firmware limita o PWM a ~70% (`MOTOR_MAX_DUTY = 180`), então a tensão média no motor fica perto de 5,9 V. Assim aproveitamos a bateria sem um segundo regulador.

---

<a id="etapa-8"></a>
## Etapa 8: Ligar a ESP32-CAM

### 8.1 Conheça os pinos da ESP32-CAM

Os nomes estão impressos na **parte de baixo** da placa. **Sempre confira pelo nome impresso, não pela posição**: existem clones com ordem diferente.

```
          ESP32-CAM (AI-Thinker), vista de baixo, com os nomes impressos
             ┌──────────────────────────────┐
     🟢 5V   │●                            ●│ 3V3     ⛔ não usar como entrada
     🟢 GND  │●                            ●│ IO16    ⛔ PSRAM
     🟡 IO12 │●                            ●│ IO0     ⛔ câmera/boot
     🟡 IO13 │●                            ●│ GND     ⚠️ em alguns clones NÃO é GND
     🟡 IO15 │●                            ●│ VCC     ⛔ saída de 3,3/5 V, não ligar
     🟡 IO14 │●                            ●│ U0R/IO3 ⛔ serial
     ⚪ IO2  │●                            ●│ U0T/IO1 ⛔ serial
     ⛔ IO4  │●   (LED flash do outro lado) ●│ GND
             └──────────────────────────────┘
   🟢 = alimentação usada   🟡 = sinal usado pelos motores
   ⚪ = livre, mas reservado  ⛔ = proibido (câmera, PSRAM, serial ou flash)
```

### 8.2 Pinos que NÃO podem ser usados, e por quê

| Pino | Motivo |
|---|---|
| **IO0** | Clock da câmera (XCLK) **e** seleção do modo de gravação. Mexer nele impede o boot e a câmera |
| **IO16** | Ligado internamente à memória PSRAM (buffers de vídeo). Usar causa travamentos aleatórios |
| **IO1 (U0T) / IO3 (U0R)** | Comunicação serial usada para gravar o firmware e para o monitor serial |
| **IO4** | LED de **flash**, que puxa ~200 mA. Reservado para o botão 💡 do dashboard |
| **IO2** | Define o modo de gravação no boot e é dado do cartão SD. Fica como reserva |
| **3V3 / VCC** | Não alimente por aqui: a placa precisa de 5 V no pino **5V** para o regulador interno funcionar bem |
| Internos: IO5, 18, 19, 21, 22, 23, 25, 26, 27, 32, 34, 35, 36, 39 | **Câmera.** Nem aparecem nos pinos laterais: estão soldados ao conector da câmera |

> **Por que IO12, 13, 14 e 15 estão livres?** Eles são do slot microSD. Como **não usamos o cartão SD**, ficam disponíveis para os motores.

### 8.3 Ligações de controle (chave DESLIGADA)

Use jumpers **fêmea-fêmea** (ESP32-CAM ↔ driver) e **macho-fêmea** (ESP32-CAM ↔ protoboard).

| # | Pino ESP32-CAM | Vai para (MX1508) | Vai para (L9110S) | Função |
|---|---|---|---|---|
| 1 | **IO14** | `IN1` | `A-IA` | Motor esquerdo, sentido 1 |
| 2 | **IO15** | `IN2` | `A-IB` | Motor esquerdo, sentido 2 |
| 3 | **IO13** | `IN3` | `B-IA` | Motor direito, sentido 1 |
| 4 | **IO12** | `IN4` | `B-IB` | Motor direito, sentido 2 |

### 8.4 Resistor de segurança no IO12 (obrigatório)

O **IO12** é lido pela ESP32 no momento do boot para escolher a tensão da memória flash. Se ele estiver em **HIGH** nessa hora, a placa **não inicia** (`flash read err, 1000`). Alguns drivers "puxam" as entradas para HIGH. O resistor garante LOW.

- **Resistor 10 kΩ** (faixas marrom-preto-laranja): uma perna na **linha 7 da protoboard**, a outra na **linha 3 (GND)**.
- Na mesma **linha 7**, coloque um jumper macho-fêmea indo ao **IO12** da ESP32-CAM e outro macho-fêmea indo ao **IN4** do driver. Isso substitui a ligação direta IO12→IN4 da tabela acima.

```
 ESP32 IO12 ──────┬────── Driver IN4
                  │
                 [10kΩ]
                  │
                 GND
```

### 8.5 Alimentação da ESP32-CAM (POR ÚLTIMO)

| De | Para |
|---|---|
| ESP32-CAM **5V** | Protoboard **linha 5 (+5V)** |
| ESP32-CAM **GND** (o que fica **ao lado do 5V**) | Protoboard **linha 3 (GND)** |

### 8.6 Fixação

- Fixe a ESP32-CAM com a **câmera apontando para frente** (lado da roda boba), sem obstruções. Com a carcaça 3D, ela fica dentro da cabeça, que já aponta para esse lado.
- Fixe cada peça no seu lugar com fita dupla-face espessa. As posições abaixo são as da carcaça 3D, que foi desenhada em volta delas (o desenho completo está em `carcaca/step/prototipo_completo.step` e em `carcaca/imagens/prototipo_cima.png`):

| Peça | Onde fica (olhando o robô de cima, com a frente para cima) | Por quê |
|---|---|---|
| **Suporte das 2 pilhas 18650** | **Na frente**, deitado no meio, com as pilhas de frente para trás e a **chave virada para o lado direito** | É a peça mais pesada: na frente, segura o robô alto para ele não "empinar" para trás. A chave fica embaixo do furo da chave na saia. As pilhas saem pela **portinha do lado esquerdo** da saia |
| **LM2596** (regulador com display) | **Atrás, do lado esquerdo**, com o display para cima | Pela **portinha de trás** dá para ver o display e girar o parafusinho (trimpot) do 5,0 V |
| **Mini protoboard** | No meio, do lado direito (entre as pilhas e o driver) | Fica perto de tudo: é o "hub" de energia |
| **Driver dos motores** | **Atrás, do lado direito**, perto dos motores | Fios curtos até os motores |
| **ESP32-CAM** | Dentro da cabeça, em cima da coluna (que fica atrás, quase em cima do eixo das rodas) | Os 6 fios descem pelo canal oco da coluna |

- **Pé antitombo** (peça impressa da carcaça): parafuse **embaixo da traseira da base**, atrás das rodas, com 2 parafusos M3 × 10 de cima para baixo. A ponta redonda fica uns 6 mm acima do chão: se o robô empinar, ela encosta e segura.
- **Bandeja, balança e botão** (em cima da saia): o passo a passo está em `carcaca/LEIA-ME.md`, "Como montar" (passos 3 a 6). Resumo: a **célula de carga** fica presa na base da balança (anel na coluna); a **aranha** é parafusada na ponta solta da célula; a **bandeja** só encaixa nos 4 pininhos da aranha e **não pode encostar em mais nada**. Os fios da célula e do botão entram na saia pelo furo de 8 mm do teto, ao lado da coluna, **com folga**. A ligação deles na ESP32 DevKit (módulo HX711) é da **Fase 5**: até lá, deixe os fios enrolados dentro da saia.
- Organize os cabos com abraçadeiras. Nada pode encostar nas rodas.

### 8.7 Diagrama completo

```
                     ┌─────────────────────────────┐
                     │  Suporte 2×18650 + CHAVE    │
                     │    (+) 7,4 V      (−)       │
                     └──────┬─────────────┬────────┘
                            │             │
          ╔═════════════════╧═══╗   ╔═════╧══════════════════════════╗
          ║ linha 1: +BAT 7,4 V ║   ║ linha 3: GND COMUM             ║
          ╚══╤═══════════╤══════╝   ╚══╤══════╤══════╤══════╤═════╤══╝
             │           │             │      │      │      │     │
             │      ┌────▼──────┐      │      │      │      │     │
             │      │ LM2596    │ IN−──┘      │      │      │     │
             │      │ IN+  OUT− ├─────────────┘      │      │     │
             │      │ OUT+ =5,0V│                    │      │     │
             │      └────┬──────┘                    │      │     │
             │      ╔════╧════════════╗              │      │     │
             │      ║ linha 5: +5 V   ╟──[470µF]─────┘      │     │
             │      ╚════╤════════════╝  (+)    (−)         │     │
             │           │                                  │     │
             │           ▼                                  │     │
             │   ┌──────────────────┐                       │     │
             │   │ ESP32-CAM     5V │                       │     │
             │   │              GND ├───────────────────────┘     │
             │   │             IO14 ├──────┐                      │
             │   │             IO15 ├────┐ │                      │
             │   │             IO13 ├──┐ │ │                      │
             │   │             IO12 ├┐ │ │ │                      │
             │   └──────────────────┘│ │ │ │                      │
             │                       │ │ │ │                      │
             │        ┌──[10kΩ]──────┤ │ │ │  (linha 7)           │
             │        │              │ │ │ │                      │
             │       GND             │ │ │ │                      │
             │   ┌───────────────────▼─▼─▼─▼──┐                   │
             └──▶│ + (VCC)  IN4 IN3 IN2 IN1   │                   │
                 │ − (GND) ◀──────────────────┼───────────────────┘
                 │      MX1508 (ponte H)      │
                 │  MOTOR-A          MOTOR-B  │
                 └────┬─┬──────────────┬─┬────┘
                      │ │              │ │
                  ┌───┴─┴───┐      ┌───┴─┴───┐
                  │ Motor   │      │ Motor   │
                  │ ESQUERDO│      │ DIREITO │
                  │ (+100nF)│      │ (+100nF)│
                  └─────────┘      └─────────┘
```

Resumo em texto (útil para conferir fio a fio):

| # | De | Para |
|---|---|---|
| 1 | Bateria (+) | linha 1 (+BAT) |
| 2 | Bateria (−) | linha 3 (GND) |
| 3 | LM2596 IN+ | linha 1 (+BAT) |
| 4 | LM2596 IN− e OUT− | linha 3 (GND) |
| 5 | LM2596 OUT+ (5,0 V) | linha 5 (+5V) |
| 6 | Capacitor 470 µF (+) / (−) | linha 5 / linha 3 |
| 7 | Driver + / − | linha 1 / linha 3 |
| 8 | ESP32-CAM 5V / GND | linha 5 / linha 3 |
| 9 | ESP32-CAM IO14 | Driver IN1 |
| 10 | ESP32-CAM IO15 | Driver IN2 |
| 11 | ESP32-CAM IO13 | Driver IN3 |
| 12 | ESP32-CAM IO12 | linha 7 → Driver IN4 (+ resistor 10 kΩ da linha 7 ao GND) |
| 13 | Motor esquerdo | Driver MOTOR-A |
| 14 | Motor direito | Driver MOTOR-B |

---

<a id="etapa-9"></a>
## Etapa 9: Revisão antes de energizar

Com a **chave DESLIGADA**, faça este checklist. Ele leva 5 minutos e pode salvar sua placa.

### Teste de continuidade (multímetro no modo 🔊 "bip")

| Ponta 1 | Ponta 2 | Esperado |
|---|---|---|
| Linha 5 (+5V) | Linha 3 (GND) | **SEM bip** (se bipar = curto-circuito!) |
| Linha 1 (+BAT) | Linha 3 (GND) | **SEM bip** |
| Linha 1 (+BAT) | Linha 5 (+5V) | **SEM bip** (se bipar, a ESP32 receberia 7,4 V) |
| GND da ESP32-CAM | GND do driver | **BIP** (GND comum ok) |
| GND da ESP32-CAM | `−` da bateria | **BIP** |

> Ao medir +5V↔GND, o capacitor grande pode dar um "bip" curto inicial enquanto carrega. Um bip **contínuo** é que indica curto.

### Checklist visual

- [ ] Capacitor eletrolítico com a faixa "−" no GND
- [ ] Resistor 10 kΩ entre IO12 e GND
- [ ] ESP32-CAM ligada no **5V**, não no 3V3
- [ ] Nenhum fio nos pinos IO0, IO16, U0R, U0T, IO4
- [ ] LM2596 mede 5,0 V (ajustado na Etapa 5)
- [ ] Nenhum fio solto ou pino desencapado encostando em outro

---

<a id="etapa-10"></a>
## Etapa 10: Primeira energização (rodas no ar)

1. **Apoie o robô sobre um copo ou caixa**, com as rodas sem tocar a mesa. Ele pode sair andando por um erro de fiação.
2. **Ligue a chave.**
3. Observe nos primeiros 3 segundos:
   - ✅ O LED vermelho na parte de trás da ESP32-CAM **acende fixo** (pode levar ~2 s). Está tudo pronto.
   - ✅ As rodas podem dar uma tremidinha rápida no boot. É normal (pulsos dos GPIOs 14/15).
   - ❌ **Cheiro de queimado, fumaça ou algo esquentando muito:** **DESLIGUE IMEDIATAMENTE** e revise a Etapa 9.
   - ❌ LED piscando rápido: câmera não iniciou. Veja a Etapa 13.
4. Conecte o celular no Wi-Fi `RoboGarcom-IoT` e abra **http://192.168.4.1**.
5. Teste **cada botão segurando por 1 segundo** e observe as rodas.

---

<a id="etapa-11"></a>
## Etapa 11: Calibração de direção

Com o robô ainda no ar, aperte **▲ Frente** e observe. "Para frente" = no sentido para onde a **câmera olha** (lado da roda boba):

| O que acontece | Correção em `src/config.h` |
|---|---|
| As duas rodas giram "para frente" | ✅ Perfeito |
| Só a roda **esquerda** gira ao contrário | `#define MOTOR_LEFT_INVERTED true` |
| Só a roda **direita** gira ao contrário | `#define MOTOR_RIGHT_INVERTED true` |
| As duas giram ao contrário | Ambas `true` |
| Ao apertar ◀, o robô vira para a **direita** | Motores trocados: inverta os conectores MOTOR-A ↔ MOTOR-B no driver |
| Imagem de cabeça para baixo | `#define CAM_VFLIP true` |
| Imagem espelhada | `#define CAM_HMIRROR true` |

Depois de alterar, regrave pelo Wi-Fi (Etapa 12). Com tudo certo, coloque o robô no chão e divirta-se.

**Ajuste fino:**
- O robô não sai do lugar em velocidade baixa? Aumente `MOTOR_MIN_DUTY` (ex.: 110).
- Está muito rápido para a mesa? Diminua `MOTOR_MAX_DUTY` (ex.: 150).
- Puxa para um lado andando reto? Os motores amarelos têm variação de fábrica; ajuste rodas e eixos. Compensar por software fica como evolução futura.

---

<a id="etapa-12"></a>
## Etapa 12: Atualizações por Wi-Fi (OTA)

Com o robô montado, não precisa mais retirar a ESP32-CAM:

1. Ligue o robô.
2. Conecte o **PC** na rede `RoboGarcom-IoT`.
3. No terminal do VS Code:
   ```
   pio run -e esp32cam_ota -t upload
   ```
4. Os motores param automaticamente durante a atualização, e o robô reinicia sozinho no fim.

> Se o OTA falhar (ex.: você gravou um firmware com erro que não inicia o Wi-Fi), retire a ESP32-CAM, coloque-a na base MB e grave via USB (Etapa 2).

---

<a id="etapa-13"></a>
## Etapa 13: Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| LED vermelho **pisca rápido** | Câmera não iniciou | Reencaixe o cabo flat; confira 5 V estável no pino 5V |
| Placa não liga, nenhum LED | Sem 5 V ou polaridade invertida | Meça 5V↔GND na própria placa |
| Não inicia **só quando o driver está ligado** | IO12 em HIGH no boot | Confira o resistor 10 kΩ IO12→GND |
| Reinicia quando os motores arrancam | Queda de tensão (brownout) | Baterias carregadas? Capacitor 470 µF no lugar? GND comum firme? |
| Vídeo congela, mas os controles funcionam | Interferência ou distância | Fique a menos de 5 m; capacitores 100 nF nos motores; reduza para `FRAMESIZE_QVGA` |
| Controles com atraso | Celular em economia de energia ou muitos clientes | Feche outras abas com o vídeo (1 stream por vez) |
| Wi-Fi `RoboGarcom-IoT` não aparece | Firmware não iniciou | Veja o monitor serial via base MB |
| Celular desconecta da rede sozinho | O Android troca para dados móveis por "falta de internet" | Desative os dados móveis durante o uso ou escolha "manter conexão" |
| Um motor não gira | Fio solto ou driver sem alimentação | Meça +BAT no driver; teste o motor direto na bateria rapidamente |
| Motor só "zumbe" | PWM baixo demais | Aumente a velocidade no slider ou `MOTOR_MIN_DUTY` |
| Upload USB: `Timed out waiting for packet header` | Não entrou em modo gravação | IO0 + RST na base MB; cabo de dados; driver CH340 |

---

<a id="etapa-14"></a>
## Etapa 14: Dicas para o portfólio

1. **Grave um vídeo curto (30–60 s)** mostrando, em tela dividida, o robô andando e a tela do celular com o stream ao vivo.
2. **Fotografe a fiação** antes de fechar o chassi e inclua o diagrama da Etapa 8.7.
3. **Destaque as decisões de engenharia**, que é o que recrutadores técnicos valorizam:
   - Alimentação separada (buck 5 V + linha de motores) para evitar brownout.
   - Dois servidores HTTP para isolar o vídeo dos comandos de baixa latência.
   - Failsafe "homem-morto" (heartbeat de 200 ms + timeout de 600 ms no firmware).
   - Análise de restrição de pinos da ESP32-CAM (strapping do GPIO12 resolvido com pull-down).
   - Atualização OTA e firmware compatível com Arduino core 2.x/3.x.
4. **Evoluções possíveis:** sensor ultrassônico para frear sozinho, seguidor de linha, rota "mesa 1 → mesa 2", WebSocket no lugar de HTTP polling ou controle por joystick analógico.
