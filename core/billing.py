import stripe
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
DOMAIN = os.getenv("DOMAIN", "http://127.0.0.1:8000")

@login_required
def create_checkout_session(request):
    # Check if user has email
    if not request.user.email:
        return render(request, 'core/error.html', {
            'message': 'Você precisa ter um email cadastrado para assinar. Por favor, atualize seu perfil.',
            'error_code': 'EMAIL_REQUIRED'
        })
    
    try:
        price_id = os.getenv("STRIPE_PRICE_ID")
        if not price_id:
            return render(request, 'core/error.html', {
                'message': 'Sistema de pagamento não configurado. Entre em contato com o suporte.',
                'error_code': 'STRIPE_NOT_CONFIGURED'
            })
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=DOMAIN + '/chat/?success=true',
            cancel_url=DOMAIN + '/chat/?canceled=true',
            client_reference_id=str(request.user.id),
        )
        return redirect(checkout_session.url, code=303)
    except stripe.error.InvalidRequestError as e:
        return render(request, 'core/error.html', {
            'message': f'Erro no pagamento: {str(e.user_message or e)}',
            'error_code': 'STRIPE_ERROR'
        })
    except Exception as e:
        return render(request, 'core/error.html', {
            'message': 'Não foi possível iniciar o pagamento. Tente novamente mais tarde.',
            'error_code': 'PAYMENT_ERROR'
        })

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
