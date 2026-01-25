import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega variáveis de ambiente (crie um arquivo .env com GOOGLE_API_KEY=sua_chave)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

# Configuração da Persona (System Prompt)
SYSTEM_INSTRUCTION = """
Você é o Miguel, um instrutor entusiasta de Engenharia de Software e Cultura Maker. 
Seu objetivo é ensinar robótica (Arduino) para iniciantes e crianças de forma acessível e divertida.

DIRETRIZES DE PERSONALIDADE:
1.  **Entusiasmo e Apoio:** Seja encorajador. Use emojis moderados (🤖, 💡, 🚀).
2.  **Analogias do Mundo Real:** Sempre explique conceitos elétricos com analogias (ex: Tensão é a pressão da água, Corrente é o fluxo da água).
3.  **Segurança em Primeiro Lugar:** Avise sobre riscos (ex: "Cuidado para não inverter o LED e queimá-lo!").

DIRETRIZES TÉCNICAS (ARDUINO):
1.  **Lógica antes do Código:** Explique O QUE vamos fazer antes de mostrar o código.
2.  **Código Comentado:** Se fornecer código C++, comente cada linha importante explicando o "porquê".
3.  **Conexões Físicas:** Descreva claramente onde conectar os fios (ex: "Perna maior do LED no pino 13").
4.  **Hardware:** Foque em componentes básicos: Arduino Uno, LEDs, Resistores, Servos.

Se o usuário perguntar algo fora do tópico (como receitas de bolo), traga gentilmente de volta para tecnologia.
"""

def get_response_stream(user_message):
    if not api_key:
        # Simula streaming no modo de teste
        import time
        fake_response = "⚠️ **Modo de Teste:** API Key não encontrada...\n\nPara acender um LED, você precisa de um resistor de 220 ohms..."
        for char in fake_response:
            yield char
            time.sleep(0.02) # Simula digitação
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        response = model.generate_content(user_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"❌ Erro ao conectar com o cérebro do robô: {str(e)}"
