from flask import Flask, render_template, request, jsonify

from tutor_ai import get_response_stream

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "Mensagem vazia"}), 400
    
    # Retorna um Response que consome o gerador
    return app.response_class(get_response_stream(user_input), mimetype='text/plain')

if __name__ == '__main__':
    print("🚀 RoboTutor iniciado! Acesse: http://127.0.0.1:5000")
    app.run(debug=True)
