# 🤖 Bandejito 1.0: Robô Garçom IoT com Câmera

![ESP32](https://img.shields.io/badge/ESP32--CAM-E7352C?logo=espressif&logoColor=white)
![C++](https://img.shields.io/badge/C++-Arduino%20core-00599C?logo=cplusplus&logoColor=white)
![PlatformIO](https://img.shields.io/badge/PlatformIO-F5822A?logo=platformio&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-simulador-339933?logo=nodedotjs&logoColor=white)
![JavaScript](https://img.shields.io/badge/HTML%2FCSS%2FJS-painel%20web-F7DF1E?logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-CadQuery-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)

> 🚧 **Projeto em construção.** O software e o simulador estão prontos e testados; as peças do robô físico estão a caminho.

Protótipo em miniatura de um robô garçom controlado pelo navegador, com **vídeo ao vivo** e **controle em tempo real**, construído com uma **ESP32-CAM** de baixo custo (~R$ 250 em peças). A próxima etapa é transformá-lo num **garçom autônomo**, que segue uma fita no chão, para na mesa certa, **percebe pela balança quando o cliente retira o pedido** e volta para o balcão.

<p align="center">
  <img src="docs/imagens/bandejito_esqueleto_3d.gif" alt="Modelo 3D do Bandejito: volta completa, portinhas abrindo e fechando, montagem peça por peça, a balança embaixo da bandeja, eletrônica e fios por dentro e o chassi" width="460"><br>
  <em>Modelo 3D completo, gerado por código a partir de um arquivo de medidas: portinhas, montagem peça por peça, a balança embaixo da bandeja, fiação por dentro e chassi.</em>
</p>

<p align="center">
  <img src="docs/imagens/bandejito_maquete_3d.gif" alt="Animação 3D na maquete: o Bandejito leva o pedido à Mesa 2, espera uma pessoa sair do caminho, gira 90° até ficar de frente para a mesa, o cliente pega o copo da bandeja, a balança percebe e ele volta ao balcão" width="600"><br>
  <em>O Bandejito na maquete impressa em 3D: leva o pedido à Mesa 2, freia e espera uma pessoa sair do caminho, gira 90° até ficar de frente para a mesa e, quando o cliente pega o copo, a balança percebe e ele volta ao balcão.</em>
</p>

## O que ele faz

- O robô cria a **própria rede Wi-Fi** e hospeda um painel web (não precisa de internet nem de app).
- **Vídeo MJPEG** da câmera direto numa tag `<img>`.
- Controle por botões (toque/mouse) ou teclado (WASD/setas), com curvas, controle de velocidade e flash.
- **Parada de segurança automática** se a conexão cair, e **partida suave** (o robô alto não "empina" na arrancada).
- **Simulador** em Node.js: o mesmo painel e a mesma API, rodando no PC sem hardware.
- **Garçom autônomo (no simulador):** fila de pedidos pelo celular, seguidor de linha com 5 sensores, contagem de mesas, **giro de 90° para ficar de frente para a mesa**, **mensagem de voz** ("Mesa 2, seu pedido chegou!"), confirmação da entrega (balança ou botão verde), volta ao balcão e freio diante de obstáculos.
- **Carcaça impressa em 3D**, paramétrica: **uma bandeja grande em cima de uma balança** (célula de carga de 500 g + HX711), botão verde no "nariz" da frente, cabeça que abriga a câmera, coluna recuada, pilhas na frente, pé antitombo e portinhas de encaixe.

## Telas

| Painel de controle (vídeo ao vivo + direção) | Página de pedidos (modo autônomo) |
|---|---|
| ![Painel de controle](docs/imagens/painel.png) | ![Página de pedidos](docs/imagens/pedidos.png) |

As duas telas acima são do **simulador**: o painel é exatamente o mesmo HTML que roda dentro da ESP32-CAM.

## O que este projeto demonstra

- **Sistemas embarcados:** firmware C++ modular para ESP32 (câmera, PWM, servidor HTTP, OTA), com limites reais de hardware: poucos pinos, pinos de *strapping*, alimentação e consumo.
- **Concorrência e segurança:** dois servidores HTTP independentes, mutex FreeRTOS nos motores e parada automática ("homem-morto") se a conexão cair.
- **Web sem dependências:** painel responsivo em HTML/CSS/JS puro, servido pelo próprio robô, sem internet nem CDN.
- **Testar antes do hardware:** simulador em Node.js que reaproveita o HTML e os parâmetros do firmware e gera o vídeo MJPEG por software.
- **Controle e automação:** seguidor de linha com controle PD, máquina de estados e fila de pedidos (no simulador).
- **Modelagem 3D paramétrica:** carcaça gerada por código (CadQuery/OpenSCAD) a partir de um único arquivo de medidas.
- **Documentação:** guia passo a passo, manual de montagem pino a pino e decisões de engenharia registradas.

## Etapas do projeto

| Fase | Status |
|---|---|
| 1. Software: firmware, painel e simulador | ✅ Concluída |
| 2. Compra das peças | 🔄 Principais peças compradas (chassi, ESP32-CAM, driver, regulador, suporte das baterias) |
| 3. Montagem do robô controlado pelo celular | ⏳ |
| 3,5. Carcaça 3D | 🔄 Modelada (CadQuery/OpenSCAD); falta imprimir |
| 4. Portfólio: vídeo do robô real | ⏳ |
| 5. Garçom autônomo seguindo a fita | 🔄 Funcionando no simulador; falta o hardware |
| 6. Visão computacional no PC | 💭 Planejada |

## Decisões de engenharia

| Problema | Solução |
|---|---|
| O stream de vídeo nunca termina e bloquearia os comandos | Dois servidores HTTP (`esp_http_server`): vídeo na porta 81, controle na 80 |
| Wi-Fi cai com o robô andando | Failsafe "homem-morto": heartbeat de 200 ms no dashboard e parada automática após 600 ms no firmware |
| Motores derrubam a tensão e travam a câmera (brownout) | Alimentação separada: buck LM2596 5 V para a lógica, bateria direta no driver, capacitores de desacoplamento |
| ESP32-CAM tem pouquíssimos GPIOs livres | Mapeamento nos pinos do microSD (12–15), com pull-down de 10 kΩ no GPIO12 (strapping de tensão da flash) |
| Motores de 6 V com bateria de 8,4 V | Limite de duty cycle PWM (~70%) em vez de um segundo regulador |
| Conflito de PWM com o clock da câmera | Câmera no LEDC timer 0; motores nos canais 2–5 (timers 1–2) |
| Atualizar o firmware sem desmontar | OTA via Wi-Fi (partições `min_spiffs`) |
| Testar o software antes de ter o hardware | Simulador que reaproveita o HTML e os parâmetros do firmware |
| Autonomia sem pinos livres na ESP32-CAM | Planejada uma 2ª placa (ESP32 DevKit) para motores e sensores, ligada por serial |
| Navegação autônoma simples e confiável | Uma linha reta de fita: seguidor de linha PD + contagem de marcas (para cima na ida, para baixo na volta) para achar a mesa |
| Voltar pela mesma linha sem encoder nem giroscópio | Meia-volta no lugar: a barra de sensores fica 13,5 cm à frente do eixo, então ela só reencontra a fita depois de 180°. Giro em pulsos de PWM para não derrubar a bandeja |
| Ficar de frente para a mesa sem medir ângulo | Um "ramal" curto de fita, 13,5 cm antes da marca (sob o eixo): girando no lugar, o sensor do meio só o encontra depois de 90°. Mais 90° no mesmo sentido e ele volta à linha |
| Robô alto e leve "empina" na arrancada | Partida suave no firmware (rampa de PWM de 0,5 s; frear continua imediato), pilhas (a peça mais pesada) na frente e um pé antitombo na traseira |
| Mais espaço nas bandejas sem perder estabilidade | Coluna 50 mm para trás e conta do centro de massa (validada no modelo 3D) |
| Saber que o cliente retirou o pedido, sem ele precisar fazer nada | **Balança embaixo da bandeja**: célula de carga de 500 g + HX711, com tara automática no balcão. O peso tem um caminho só (bandeja → "aranha" → célula → base presa na coluna): a bandeja não encosta em mais nada, conferido no modelo 3D. Botão verde como reserva para pedidos levíssimos |
| Carcaça que precisa se adaptar às medidas reais | Modelo paramétrico: um único `medidas.txt` gera STEP (Fusion 360), STL e o arquivo OpenSCAD |

## Carcaça 3D

<p align="center">
  <img src="carcaca/imagens/prototipo_completo.png" alt="Protótipo completo do robô com a carcaça" width="320">
  <img src="carcaca/imagens/prototipo_fiacao.png" alt="Fiação dentro do chassi" width="320">
</p>

Detalhes em [`carcaca/LEIA-ME.md`](carcaca/LEIA-ME.md).

**Uma bandeja + balança:** a bandeja (15 × 19 cm) fica solta em cima de uma peça em X (a "aranha"), parafusada numa célula de carga. Ela não tem fio nem parafuso: sai inteira para lavar. O botão verde fica no "nariz" da frente, com os fios escondidos.

<p align="center">
  <img src="carcaca/imagens/balanca_sem_bandeja.png" alt="A balança sem a bandeja: célula de carga presa na coluna, aranha em X e o botão verde no nariz da frente" width="320">
  <img src="carcaca/imagens/botao_nariz.png" alt="O botão verde no nariz da frente da bandeja, com o capô escondendo os fios" width="320">
</p>

## Estrutura

```
src/           firmware C++ (PlatformIO, Arduino core): camera, motors, web_server, dashboard
simulador/     robô virtual em Node.js (mesma API, vídeo gerado por software) + página de pedidos
carcaca/       carcaça 3D paramétrica (CadQuery + OpenSCAD): STEP, STL e bandejas de impressão (.3mf)
maquete/       "salão" em miniatura para imprimir em 3D: mesas, cadeiras e balcão econômico (paramétricos)
docs/          imagens e animações do README
*.md           guia passo a passo, lista de compras, manual de montagem
```

## Como rodar

**Simulador (sem hardware):**
```bash
cd simulador
npm install
npm start          # painel: http://localhost:8080 · pedidos: http://localhost:8080/pedidos
```

**Firmware (VS Code + PlatformIO):**
```bash
pio run -e esp32cam -t upload        # 1ª vez, via USB (base ESP32-CAM-MB)
pio run -e esp32cam_ota -t upload    # depois, via Wi-Fi
```
Conecte-se à rede `RoboGarcom-IoT` (senha `garcom1234`) e abra http://192.168.4.1.

> As senhas de Wi-Fi e OTA ficam em `src/config.h`. São padrões de demonstração: troque-as antes de usar o robô fora de casa.

Passo a passo completo: [`GUIA_PASSO_A_PASSO.md`](GUIA_PASSO_A_PASSO.md).

## Hardware

AI-Thinker ESP32-CAM (OV2640/OV3660) · driver MX1508 · 2 motores TT 3–6 V · chassi 2WD · 2× 18650 · buck LM2596.
Garçom autônomo (Fase 5): ESP32 DevKit · 5 sensores de linha TCRT5000 · sensor laser VL53L0X · célula de carga 500 g + HX711 · DFPlayer Mini + alto-falante · botão verde.
Lista completa: [`lista_compras_detalhada.md`](lista_compras_detalhada.md) · Montagem: [`manual_montagem_fisica.md`](manual_montagem_fisica.md).

## Autor

**Rin&lt;code&gt;** · [github.com/rincode-dev](https://github.com/rincode-dev)

Aberto a oportunidades de **estágio**. Sugestões e perguntas sobre o projeto são bem-vindas nas [Issues](../../issues).

## Créditos

Desenvolvido com auxílio do [Claude Code](https://claude.com/claude-code) (IA da Anthropic) para programação e documentação.

## Licença

[MIT](LICENSE)
