from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AISettings:
    google_api_keys: list[str]
    groq_api_key: str | None
    models: list[str]
    max_retries: int = 3
    base_delay: float = 1.0


@dataclass(frozen=True)
class BillingSettings:
    stripe_secret_key: str | None
    stripe_price_id: str | None
    stripe_webhook_secret: str | None
    domain: str | None


def load_google_api_keys():
    keys = []
    primary_key = os.getenv("GOOGLE_API_KEY")
    if primary_key:
        keys.append(primary_key)

    index = 2
    while True:
        key = os.getenv(f"GOOGLE_API_KEY_{index}")
        if not key:
            break
        keys.append(key)
        index += 1

    return keys


def get_ai_settings():
    return AISettings(
        google_api_keys=load_google_api_keys(),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        models=[
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-flash-latest",
        ],
    )


def get_billing_settings():
    return BillingSettings(
        stripe_secret_key=os.getenv("STRIPE_SECRET_KEY"),
        stripe_price_id=os.getenv("STRIPE_PRICE_ID"),
        stripe_webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET"),
        domain=os.getenv("DOMAIN"),
    )
