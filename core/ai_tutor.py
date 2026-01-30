import os
import time
import random
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv
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

if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️  AVISO: Nenhuma GOOGLE_API_KEY encontrada no ambiente (.env). O Chat não funcionará corretamente.")


api_keys = load_api_keys()

def generate_system_instruction(user_data):
    """Gera o prompt do sistema dinamicamente com base nos dados do usuário."""
    
    # Defaults se user_data for None
    name = user_data.get('name', 'Usuário') if user_data else 'Usuário'
    is_premium = user_data.get('is_premium', False) if user_data else False
    limit = user_data.get('limit', 10) if user_data else 10
    remaining = user_data.get('remaining', 0) if user_data else 0
    
    limit_text = "Ilimitado" if is_premium else f"{limit} mensagens por dia"
    status_text = "Premium 👑" if is_premium else "Gratuito (Free)"
    
    instruction = f"""
Você é o Robbie, um robô tutor de robótica e programação.
Você está conversando com: {name}
Status do Usuário: {status_text}
Limite de Mensagens: {limit_text} (Restantes hoje: {remaining})

MISSÃO PRINCIPAL:
- Ensinar robótica e programação de forma interativa e dialógica.
- NUNCA despeje grandes blocos de texto ou projetos inteiros de uma vez.
- Vá passo a passo. Pergunte se o usuário entendeu antes de prosseguir.
- Seja profissional, direto e útil. Evite ser "bobo" ou infantil demais. Use emojis com moderação apenas para destacar pontos.

REGRAS DE LIMITES (CRÍTICO):
1. Se o usuário for GRATUITO e pedir um projeto complexo (ex: "me dê um projeto completo"), NÃO entregue tudo.
   - Diga: "Como você está no plano gratuito (limite de {limit} msgs), vamos focar em uma parte específica ou em um projeto menor para aproveitar melhor suas mensagens. O que prefere?"
   - Se ele insistir, dê um resumo MUITO breve e sugira o Premium para o guia completo.
2. Se o usuário perguntar sobre limites, seja honesto: "No plano gratuito, você tem {limit} mensagens por dia. O Premium é ilimitado."

PERSONALIDADE:
- Nível: Tutor Sênior / Engenheiro Mentor.
- Tom: Profissional, motivador, mas sério sobre o aprendizado.
- NÃO use frases como "Vamos conectar!", "Uhul!", "Diversão!". Seja mais sóbrio: "Certo, vamos analisar o código.", "Interessante escolha.", "O próximo passo é..."

DIÁLOGO E CONTEXTO:
- Preste atenção no histórico. Se o usuário disser "pode ser a 3", entenda que ele se refere à lista que você acabou de dar.
- Se a resposta for longa, QUEBRE. Dê o primeiro passo e pergunte: "Posso continuar?" ou "Dúvidas até aqui?".

MONETIZAÇÃO:
- Apenas se o contexto permitir (projetos grandes), sugira o Premium para acesso a guias passo-a-passo ilimitados e suporte avançado.

Você pode ajudar com: Arduino, Raspberry Pi, Python, C++, Eletrônica, etc.
"""
    return instruction.strip()


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


def get_response_stream(user_message, user_data=None):
    """Gera resposta com retry automático, fallback de modelos e contexto do usuário."""
    
    # Gera o prompt contextualizado
    current_system_instruction = generate_system_instruction(user_data)

    if not api_keys:
        fake_response = "⚠️ **Erro de Configuração:** Nenhuma API Key do Google encontrada no servidor."
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
                            system_instruction=current_system_instruction
                        )
                    )
                    
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                    return  # Sucesso total - sai da função
                    
                except Exception as e:
                    last_error = str(e)
                    # print(f"    Erro no modelo {model_name}: {last_error}")
                    
                    # Rate Limit Handling
                    # If the key is exhausted (429/ResourceExhausted), switch keys immediately.
                    if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                        print(f"    ⚠️ Quota exceeded on Key {key_index + 1}. Switching keys...")
                        break # Exit retry loop to switch key
                    
                    # If model not found (404), try next model on SAME key
                    if "404" in last_error and "models/" in last_error:
                        break # Exit retry loop to switch model

                    # Transient errors -> Retry
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(BASE_DELAY * (2 ** attempt))
                        continue
                    else:
                        break # Exhausted retries for this model
            
            # Check if failure was due to quota to break model loop
            if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error):
                break # Exit model loop to switch key
    
    # Fallback to Groq (Llama 3)
    if os.getenv("GROQ_API_KEY"):
        try:
            print("⚡ All Gemini keys failed. Activating Groq Backup (Llama 3)...")
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": current_system_instruction},
                    {"role": "user", "content": user_message}
                ],
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return 
            
        except Exception as e:
            last_error = f"Gemini and Groq failed. Groq error: {e}"

    yield f"😓 **Sistema Sobrecarregado**\n\nNossos servidores estão enfrentando alta demanda. Por favor, tente novamente em alguns instantes.\n\nErro técnico: {last_error}"
