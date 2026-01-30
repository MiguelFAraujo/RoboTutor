from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json

from .models import MessageLog, Conversation, Project
from .ai_tutor import get_response_stream
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


# ============================================================
# PAGES
# ============================================================

def landing(request):
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'core/landing.html')


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

def stream_and_save_response(user, conversation, user_message, user_data=None):
    full_response = ""

    for chunk in get_response_stream(user_message, user_data):
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


@csrf_exempt
@login_required(login_url='/accounts/login/')
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        conversation_id = data.get('conversation_id')

        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

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

        return StreamingHttpResponse(
            stream_and_save_response(
                request.user,
                conversation,
                user_message,
                user_data
            ),
            content_type='text/plain',
            headers={'X-Conversation-Id': str(conversation.id)}
        )

    except Exception as e:
        print(f"❌ Erro no chat_api: {e}")
        return JsonResponse({'error': str(e)}, status=500)


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
        return JsonResponse({'error': 'Conversation not found'}, status=404)


# ============================================================
# AUTH
# ============================================================

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# ============================================================
# CONVERSATIONS
# ============================================================

@csrf_exempt
@login_required(login_url='/accounts/login/')
def delete_conversation(request, conversation_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        conversation = Conversation.objects.get(
            id=conversation_id,
            user=request.user
        )
        conversation.delete()
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)


# ============================================================
# PROJECTS
# ============================================================

@login_required(login_url='/accounts/login/')
def projects_list(request):
    projects = list(Project.objects.filter(user=request.user))

    return render(request, 'core/projects.html', {
        'projects': projects,
        'user': request.user
    })


@csrf_exempt
@login_required(login_url='/accounts/login/')
def create_project(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
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


@csrf_exempt
@login_required(login_url='/accounts/login/')
def update_project_status(request, project_id):
    if request.method not in ['POST', 'PATCH']:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    data = json.loads(request.body)
    status = data.get('status')

    if status not in ['in_progress', 'completed', 'paused']:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    try:
        project = Project.objects.get(
            id=project_id,
            user=request.user
        )
        project.status = status
        project.save()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)


@csrf_exempt
@login_required(login_url='/accounts/login/')
def delete_project(request, project_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        project = Project.objects.get(
            id=project_id,
            user=request.user
        )
        project.delete()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
