import stripe

from core.config import get_billing_settings


def get_domain(request):
    settings = get_billing_settings()
    return settings.domain or request.build_absolute_uri("/").rstrip("/")


def configure_stripe():
    settings = get_billing_settings()
    stripe.api_key = settings.stripe_secret_key
    return settings


def create_checkout_for_user(request, user):
    settings = configure_stripe()
    if not settings.stripe_price_id:
        raise ValueError("STRIPE_NOT_CONFIGURED")

    return stripe.checkout.Session.create(
        customer_email=user.email,
        payment_method_types=["card"],
        line_items=[
            {
                "price": settings.stripe_price_id,
                "quantity": 1,
            },
        ],
        mode="subscription",
        success_url=get_domain(request) + "/chat/?success=true",
        cancel_url=get_domain(request) + "/chat/?canceled=true",
        client_reference_id=str(user.id),
    )


def sync_subscription_status(user, *, is_premium, customer_id=None, subscription_id=None):
    profile = user.profile
    profile.is_premium = is_premium
    if customer_id is not None:
        profile.stripe_customer_id = customer_id
    if subscription_id is not None:
        profile.stripe_subscription_id = subscription_id
    profile.save()


def construct_stripe_event(payload, signature):
    settings = configure_stripe()
    if not signature or not settings.stripe_webhook_secret:
        raise ValueError("STRIPE_SIGNATURE_MISSING")

    return stripe.Webhook.construct_event(
        payload,
        signature,
        settings.stripe_webhook_secret,
    )


def apply_checkout_completed(event, user_model):
    session = event["data"]["object"]
    user_id = session.get("client_reference_id")
    if not user_id:
        return

    try:
        user = user_model.objects.get(id=user_id)
    except user_model.DoesNotExist:
        return

    sync_subscription_status(
        user,
        is_premium=True,
        customer_id=session.get("customer"),
        subscription_id=session.get("subscription"),
    )


def apply_subscription_deleted(event, user_model):
    subscription = event["data"]["object"]
    subscription_id = subscription.get("id")
    if not subscription_id:
        return

    try:
        user = user_model.objects.get(profile__stripe_subscription_id=subscription_id)
    except user_model.DoesNotExist:
        return

    sync_subscription_status(user, is_premium=False, subscription_id=subscription_id)


def handle_stripe_event(event, user_model):
    event_type = event.get("type")
    if event_type == "checkout.session.completed":
        apply_checkout_completed(event, user_model)
    elif event_type == "customer.subscription.deleted":
        apply_subscription_deleted(event, user_model)
