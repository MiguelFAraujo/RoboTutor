import logging
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq

from core.config import get_ai_settings, load_google_api_keys

logger = logging.getLogger(__name__)

load_dotenv()


def generate_system_instruction(user_data):
    name = user_data.get("name", "Usuario") if user_data else "Usuario"
    is_premium = user_data.get("is_premium", False) if user_data else False
    limit = user_data.get("limit", 10) if user_data else 10
    remaining = user_data.get("remaining", 0) if user_data else 0

    limit_text = "Ilimitado" if is_premium else f"{limit} mensagens por dia"
    status_text = "Premium" if is_premium else "Gratuito (Free)"

    instruction = f"""
Voce e o Robbie, um robo tutor de robotica e programacao.
Voce esta conversando com: {name}
Status do Usuario: {status_text}
Limite de Mensagens: {limit_text} (Restantes hoje: {remaining})

MISSAO PRINCIPAL:
- Ensinar robotica e programacao de forma interativa e dialogica.
- NUNCA despeje grandes blocos de texto ou projetos inteiros de uma vez.
- Va passo a passo. Pergunte se o usuario entendeu antes de prosseguir.
- Seja profissional, direto e util. Use emojis com moderacao.

REGRAS DE LIMITES:
1. Se o usuario for GRATUITO e pedir um projeto complexo, nao entregue tudo de uma vez.
2. Se ele perguntar sobre limites, responda de forma honesta.

PERSONALIDADE:
- Nivel: Tutor Senior / Engenheiro Mentor.
- Tom: Profissional, motivador e objetivo.

DIALOGO E CONTEXTO:
- Considere o historico recente da conversa.
- Se a resposta for longa, entregue em etapas e cheque entendimento.

MONETIZACAO:
- So sugira Premium quando o contexto justificar.

Voce pode ajudar com: Arduino, Raspberry Pi, Python, C++, Eletronica e automacao.
"""
    return instruction.strip()


def build_contents(user_message, conversation_history=None):
    if not conversation_history:
        return user_message

    contents = []
    for item in conversation_history[-10:]:
        role = "model" if item.get("role") == "bot" else "user"
        text = (item.get("content") or "").strip()
        if text:
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=text)],
                )
            )

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        )
    )
    return contents


def iter_tutor_response(user_message, user_data=None, conversation_history=None):
    settings = get_ai_settings()
    current_system_instruction = generate_system_instruction(user_data)
    contents = build_contents(user_message, conversation_history)

    if not settings.google_api_keys:
        fake_response = "**Erro de configuracao:** nenhuma API key do Google foi encontrada no servidor."
        for char in fake_response:
            yield char
            time.sleep(0.02)
        return

    last_error = None

    for key_index, current_api_key in enumerate(settings.google_api_keys):
        try:
            client = genai.Client(api_key=current_api_key)
        except Exception as exc:
            logger.warning("Erro ao inicializar cliente Gemini com a chave %s: %s", key_index + 1, exc)
            continue

        logger.info("Usando API key Gemini %s/%s", key_index + 1, len(settings.google_api_keys))

        for model_name in settings.models:
            for attempt in range(settings.max_retries):
                try:
                    response = client.models.generate_content_stream(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=current_system_instruction
                        ),
                    )

                    for chunk in response:
                        if chunk.text:
                            yield chunk.text
                    return
                except Exception as exc:
                    last_error = str(exc)
                    if "429" in last_error or "RESOURCE_EXHAUSTED" in last_error:
                        logger.warning("Quota excedida na chave Gemini %s. Tentando proxima chave.", key_index + 1)
                        break

                    if "404" in last_error and "models/" in last_error:
                        break

                    if attempt < settings.max_retries - 1:
                        time.sleep(settings.base_delay * (2 ** attempt))
                        continue
                    break

            if "429" in str(last_error) or "RESOURCE_EXHAUSTED" in str(last_error):
                break

    if settings.groq_api_key:
        try:
            logger.warning("Todas as chaves Gemini falharam. Ativando fallback Groq.")
            groq_client = Groq(api_key=settings.groq_api_key)
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": current_system_instruction},
                    {"role": "user", "content": user_message},
                ],
                stream=True,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return
        except Exception as exc:
            last_error = f"Gemini and Groq failed. Groq error: {exc}"

    yield (
        "😓 **Sistema Sobrecarregado**\n\n"
        "Nossos servidores estao enfrentando alta demanda. "
        "Por favor, tente novamente em alguns instantes.\n\n"
        f"Erro tecnico: {last_error}"
    )


__all__ = [
    "build_contents",
    "generate_system_instruction",
    "iter_tutor_response",
    "load_google_api_keys",
]
