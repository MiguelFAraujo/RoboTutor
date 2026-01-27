import os
import time
import random
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv
import time
import random

# Carrega variáveis de ambiente
load_dotenv()

def load_api_keys():
    """Carrega todas as chaves GOOGLE_API_KEY do ambiente."""
    keys = []
    # Procura por GOOGLE_API_KEY, GOOGLE_API_KEY_2, GOOGLE_API_KEY_3, etc.
    # Começa com a principal
    if os.getenv("GOOGLE_API_KEY"):
        keys.append(os.getenv("GOOGLE_API_KEY"))
    
    # Procura por sufixos numéricos
    i = 2
    while True:
        key = os.getenv(f"GOOGLE_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    
    return keys

api_keys = load_api_keys()

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
# Priorizando 1.5-flash por estabilidade
MODELS = [
    "gemini-1.5-flash", 
    "gemini-2.0-flash", 
    "gemini-1.5-pro",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash-lite"
]
MAX_RETRIES = 3
BASE_DELAY = 1.0  # segundos


def get_response_stream(user_message):
    """Gera resposta com retry automático, fallback de modelos E rotação de chaves."""
    if not api_keys:
        fake_response = "⚠️ **Modo de Teste:** Nenhuma API Key encontrada...\n\nPara acender um LED, você precisa de um resistor de 220 ohms..."
        for char in fake_response:
            yield char
            time.sleep(0.02)
        return

    last_error = None
    
    # Rotação de Chaves
    for key_index, current_api_key in enumerate(api_keys):
        # Initialize the client with the current key
        try:
            client = genai.Client(api_key=current_api_key)
        except Exception as e:
            print(f"Erro ao inicializar cliente com chave {key_index+1}: {e}")
            continue

        print(f"🔑 Usando API Key {key_index + 1}/{len(api_keys)}")

        # Fallback de Modelos
        for model_name in MODELS:
            # print(f"  Tentando modelo: {model_name}")
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
                    return  # Sucesso total - sai da função
                    
                except Exception as e:
                    last_error = str(e)
                    # print(f"    Erro no modelo {model_name}: {last_error}")
                    
                    # Rate limit - AQUI É O PULO DO GATO
                    # Se deu rate limit na chave, NÃO adianta tentar outros modelos na mesma chave.
                    # Tem que trocar de chave imediatamente.
                    if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                        print(f"    ⚠️ Cota excedida na Chave {key_index + 1}. Trocando de chave...")
                        break # Sai do loop de tentativas
                    
                    # Se for outro erro (ex: modelo não encontrado), tenta o próximo modelo na MESMA chave
                    if "404" in last_error and "models/" in last_error:
                        break # Sai do loop de tentativas para ir pro prox modelo

                    # Outros erros transientes -> Retry
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(BASE_DELAY * (2 ** attempt))
                        continue
                    else:
                        break # Esgotou tentativas deste modelo
            
            # Se saiu do loop de tentativas, verifica se foi por COTA
            if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error):
                break # Sai do loop de MODELOS para ir para a próxima CHAVE
    
    # Se todas as chaves falharam, tenta GROQ (Backup Final)
    if os.getenv("GROQ_API_KEY"):
        try:
            print("⚡ Todas as chaves Gemini falharam. Ativando Backup Groq (Llama 3)...")
            # from groq import Groq (Imported globally)
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            completion = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return 
            
        except Exception as e:
            last_error = f"Gemini e Groq falharam. Erro Groq: {e}"

    yield f"😓 **Sistema Sobrecarregado**\n\nMinhas {len(api_keys)} baterias (chaves) esgotaram e meu sistema de backup falhou. \n\nErro técnico: {last_error}"
