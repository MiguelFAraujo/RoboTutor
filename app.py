from flask import Flask, render_template, request, jsonify
from tutor_ai import get_response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "Mensagem vazia"}), 400
    
    # Chama a lógica do tutor_ai
    response = get_response(user_input)
    
    # Retorna formatado para o frontend (pode usar Markdown no futuro)
    return jsonify({"response": response})

if __name__ == '__main__':
    print("🚀 RoboTutor iniciado! Acesse: http://127.0.0.1:5000")
    app.run(debug=True)
