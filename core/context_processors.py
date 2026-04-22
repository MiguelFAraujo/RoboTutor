from django.conf import settings
from django.urls import reverse


def auth_context(request):
    google_login_path = reverse("google_login_entry")
    google_login_url = (
        f"{settings.APP_BASE_URL}{google_login_path}"
        if settings.APP_BASE_URL
        else google_login_path
    )

    callback_url = ""
    if settings.APP_BASE_URL:
        callback_url = f"{settings.APP_BASE_URL}/accounts/google/login/callback/"

    return {
        "app_base_url": settings.APP_BASE_URL,
        "google_login_url": google_login_url,
        "google_oauth_callback_uri": callback_url,
    }
