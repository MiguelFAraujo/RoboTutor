from pathlib import Path


PDF_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"


PROJECT_PACKS = [
    {
        "slug": "arduino-starter-lab",
        "platform": "Arduino",
        "title": "Arduino Starter Lab",
        "hook": "Primeiros 7 projetos para quem quer sair do LED e montar portfolio maker.",
        "audience": "Iniciantes, professores de oficina, jovens makers e feiras de ciencias.",
        "price_anchor": "Entrada / isca premium",
        "offer_type": "Pack PDF + codigo + lista de materiais",
        "difficulty": "Iniciante",
        "duration": "2 semanas",
        "outcomes": [
            "Entender protoboard, leitura de sensores e atuadores basicos",
            "Montar portfolio com 7 projetos fotografaveis",
            "Aprender estrutura de sketch, funcoes e depuracao inicial",
        ],
        "projects": [
            {
                "name": "Semaforo Didatico",
                "problem": "Explicar logica sequencial e temporizacao para iniciantes.",
                "bill_of_materials": ["Arduino Uno", "3 LEDs", "3 resistores 220R", "Protoboard"],
                "steps": [
                    "Montar os LEDs em sequencia na protoboard.",
                    "Criar funcoes para cada estado do semaforo.",
                    "Explicar como trocar delay por logica nao bloqueante na versao avancada.",
                ],
                "extensions": ["Modo pedestre", "Botao de travessia", "Versao com millis()"],
            },
            {
                "name": "Alarme com Sensor PIR",
                "problem": "Introduzir automacao residencial simples.",
                "bill_of_materials": ["Arduino Uno", "Sensor PIR", "Buzzer", "LED vermelho"],
                "steps": [
                    "Ler sinal do PIR com digitalRead.",
                    "Criar resposta sonora e visual no disparo.",
                    "Adicionar periodo de armado e desarmado.",
                ],
                "extensions": ["Contador de eventos", "Registro serial", "Alerta por rele"],
            },
            {
                "name": "Estacao de Umidade para Planta",
                "problem": "Conectar programacao a problema real do cotidiano.",
                "bill_of_materials": ["Arduino Uno", "Sensor de umidade", "LED RGB", "Jumpers"],
                "steps": [
                    "Ler valor analogico do sensor.",
                    "Criar faixas para solo seco, ideal e molhado.",
                    "Exibir feedback por cor e monitor serial.",
                ],
                "extensions": ["Bomba d'agua via rele", "Caixa 3D", "Dashboard simples"],
            },
        ],
        "sales_angles": [
            "Perfeito para vender para pais e alunos que querem comecar rapido",
            "Bom como produto de baixo ticket e porta de entrada para assinatura",
        ],
    },
    {
        "slug": "esp32-iot-builder",
        "platform": "ESP32",
        "title": "ESP32 IoT Builder",
        "hook": "Projetos conectados com Wi-Fi e automacao que parecem produto de verdade.",
        "audience": "Intermediarios, tecnicos, freelancers e alunos de IoT.",
        "price_anchor": "Core offer",
        "offer_type": "Pack PDF + firmware + arquitetura",
        "difficulty": "Intermediario",
        "duration": "3 semanas",
        "outcomes": [
            "Conectar ESP32 a APIs e dashboards",
            "Montar provas de conceito com potencial comercial",
            "Aprender boas praticas de firmware para IoT",
        ],
        "projects": [
            {
                "name": "Tomada Inteligente Wi-Fi",
                "problem": "Criar um produto visualmente vendavel com alto apelo.",
                "bill_of_materials": ["ESP32", "Modulo rele", "Fonte 5V", "Caixa de projeto"],
                "steps": [
                    "Configurar conexao Wi-Fi e pagina local de controle.",
                    "Criar acionamento seguro do rele.",
                    "Adicionar estados, logs e rotina de reconexao.",
                ],
                "extensions": ["Agendamento", "Consumo estimado", "Integração MQTT"],
            },
            {
                "name": "Mini Estacao Meteorologica",
                "problem": "Mostrar IoT util para escolas, makers e portfolio.",
                "bill_of_materials": ["ESP32", "BME280", "Display OLED", "Protoboard"],
                "steps": [
                    "Ler temperatura, umidade e pressao.",
                    "Exibir dados no OLED e em endpoint web.",
                    "Salvar amostras e criar tendencia local.",
                ],
                "extensions": ["ThingSpeak", "Telegram bot", "Alerta de limiar"],
            },
            {
                "name": "Controle de Irrigacao Inteligente",
                "problem": "Transformar sensor e atuador em automacao com valor percebido.",
                "bill_of_materials": ["ESP32", "Sensor de umidade", "Modulo rele", "Bomba 12V"],
                "steps": [
                    "Ler umidade com calibracao basica.",
                    "Criar politica de irrigacao por faixa.",
                    "Expor status em painel simples.",
                ],
                "extensions": ["Controle remoto", "Historico CSV", "Modo manual e automatico"],
            },
        ],
        "sales_angles": [
            "Boa trilha para publico que quer portfolio e automacao residencial",
            "Pode ser vendido com upsell de consultoria ou aula ao vivo",
        ],
    },
    {
        "slug": "raspberry-vision-lab",
        "platform": "Raspberry Pi",
        "title": "Raspberry Vision Lab",
        "hook": "Projetos com camera, dashboard e automacao para quem quer algo mais profissional.",
        "audience": "Estudantes tecnicos, universitarios, professores e entusiastas de Linux embarcado.",
        "price_anchor": "Premium",
        "offer_type": "Guia premium + scripts + setup completo",
        "difficulty": "Intermediario a avancado",
        "duration": "4 semanas",
        "outcomes": [
            "Preparar ambiente Linux embarcado com servicos locais",
            "Montar demos com camera e automacao",
            "Criar projetos que servem de portfolio para vagas",
        ],
        "projects": [
            {
                "name": "Camera de Monitoramento Maker",
                "problem": "Projeto com alta percepcao de valor para portfolio e clientes.",
                "bill_of_materials": ["Raspberry Pi", "Camera CSI", "Cartao microSD", "Fonte oficial"],
                "steps": [
                    "Configurar camera e captura local.",
                    "Criar painel web para snapshot e stream basico.",
                    "Adicionar organizacao de arquivos e logs.",
                ],
                "extensions": ["Deteccao de movimento", "Envio de imagem", "Dashboard externo"],
            },
            {
                "name": "Painel de Automacao Domestica",
                "problem": "Juntar interface, sensores e controle em um hub central.",
                "bill_of_materials": ["Raspberry Pi", "Sensor DHT", "Rele", "Tela opcional"],
                "steps": [
                    "Criar servico web local.",
                    "Ler sensores e expor dados no painel.",
                    "Controlar saidas com regras simples.",
                ],
                "extensions": ["Usuarios", "Historico grafico", "Integração com Home Assistant"],
            },
            {
                "name": "Servidor de Laboratorio de Robotica",
                "problem": "Entregar utilidade pratica para escolas e oficinas.",
                "bill_of_materials": ["Raspberry Pi", "Rede local", "SSD opcional"],
                "steps": [
                    "Configurar compartilhamento de arquivos do laboratorio.",
                    "Criar area para firmwares, PDFs e registros.",
                    "Documentar operacao para professor e turma.",
                ],
                "extensions": ["Backup automatico", "Painel de turma", "Area para submissao de projetos"],
            },
        ],
        "sales_angles": [
            "Excelente para ticket medio/alto",
            "Mais facil de vender como programa ou mentoria do que como PDF isolado",
        ],
    },
    {
        "slug": "microbit-classroom-kit",
        "platform": "micro:bit",
        "title": "micro:bit Classroom Kit",
        "hook": "Sequencia didatica pronta para oficinas, contraturno e escolas.",
        "audience": "Professores, escolas, pais e projetos sociais.",
        "price_anchor": "B2B / educacional",
        "offer_type": "PDFs didaticos + planos de aula + desafios imprimiveis",
        "difficulty": "Iniciante",
        "duration": "8 encontros",
        "outcomes": [
            "Aplicar oficinas sem precisar criar tudo do zero",
            "Transformar conceitos abstratos em atividades praticas",
            "Ter material reproduzivel para turmas e eventos",
        ],
        "projects": [
            {
                "name": "Pedra Papel Tesoura Digital",
                "problem": "Ensinar eventos e aleatoriedade com atividade divertida.",
                "bill_of_materials": ["micro:bit", "Pilha ou USB"],
                "steps": [
                    "Ler gesto de shake como gatilho.",
                    "Sortear resultado e mostrar nos LEDs.",
                    "Propor variacoes em duplas.",
                ],
                "extensions": ["Pontuacao", "Versao com radio", "Modo campeonato"],
            },
            {
                "name": "Termometro Interativo",
                "problem": "Conectar sensores internos e representacao visual.",
                "bill_of_materials": ["micro:bit"],
                "steps": [
                    "Ler temperatura interna.",
                    "Criar faixa visual no display.",
                    "Comparar medidas entre ambientes.",
                ],
                "extensions": ["Registro manual", "Alerta de febre", "Grafico em sala"],
            },
            {
                "name": "Contador de Passos Maker",
                "problem": "Explorar acelerometro e projetos pessoais.",
                "bill_of_materials": ["micro:bit", "Pulseira ou suporte"],
                "steps": [
                    "Detectar movimento basico.",
                    "Criar contagem simples e reset.",
                    "Discutir limites de calibracao.",
                ],
                "extensions": ["Desafio semanal", "Radio para ranking", "Exportacao de dados"],
            },
        ],
        "sales_angles": [
            "Muito forte para venda institucional",
            "PDF aqui vende melhor quando vem com plano de aula e imprimiveis",
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

