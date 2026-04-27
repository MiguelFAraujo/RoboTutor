import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.utils import timezone

from core.catalog import get_pack_by_slug
from core.models import AuditEvent, CatalogOrder
from core.services.pdf_service import generate_single_pack


ALLOWED_RESOURCE_HOSTS = {
    "raw.githubusercontent.com",
    "github.com",
}


def get_delivery_dir():
    return Path(getattr(settings, "DELIVERY_BUNDLE_DIR", settings.BASE_DIR / "generated_bundles"))


def extract_request_context(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return ip_address, user_agent


def log_audit_event(event_type, *, order=None, user=None, severity="info", request=None, payload=None):
    ip_address = None
    user_agent = ""
    if request is not None:
        ip_address, user_agent = extract_request_context(request)
    elif order is not None:
        ip_address = order.purchaser_ip
        user_agent = order.user_agent

    return AuditEvent.objects.create(
        order=order,
        user=user or getattr(order, "user", None),
        event_type=event_type,
        severity=severity,
        ip_address=ip_address,
        user_agent=user_agent,
        payload=payload or {},
    )


def assess_order_risk(user, request, pack_slug):
    score = 0
    reasons = []
    ip_address, user_agent = extract_request_context(request)

    recent_window = timezone.now() - timezone.timedelta(minutes=30)
    recent_orders = CatalogOrder.objects.filter(user=user, created_at__gte=recent_window).count()
    if recent_orders >= 3:
        score += 25
        reasons.append("Muitas tentativas de compra em pouco tempo.")

    recent_ip_orders = CatalogOrder.objects.filter(
        purchaser_ip=ip_address,
        created_at__gte=recent_window,
    ).exclude(user=user).count()
    if ip_address and recent_ip_orders >= 3:
        score += 35
        reasons.append("Mesmo IP tentando comprar para contas diferentes.")

    recent_downloads = AuditEvent.objects.filter(
        event_type="bundle_downloaded",
        ip_address=ip_address,
        created_at__gte=recent_window,
    ).count()
    if ip_address and recent_downloads >= 5:
        score += 20
        reasons.append("Volume alto de downloads recentes no mesmo IP.")

    if not user.email:
        score += 50
        reasons.append("Usuario sem e-mail confirmado para entrega.")

    if "bot" in (user_agent or "").lower():
        score += 15
        reasons.append("User-Agent parece automatizado.")

    existing_paid = CatalogOrder.objects.filter(
        user=user,
        pack_slug=pack_slug,
        status__in=[CatalogOrder.STATUS_PAID, CatalogOrder.STATUS_FULFILLED],
    ).exists()
    if existing_paid:
        score += 10
        reasons.append("Usuario ja possui compra paga para este pack.")

    return score, reasons


def create_catalog_order(user, request, pack_slug):
    pack = get_pack_by_slug(pack_slug)
    if not pack:
        raise ValueError("PACK_NOT_FOUND")

    ip_address, user_agent = extract_request_context(request)
    risk_score, risk_reasons = assess_order_risk(user, request, pack_slug)

    status = CatalogOrder.STATUS_BLOCKED if risk_score >= 70 else CatalogOrder.STATUS_PENDING
    order = CatalogOrder.objects.create(
        user=user,
        pack_slug=pack_slug,
        pack_title=pack["title"],
        status=status,
        amount_cents=pack.get("price_cents", 0),
        currency="brl",
        customer_email=user.email or "",
        purchaser_ip=ip_address,
        user_agent=user_agent,
        risk_score=risk_score,
        risk_reasons=risk_reasons,
        source_snapshot={
            "pack_slug": pack["slug"],
            "pack_title": pack["title"],
            "open_resources": pack.get("open_resources", []),
            "delivery_label": pack.get("delivery_label"),
        },
    )
    log_audit_event(
        "order_created",
        order=order,
        request=request,
        severity="warning" if status == CatalogOrder.STATUS_BLOCKED else "info",
        payload={"risk_score": risk_score, "risk_reasons": risk_reasons},
    )
    return order


def mark_order_paid(order, *, stripe_session_id="", payment_intent_id=""):
    order.status = CatalogOrder.STATUS_PAID
    order.stripe_session_id = stripe_session_id or order.stripe_session_id
    order.stripe_payment_intent_id = payment_intent_id or order.stripe_payment_intent_id
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "stripe_session_id", "stripe_payment_intent_id", "paid_at", "updated_at"])
    log_audit_event("order_paid", order=order, payload={"stripe_session_id": order.stripe_session_id})
    return order


