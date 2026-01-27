import os
import sys
import django
import stripe
import time
import requests
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
DOMAIN = os.getenv("DOMAIN", "http://127.0.0.1:8000")

def simulate(user_email):
    print(f"Simulando pagamento para: {user_email}")
    
    if not STRIPE_WEBHOOK_SECRET:
        print("❌ ERRO: STRIPE_WEBHOOK_SECRET não encontrado no .env")
        return

    # Configura Django para acessar o banco de dados
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'robotutor_project.settings')
    try:
        django.setup()
        from django.contrib.auth.models import User
    except Exception as e:
        print(f"❌ Erro ao configurar Django: {e}")
        return
    
    try:
        user = User.objects.get(email=user_email)
        print(f"✅ Usuário encontrado: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print(f"❌ Erro: Usuário com email '{user_email}' não encontrado.")
        return

    # Cria o payload simulando o evento do Stripe
    payload_data = {
        "id": "evt_test_webhook_" + str(int(time.time())),
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(time.time()),
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_" + str(int(time.time())),
                "object": "checkout.session",
                "client_reference_id": str(user.id),
                "customer": "cus_test_fake_" + str(int(time.time())),
                "subscription": "sub_test_fake_" + str(int(time.time())),
                "payment_status": "paid",
                "status": "complete",
                "amount_total": 1999,
                "currency": "brl",
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {
            "id": "req_test_123",
            "idempotency_key": "key_test_123"
        }
    }
    
    payload_str = json.dumps(payload_data)
    
    # Gera a assinatura correta (HMAC-SHA256)
    timestamp = int(time.time())
    
    try:
        # Usa a biblioteca do stripe se disponível para garantir compatibilidade
        signature = stripe.webhook.Signature.compute_signature(
            timestamp,
            payload_str,
            STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print(f"❌ Erro ao gerar assinatura: {e}")
        return

    sig_header = f"t={timestamp},v1={signature}"
    
    url = f"{DOMAIN}/webhook/"
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": sig_header
    }
    
    print(f"📡 Enviando Webhook para: {url}")
    try:
        response = requests.post(url, data=payload_str, headers=headers)
        print(f"Resposta do Servidor: Código {response.status_code}")
        print(f"Conteúdo: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 SUCESSO! O pagamento foi simulado e o usuário deve ser PREMIUM agora.")
            # Verify directly
            user.profile.refresh_from_db()
            print(f"STATUS ATUAL NO BANCO: Premium = {user.profile.is_premium}")
        else:
            print("\n⚠️ FALHA: O servidor retornou erro.")
    except Exception as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("Verifique se o servidor está rodando (python manage.py runserver)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n Uso: python simulate_payment.py <email_do_usuario>")
        print(" Exemplo: python simulate_payment.py marianamanda@email.com")
    else:
        simulate(sys.argv[1])
