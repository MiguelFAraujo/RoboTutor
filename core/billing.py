from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import stripe

from core.services.billing_service import create_checkout_for_user, construct_stripe_event, handle_stripe_event

@login_required
def create_checkout_session(request):
    # Check if user has email
    if not request.user.email:
        return render(request, 'core/error.html', {
            'message': 'Você precisa ter um email cadastrado para assinar. Por favor, atualize seu perfil.',
            'error_code': 'EMAIL_REQUIRED'
        })
    
    try:
        checkout_session = create_checkout_for_user(request, request.user)
        return redirect(checkout_session.url)
    except ValueError:
        return render(request, 'core/error.html', {
            'message': 'Sistema de pagamento não configurado. Entre em contato com o suporte.',
            'error_code': 'STRIPE_NOT_CONFIGURED'
        })
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
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = construct_stripe_event(payload, sig_header)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    handle_stripe_event(event, User)
    return HttpResponse(status=200)