def user_has_pack_access(user, pack_slug):
    if not user.is_authenticated:
        return False
    if getattr(getattr(user, "profile", None), "is_premium", False):
        return True
    return CatalogOrder.objects.filter(
        user=user,
        pack_slug=pack_slug,
        status__in=[CatalogOrder.STATUS_PAID, CatalogOrder.STATUS_FULFILLED],
    ).exists()


def get_latest_access_order(user, pack_slug):
    return CatalogOrder.objects.filter(
        user=user,
        pack_slug=pack_slug,
        status__in=[CatalogOrder.STATUS_PAID, CatalogOrder.STATUS_FULFILLED],
    ).order_by("-paid_at", "-created_at").first()


def _safe_destination(base_dir, relative_path):
    destination = (base_dir / relative_path).resolve()
    base_resolved = base_dir.resolve()
    if not str(destination).startswith(str(base_resolved)):
        raise ValueError("TARGET_PATH_INVALID")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def _validate_resource_url(url):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in ALLOWED_RESOURCE_HOSTS:
        raise ValueError("RESOURCE_HOST_NOT_ALLOWED")


def fetch_open_resource(resource, base_dir):
    _validate_resource_url(resource["url"])
    destination = _safe_destination(base_dir, resource["target_path"])
    with urlopen(resource["url"], timeout=30) as remote_file, open(destination, "wb") as local_file:
        shutil.copyfileobj(remote_file, local_file)
    return destination


def write_bundle_manifest(order, bundle_dir):
    pack = get_pack_by_slug(order.pack_slug) or {}
    manifest = {
        "order_id": order.id,
        "pack_slug": order.pack_slug,
        "pack_title": order.pack_title,
        "generated_at": timezone.now().isoformat(),
        "pdf_file": f"{order.pack_slug}.pdf",
        "delivery_label": pack.get("delivery_label"),
        "open_resources": order.source_snapshot.get("open_resources", []),
        "license_notice": "Somente materiais com origem publica informada no manifesto foram empacotados.",
    }
    manifest_path = bundle_dir / "manifesto-entrega.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8")
    return manifest_path


def _build_bundle_archive(source_dir, destination_zip):
    with zipfile.ZipFile(destination_zip, "w", compression=zipfile.ZIP_DEFLATED) as bundle_zip:
        for path in source_dir.rglob("*"):
            if path.is_file():
                bundle_zip.write(path, path.relative_to(source_dir))


def _sha256_for_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_order_bundle(order):
    if order.status not in [CatalogOrder.STATUS_PAID, CatalogOrder.STATUS_FULFILLED]:
        raise ValueError("ORDER_NOT_PAID")

    current_bundle = Path(order.delivery_bundle_path) if order.delivery_bundle_path else None
    if current_bundle and current_bundle.exists():
        return current_bundle

    delivery_dir = get_delivery_dir()
    delivery_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pdf_path = generate_single_pack(order.pack_slug, temp_path)
        working_dir = temp_path / "bundle"
        working_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf_path, working_dir / pdf_path.name)

        for resource in order.source_snapshot.get("open_resources", []):
            fetch_open_resource(resource, working_dir)

        write_bundle_manifest(order, working_dir)

        zip_path = delivery_dir / f"pedido-{order.id}-{order.pack_slug}.zip"
        _build_bundle_archive(working_dir, zip_path)

    order.delivery_bundle_path = str(zip_path)
    order.delivery_checksum = _sha256_for_file(zip_path)
    order.status = CatalogOrder.STATUS_FULFILLED
    order.downloaded_at = timezone.now()
    order.save(update_fields=["delivery_bundle_path", "delivery_checksum", "status", "downloaded_at", "updated_at"])
    log_audit_event(
        "bundle_prepared",
        order=order,
        payload={"bundle_path": order.delivery_bundle_path, "checksum": order.delivery_checksum},
    )
    return zip_path
