from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
import json

from .catalog import PROJECT_PACKS, get_pack_by_slug, get_pack_pdf_path
from .models import MessageLog, Conversation, Project
from .ai_tutor import get_response_stream
from .services.catalog_service import get_catalog_overview, get_catalog_pack
from .utils import get_user_daily_limit, get_daily_usage, check_message_limit
from .forms import CustomUserCreationForm


# ============================================================
# HELPERS (CRÍTICO PRA NÃO DAR ERRO 500)
# ============================================================

def user_is_premium(user):
    try:
        return user.profile.is_premium
    except Exception:
        return False


def parse_json_body(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "JSON inválido"}, status=400)


# ============================================================
# PAGES
# ============================================================

def landing(request):
    overview = get_catalog_overview()
    context = {
        "catalog": overview["packs"],
        "platforms": overview["platforms"],
        "pack_count": overview["pack_count"],
    }
    if request.user.is_authenticated:
        context["go_to_app"] = True
    return render(request, 'core/landing.html', context)


@require_GET
def academy_catalog(request):
    overview = get_catalog_overview()
    return render(
        request,
        "core/academy.html",
        {
            "catalog": overview["packs"],
            "platforms": overview["platforms"],
            "pack_count": overview["pack_count"],
        },
    )


@require_GET
def academy_pack_detail(request, slug):
    pack = get_catalog_pack(slug)
    if not pack:
        return render(request, "core/error.html", {"message": "Trilha não encontrada.", "error_code": "PACK_NOT_FOUND"}, status=404)
    return render(request, "core/academy_detail.html", {"pack": pack})


@require_GET
def academy_pdf_download(request, slug):
    pack = get_pack_by_slug(slug)
    if not pack:
        return render(request, "core/error.html", {"message": "Trilha não encontrada.", "error_code": "PACK_NOT_FOUND"}, status=404)

    pdf_path = get_pack_pdf_path(slug)
    if not pdf_path.exists():
        return render(
            request,
            "core/error.html",
            {
                "message": "O PDF desta trilha ainda não foi gerado. Execute o comando de geração primeiro.",
                "error_code": "PDF_NOT_GENERATED",
            },
            status=404,
        )

    return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename=pdf_path.name)


@login_required(login_url='/accounts/login/')
def index(request):
    limit = get_user_daily_limit(request.user)
    usage = get_daily_usage(request.user)
    remaining = max(0, limit - usage)

    progress_percentage = int((remaining / limit) * 100) if limit > 0 else 100
    is_premium = user_is_premium(request.user)

    conversations = Conversation.objects.filter(
        user=request.user
    ).order_by('-created_at')

    projects = list(Project.objects.filter(user=request.user))

    return render(request, 'core/index.html', {
        'remaining': remaining,
        'limit': limit,
        'progress_percentage': progress_percentage,
        'is_premium': is_premium,
        'user': request.user,
        'conversations': conversations,
        'projects': projects
    })


# ============================================================
# CHAT
# ============================================================

def stream_and_save_response(user, conversation, user_message, user_data=None, conversation_history=None):
    full_response = ""

    for chunk in get_response_stream(user_message, user_data, conversation_history):
        full_response += chunk
        yield chunk

    if full_response and conversation:
        MessageLog.objects.create(
            user=user,
            conversation=conversation,
            role='bot',
            content=full_response,
            content_length=len(full_response)
        )


@require_POST
@login_required(login_url='/accounts/login/')
def chat_api(request):
    try:
        data, error_response = parse_json_body(request)
        if error_response:
            return error_response

        user_message = data.get('message')
        conversation_id = data.get('conversation_id')

        if not user_message:
            return JsonResponse({'error': 'Mensagem vazia'}, status=400)

        allowed, limit, remaining = check_message_limit(request.user)
        if not allowed:
            return JsonResponse({
                "error": "LIMIT_REACHED",
                "response": f"🚫 Limite diário atingido ({limit}/{limit})"
            }, status=403)

        conversation = None
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user=request.user
                )
            except Conversation.DoesNotExist:
                pass

        if not conversation:
            title = user_message[:30]
            conversation = Conversation.objects.create(
                user=request.user,
                title=title
            )

        MessageLog.objects.create(
            user=request.user,
            conversation=conversation,
            role='user',
            content=user_message,
            content_length=len(user_message)
        )

        user_data = {
            'name': request.user.first_name or request.user.username,
            'is_premium': user_is_premium(request.user),
            'limit': limit,
            'remaining': remaining
        }
        conversation_history = list(
            conversation.messages.order_by("timestamp").values("role", "content")
        )

        return StreamingHttpResponse(
            stream_and_save_response(
                request.user,
                conversation,
                user_message,
                user_data,
                conversation_history,
            ),
            content_type='text/plain',
            headers={'X-Conversation-Id': str(conversation.id)}
        )

    except Exception as e:
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@require_GET
@login_required(login_url='/accounts/login/')
def get_conversation_history(request, conversation_id):
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )
        messages = conversation.messages.order_by(
            'timestamp'
        ).values('role', 'content')
        return JsonResponse({'messages': list(messages)})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)


# ============================================================
# AUTH
# ============================================================

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('chat')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@require_GET
def google_login_entry(request):
    target = "/accounts/google/login/"
    if settings.APP_BASE_URL:
        target = f"{settings.APP_BASE_URL}{target}"

    params = {}
    next_url = request.GET.get("next")
    process = request.GET.get("process")

    if next_url:
        params["next"] = next_url
    if process:
        params["process"] = process

    if params:
        target = f"{target}?{urlencode(params)}"

    return redirect(target)


# ============================================================
# CONVERSATIONS
# ============================================================

@require_http_methods(["DELETE"])
@login_required(login_url='/accounts/login/')
def delete_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )
        conversation.delete()
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversa não encontrada'}, status=404)


# ============================================================
# PROJECTS
# ============================================================

@login_required(login_url='/accounts/login/')
def projects_list(request):
    projects = list(Project.objects.filter(user=request.user))
    overview = get_catalog_overview()

    return render(request, 'core/projects.html', {
        'projects': projects,
        'user': request.user,
        'catalog': overview["packs"],
    })


@require_POST
@login_required(login_url='/accounts/login/')
def create_project(request):
    data, error_response = parse_json_body(request)
    if error_response:
        return error_response

    title = data.get('title', 'Meu Projeto')
    description = data.get('description', '')
    conversation_id = data.get('conversation_id')

    conversation = None
    if conversation_id:
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except Conversation.DoesNotExist:
            pass

    project = Project.objects.create(
        user=request.user,
        conversation=conversation,
        title=title,
        description=description,
        status='in_progress'
    )

    return JsonResponse({
        'success': True,
        'project_id': project.id
    })


@require_http_methods(["POST", "PATCH"])
@login_required(login_url='/accounts/login/')
def update_project_status(request, project_id):
    data, error_response = parse_json_body(request)
    if error_response:
        return error_response

    status = data.get('status')

    if status not in ['in_progress', 'completed', 'paused']:
        return JsonResponse({'error': 'Status inválido'}, status=400)

    try:
        project = Project.objects.get(
            id=project_id,
            user=request.user
        )
        project.status = status
        project.save()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Projeto não encontrado'}, status=404)


@require_http_methods(["DELETE"])
@login_required(login_url='/accounts/login/')
def delete_project(request, project_id):
    try:
        project = Project.objects.get(
            id=project_id,
            user=request.user
        )
        project.delete()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Projeto não encontrado'}, status=404)
