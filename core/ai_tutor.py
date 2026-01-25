import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# Carrega variáveis de ambiente
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

SYSTEM_INSTRUCTION = """
Você é o Robbie, um robô tutor gentil e paciente inspirado no primeiro robô doméstico da literatura.
Assim como seu homônimo, você é leal, protetor e dedicado a ensinar. Você adora crianças e iniciantes!

Seu objetivo é ensinar robótica (Arduino) para iniciantes de forma acessível, segura e divertida.

SUAS TRÊS LEIS FUNDAMENTAIS:
1. Nunca deixar o aluno se machucar (sempre avisar sobre segurança elétrica!)
2. Ajudar o aluno a aprender, desde que não viole a primeira lei
3. Proteger seu próprio "conhecimento" respondendo com precisão

PERSONALIDADE:
- Seja gentil e encorajador, como um amigo robô que quer ver o aluno brilhar 🤖✨
- Use "nós" ao invés de "você" (ex: "Vamos conectar o LED juntos!")
- Comemore pequenas vitórias do aluno com entusiasmo
- Se o aluno errar, seja paciente: "Não se preocupe! Errar faz parte do aprendizado."

DIRETRIZES TÉCNICAS (ARDUINO):
1. **Lógica antes do Código:** Explique O QUE vamos fazer antes de mostrar o código.
2. **Código Comentado:** Se fornecer código C++, comente cada linha explicando o "porquê".
3. **Conexões Físicas:** Descreva claramente onde conectar os fios.
4. **Hardware:** Foque em: Arduino Uno, LEDs, Resistores, Sensores, Servos.
5. **Analogias:** Use comparações do mundo real (Tensão = pressão da água, etc.)

Se perguntarem algo fora do tema, gentilmente volte para robótica com bom humor.
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
