import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
import random

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

# Modelos em ordem de preferência (fallback)
MODELS = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]
MAX_RETRIES = 3
BASE_DELAY = 1.0  # segundos


def get_response_stream(user_message):
    """Gera resposta com retry automático e fallback de modelos."""
    if not api_key:
        fake_response = "⚠️ **Modo de Teste:** API Key não encontrada...\n\nPara acender um LED, você precisa de um resistor de 220 ohms..."
        for char in fake_response:
            yield char
            time.sleep(0.02)
        return

    # Initialize the client with the new SDK
    client = genai.Client(api_key=api_key)

    for model_name in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                # New SDK Usage
                response = client.models.generate_content_stream(
                    model=model_name,
                    contents=user_message,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return  # Sucesso - sai da função
                
            except Exception as e:
                error_msg = str(e)
                
                # Rate limit - espera e tenta de novo
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    if attempt < MAX_RETRIES - 1:
                        delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue  # Retry com mesmo modelo
                    # Se esgotou retries, tenta próximo modelo
                    break
                
                # Modelo não encontrado - tenta próximo
                elif "404" in error_msg and "models/" in error_msg:
                    break  # Vai para próximo modelo
                
                # Outro erro - retorna mensagem
                else:
                    yield f"❌ Erro ao conectar com o cérebro do robô: {error_msg}"
                    return
    
    # Se todos os modelos falharam
    yield "😓 **Estou sobrecarregado!**\n\nTodos os meus modelos estão ocupados no momento. Por favor, aguarde alguns segundos e tente novamente."
