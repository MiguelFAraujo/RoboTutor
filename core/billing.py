import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = "https://robotutor-miguel.onrender.com" # TODO: Make dynamic or ENV
# Local testing: "http://127.0.0.1:8000"

def create_checkout_session(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        # Preço Base: R$ 19,99 (Criar no Dashboard do Stripe e pegar o Price ID)
        # Para facilitar, vou criar o produto na hora se não existir (apenas exemplo)
        # Em produção, use o PRICE_ID fixo do seu dashboard.
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    # Price ID do seu plano de R$ 19,99
                    'price': os.getenv("STRIPE_PRICE_ID"), 
                    'quantity': 1,
                },
            ],
            mode='subscription',
            # Sem cupom para plano semanal
            success_url=DOMAIN + '/?success=true',
            cancel_url=DOMAIN + '/?canceled=true',
            client_reference_id=request.user.id,
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return JsonResponse({'error': str(e)})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Ativar Premium
        user_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                user.profile.is_premium = True
                user.profile.stripe_customer_id = stripe_customer_id
                user.profile.stripe_subscription_id = stripe_subscription_id
                user.profile.save()
                print(f"✅ Usuário {user.email} virou Premium!")
            except User.DoesNotExist:
                print("❌ Usuário não encontrado no webhook.")

    return HttpResponse(status=200)
