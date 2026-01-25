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

def get_response(user_message):
    if not api_key:
        return "⚠️ **Modo de Teste:** API Key não encontrada. Configure o arquivo .env para falar com o Miguel AI real! <br><br> *Resposta simulada:* Para acender um LED, você precisa de um resistor de 220 ohms para limitar a corrente..."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        # Aqui poderíamos manter histórico, mas para simplificar vamos stateless por enquanto
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"❌ Erro ao conectar com o cérebro do robô: {str(e)}"
