from pathlib import Path
import os
import dj_database_url
from urllib.parse import urlparse

# --------------------------------------------------
# BASE
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent


def _normalize_base_url(value):
    if not value:
        return ""
    return value.rstrip("/")


def _extract_host(url):
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return parsed.netloc or parsed.path


def _build_origin(url):
    if not url:
        return ""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return ""

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-local-key")

# --------------------------------------------------
# DEBUG
# --------------------------------------------------
DEBUG = os.getenv("VERCEL") != "1"

if not DEBUG and SECRET_KEY == "django-insecure-local-key":
    raise RuntimeError("SECRET_KEY precisa estar configurada em producao.")

# --------------------------------------------------
# HOSTS
# --------------------------------------------------
APP_BASE_URL = _normalize_base_url(
    os.getenv("APP_BASE_URL")
    or (
        f"https://{os.getenv('VERCEL_PROJECT_PRODUCTION_URL')}"
        if os.getenv("VERCEL_PROJECT_PRODUCTION_URL")
        else ""
    )
    or (
        f"https://{os.getenv('VERCEL_URL')}"
        if os.getenv("VERCEL_URL") and not DEBUG
        else ""
    )
)

APP_HOST = _extract_host(APP_BASE_URL)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "robo-tutor.vercel.app",
    ".vercel.app",
]

if APP_HOST and APP_HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(APP_HOST)

# --------------------------------------------------
# APPS
# --------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "core",
]

SITE_ID = 1

# --------------------------------------------------
# AUTH / ALLAUTH
# --------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth Configuration (Updated Format)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True

LOGIN_REDIRECT_URL = "/chat/"
LOGOUT_REDIRECT_URL = "/"

# Social Login Configuration
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = "core.adapters.CustomSocialAccountAdapter"

# ⚠️ NÃO force protocolo aqui
# O allauth resolve automaticamente
# ACCOUNT_DEFAULT_HTTP_PROTOCOL = ...

# --------------------------------------------------
# GOOGLE OAUTH
# --------------------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"prompt": "select_account"},
        "VERIFIED_EMAIL": True,
        # Credenciais diretamente no settings (não depende do banco)
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret": GOOGLE_CLIENT_SECRET,
            "key": "",
        },
    }
}


# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# --------------------------------------------------
# URLS / TEMPLATES
# --------------------------------------------------
ROOT_URLCONF = "robotutor_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.auth_context",
            ],
        },
    },
]

WSGI_APPLICATION = "robotutor_project.wsgi.application"

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------
# STATIC
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
GENERATED_PDF_DIR = BASE_DIR / "generated_pdfs"

# --------------------------------------------------
# I18N
# --------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# CSRF
# --------------------------------------------------
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8095",
    "http://localhost:8095",
    "https://robo-tutor.vercel.app",
]

APP_ORIGIN = _build_origin(APP_BASE_URL)
if APP_ORIGIN and APP_ORIGIN not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(APP_ORIGIN)

# --------------------------------------------------
# SECURITY (SÓ PRODUÇÃO)
# --------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

