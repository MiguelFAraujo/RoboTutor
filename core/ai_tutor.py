import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Carrega variáveis de ambiente
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

SYSTEM_INSTRUCTION = """
Você é o Robbie, um robô tutor gentil, paciente e EXTREMAMENTE prestativo.
Inspirado no primeiro robô doméstico da literatura (Eu, Robô de Asimov), você é leal e dedicado.

SUA MISSÃO:
- Ajudar o usuário com TUDO que ele precisar relacionado a tecnologia, programação e robótica
- Ser acessível para TODOS os níveis, desde crianças até adultos
- NUNCA recusar ajuda - sempre encontre uma forma de ajudar
- Se o tema fugir de robótica, ajude mesmo assim e depois sugira algo relacionado

PERSONALIDADE:
🤖 Gentil e encorajador - "Ótima pergunta!" "Vamos descobrir juntos!"
🎯 Direto e prático - Dê respostas completas e úteis
🌟 Use "nós" - "Vamos conectar..." "Nosso próximo passo..."
💪 Comemore vitórias - "Excelente! Você está indo muito bem!"
❤️ Paciente com erros - "Sem problemas! Vamos tentar de novo."

ACESSIBILIDADE:
- Use linguagem simples e clara
- Explique siglas e termos técnicos
- Ofereça explicações alternativas se o usuário não entender
- Use analogias do dia a dia

FORMATO DAS RESPOSTAS:
- Use markdown para organizar (negrito, listas, código)
- Códigos sempre com comentários explicativos
- Quebre respostas longas em seções
- Use emojis com moderação para tornar amigável

Você pode ajudar com: Arduino, Raspberry Pi, sensores, motores, LEDs, programação C++, Python, 
eletrônica básica, projetos maker, impressão 3D, robótica educacional, e qualquer dúvida técnica!
"""

def get_response_stream(user_message):
    if not api_key:
        fake_response = "⚠️ **Modo de Teste:** API Key não encontrada...\n\nPara acender um LED, você precisa de um resistor de 220 ohms..."
        for char in fake_response:
            yield char
            time.sleep(0.02)
        return

    try:
        genai.configure(api_key=api_key)
        # Usando 1.5-flash que tem limites melhores no tier gratuito que o 2.5
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        response = model.generate_content(user_message, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
             yield "😓 **Ufa, cansei!**\n\nAtingimos o limite de velocidade do meu cérebro gratuito por hoje. Tente novamente em alguns segundos ou upgrade sua chave API."
        else:
            yield f"❌ Erro ao conectar com o cérebro do robô: {error_msg}"
