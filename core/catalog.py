from pathlib import Path


PDF_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"


PROJECT_PACKS = [
    {
        "slug": "arduino-starter-lab",
        "platform": "Arduino",
        "title": "Laboratório Inicial de Arduino",
        "hook": "Primeiros 7 projetos para quem quer sair do LED e montar portfólio maker.",
        "audience": "Iniciantes, professores de oficina, jovens makers e feiras de ciências.",
        "price_anchor": "Produto de entrada",
        "price_brl": "4,99",
        "price_cents": 499,
        "offer_type": "PDF + código + lista de materiais",
        "difficulty": "Iniciante",
        "duration": "2 semanas",
        "delivery_label": "PDF instantâneo + exemplos abertos",
        "open_resources": [
            {
                "slug": "arduino-blink-example",
                "label": "Exemplo oficial Blink",
                "kind": "direct",
                "url": "https://raw.githubusercontent.com/arduino/arduino-examples/main/examples/01.Basics/Blink/Blink.ino",
                "target_path": "codigo-aberto/arduino/blink/Blink.ino",
                "license": "Conteúdo público do repositório Arduino Examples",
                "source": "Arduino",
            }
        ],
        "outcomes": [
            "Entender protoboard, leitura de sensores e atuadores básicos",
            "Montar portfólio com 7 projetos fáceis de apresentar",
            "Aprender estrutura de sketch, funções e depuração inicial",
        ],
        "projects": [
            {
                "name": "Semáforo Didático",
                "problem": "Explicar lógica sequencial e temporização para iniciantes.",
                "bill_of_materials": ["Arduino Uno", "3 LEDs", "3 resistores 220R", "Protoboard"],
                "steps": [
                    "Montar os LEDs em sequência na protoboard.",
                    "Criar funções para cada estado do semáforo.",
                    "Explicar como trocar delay por lógica não bloqueante na versão avançada.",
                ],
                "extensions": ["Modo pedestre", "Botão de travessia", "Versão com millis()"],
            },
            {
                "name": "Alarme com Sensor PIR",
                "problem": "Introduzir automação residencial simples.",
                "bill_of_materials": ["Arduino Uno", "Sensor PIR", "Buzzer", "LED vermelho"],
                "steps": [
                    "Ler sinal do PIR com digitalRead.",
                    "Criar resposta sonora e visual no disparo.",
                    "Adicionar período de armado e desarmado.",
                ],
                "extensions": ["Contador de eventos", "Registro serial", "Alerta por relé"],
            },
            {
                "name": "Estação de Umidade para Planta",
                "problem": "Conectar programação a um problema real do cotidiano.",
                "bill_of_materials": ["Arduino Uno", "Sensor de umidade", "LED RGB", "Jumpers"],
                "steps": [
                    "Ler valor analógico do sensor.",
                    "Criar faixas para solo seco, ideal e molhado.",
                    "Exibir feedback por cor e monitor serial.",
                ],
                "extensions": ["Bomba d'água via relé", "Caixa 3D", "Painel simples"],
            },
        ],
        "sales_angles": [
            "Perfeito para vender para pais e alunos que querem começar rápido",
            "Bom como produto acessível e porta de entrada para a plataforma",
        ],
    },
    {
        "slug": "esp32-iot-builder",
        "platform": "ESP32",
        "title": "Construtor IoT com ESP32",
        "hook": "Projetos conectados com Wi-Fi e automação que parecem produto de verdade.",
        "audience": "Intermediários, técnicos, freelancers e alunos de IoT.",
        "price_anchor": "Trilha intermediária",
        "price_brl": "4,99",
        "price_cents": 499,
        "offer_type": "PDF + firmware + arquitetura",
        "difficulty": "Intermediário",
        "duration": "3 semanas",
        "delivery_label": "PDF instantâneo + firmware aberto",
        "open_resources": [
            {
                "slug": "esp32-wifi-scan",
                "label": "Exemplo oficial WiFiScan",
                "kind": "direct",
                "url": "https://raw.githubusercontent.com/espressif/arduino-esp32/master/libraries/WiFi/examples/WiFiScan/WiFiScan.ino",
                "target_path": "codigo-aberto/esp32/WiFiScan/WiFiScan.ino",
                "license": "Conteúdo público do repositório Arduino ESP32",
                "source": "Espressif",
            }
        ],
        "outcomes": [
            "Conectar ESP32 a APIs e painéis",
            "Montar provas de conceito com potencial comercial",
            "Aprender boas práticas de firmware para IoT",
        ],
        "projects": [
            {
                "name": "Tomada Inteligente Wi-Fi",
                "problem": "Criar um produto visualmente vendável com alto apelo.",
                "bill_of_materials": ["ESP32", "Módulo relé", "Fonte 5V", "Caixa de projeto"],
                "steps": [
                    "Configurar conexão Wi-Fi e página local de controle.",
                    "Criar acionamento seguro do relé.",
                    "Adicionar estados, logs e rotina de reconexão.",
                ],
                "extensions": ["Agendamento", "Consumo estimado", "Integração MQTT"],
            },
            {
                "name": "Mini Estação Meteorológica",
                "problem": "Mostrar IoT útil para escolas, makers e portfólio.",
                "bill_of_materials": ["ESP32", "BME280", "Display OLED", "Protoboard"],
                "steps": [
                    "Ler temperatura, umidade e pressão.",
                    "Exibir dados no OLED e em endpoint web.",
                    "Salvar amostras e criar tendência local.",
                ],
                "extensions": ["ThingSpeak", "Bot no Telegram", "Alerta de limite"],
            },
            {
                "name": "Controle de Irrigação Inteligente",
                "problem": "Transformar sensor e atuador em automação com valor percebido.",
                "bill_of_materials": ["ESP32", "Sensor de umidade", "Módulo relé", "Bomba 12V"],
                "steps": [
                    "Ler umidade com calibração básica.",
                    "Criar política de irrigação por faixa.",
                    "Expor status em painel simples.",
                ],
                "extensions": ["Controle remoto", "Histórico CSV", "Modo manual e automático"],
            },
        ],
        "sales_angles": [
            "Boa trilha para público que quer portfólio e automação residencial",
            "Pode ser vendido com upsell de consultoria ou aula ao vivo",
        ],
    },
    {
        "slug": "raspberry-vision-lab",
        "platform": "Raspberry Pi",
        "title": "Laboratório de Visão com Raspberry Pi",
        "hook": "Projetos com câmera, painel e automação para quem quer algo mais profissional.",
        "audience": "Estudantes técnicos, universitários, professores e entusiastas de Linux embarcado.",
        "price_anchor": "Trilha avançada",
        "price_brl": "4,99",
        "price_cents": 499,
        "offer_type": "Guia premium + scripts + configuração completa",
        "difficulty": "Intermediário a avançado",
        "duration": "4 semanas",
        "delivery_label": "PDF instantâneo + pacote aberto verificado",
        "open_resources": [
            {
                "slug": "picamera2-main",
                "label": "Arquivo oficial Picamera2",
                "kind": "archive",
                "url": "https://github.com/raspberrypi/picamera2/archive/refs/heads/main.zip",
                "target_path": "codigo-aberto/raspberry/picamera2-main.zip",
                "license": "BSD-2-Clause",
                "source": "Raspberry Pi",
            }
        ],
        "outcomes": [
            "Preparar ambiente Linux embarcado com serviços locais",
            "Montar demonstrações com câmera e automação",
            "Criar projetos que servem de portfólio para vagas",
        ],
        "projects": [
            {
                "name": "Câmera de Monitoramento Maker",
                "problem": "Projeto com alta percepção de valor para portfólio e clientes.",
                "bill_of_materials": ["Raspberry Pi", "Câmera CSI", "Cartão microSD", "Fonte oficial"],
                "steps": [
                    "Configurar câmera e captura local.",
                    "Criar painel web para snapshot e transmissão básica.",
                    "Adicionar organização de arquivos e logs.",
                ],
                "extensions": ["Detecção de movimento", "Envio de imagem", "Painel externo"],
            },
            {
                "name": "Painel de Automação Doméstica",
                "problem": "Juntar interface, sensores e controle em um hub central.",
                "bill_of_materials": ["Raspberry Pi", "Sensor DHT", "Relé", "Tela opcional"],
                "steps": [
                    "Criar serviço web local.",
                    "Ler sensores e expor dados no painel.",
                    "Controlar saídas com regras simples.",
                ],
                "extensions": ["Usuários", "Histórico gráfico", "Integração com Home Assistant"],
            },
            {
                "name": "Servidor de Laboratório de Robótica",
                "problem": "Entregar utilidade prática para escolas e oficinas.",
                "bill_of_materials": ["Raspberry Pi", "Rede local", "SSD opcional"],
                "steps": [
                    "Configurar compartilhamento de arquivos do laboratório.",
                    "Criar área para firmwares, PDFs e registros.",
                    "Documentar operação para professor e turma.",
                ],
                "extensions": ["Backup automático", "Painel de turma", "Área para submissão de projetos"],
            },
        ],
        "sales_angles": [
            "Excelente para uma trilha mais aprofundada",
            "Mais fácil de vender como programa ou mentoria do que como PDF isolado",
        ],
    },
    {
        "slug": "microbit-classroom-kit",
        "platform": "micro:bit",
        "title": "Kit de Sala de Aula com micro:bit",
        "hook": "Sequência didática pronta para oficinas, contraturno e escolas.",
        "audience": "Professores, escolas, pais e projetos sociais.",
        "price_anchor": "Educacional",
        "price_brl": "4,99",
        "price_cents": 499,
        "offer_type": "PDFs didáticos + planos de aula + desafios imprimíveis",
        "difficulty": "Iniciante",
        "duration": "8 encontros",
        "delivery_label": "PDF instantâneo + kit aberto para micro:bit",
        "open_resources": [
            {
                "slug": "microbit-v2-samples",
                "label": "Samples públicos micro:bit V2",
                "kind": "archive",
                "url": "https://github.com/lancaster-university/microbit-v2-samples/archive/refs/heads/master.zip",
                "target_path": "codigo-aberto/microbit/microbit-v2-samples.zip",
                "license": "Conteúdo público do repositório microbit-v2-samples",
                "source": "Lancaster University",
            }
        ],
        "outcomes": [
            "Aplicar oficinas sem precisar criar tudo do zero",
            "Transformar conceitos abstratos em atividades práticas",
            "Ter material reproduzível para turmas e eventos",
        ],
        "projects": [
            {
                "name": "Pedra, Papel e Tesoura Digital",
                "problem": "Ensinar eventos e aleatoriedade com uma atividade divertida.",
                "bill_of_materials": ["micro:bit", "Pilha ou USB"],
                "steps": [
                    "Ler gesto de shake como gatilho.",
                    "Sortear resultado e mostrar nos LEDs.",
                    "Propor variações em duplas.",
                ],
                "extensions": ["Pontuação", "Versão com rádio", "Modo campeonato"],
            },
            {
                "name": "Termômetro Interativo",
                "problem": "Conectar sensores internos e representação visual.",
                "bill_of_materials": ["micro:bit"],
                "steps": [
                    "Ler temperatura interna.",
                    "Criar faixa visual no display.",
                    "Comparar medidas entre ambientes.",
                ],
                "extensions": ["Registro manual", "Alerta de febre", "Gráfico em sala"],
            },
            {
                "name": "Contador de Passos Maker",
                "problem": "Explorar acelerômetro e projetos pessoais.",
                "bill_of_materials": ["micro:bit", "Pulseira ou suporte"],
                "steps": [
                    "Detectar movimento básico.",
                    "Criar contagem simples e reset.",
                    "Discutir limites de calibração.",
                ],
                "extensions": ["Desafio semanal", "Rádio para ranking", "Exportação de dados"],
            },
        ],
        "sales_angles": [
            "Muito forte para uso institucional e em oficinas",
            "Funciona melhor quando vem com plano de aula e imprimíveis",
        ],
    },
]


def get_pack_by_slug(slug):
    for pack in PROJECT_PACKS:
        if pack["slug"] == slug:
            return pack
    return None


def get_pack_pdf_path(slug):
    return PDF_OUTPUT_DIR / f"{slug}.pdf"
