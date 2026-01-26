from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse, StreamingHttpResponse
import json
import os
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import MessageLog, Conversation, Project
from .ai_tutor import get_response_stream

def landing(request):
    # If user is logged in, go straight to chat
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'core/landing.html')

@login_required
def index(request):
    # Tiered Limit Logic
    today = timezone.now().date()
    usage_count = MessageLog.objects.filter(
        user=request.user,
        timestamp__date=today,
        role='user'
    ).count()
    
    LIMIT = 50 if getattr(request.user, 'profile', None) and request.user.profile.is_premium else 10
    remaining = max(0, LIMIT - usage_count)
    is_premium = getattr(request.user, 'profile', None) and request.user.profile.is_premium
    
    # Conversations for Sidebar
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    
    # Projects for Sidebar (with error handling for missing table)
    try:
        projects = list(Project.objects.filter(user=request.user))
    except Exception:
        projects = []

    return render(request, 'core/index.html', {
        'remaining': remaining,
        'limit': LIMIT,
        'is_premium': is_premium,
        'user': request.user,
        'conversations': conversations,
        'projects': projects
    })


def stream_and_save_response(user, conversation, user_message):
    """Generator that streams AI response and saves it when complete."""
    full_response = ""
    
    for chunk in get_response_stream(user_message):
        full_response += chunk
        yield chunk
    
    # Save bot response after streaming completes
    if full_response and conversation:
        MessageLog.objects.create(
            user=user,
            conversation=conversation,
            role='bot',
            content=full_response,
            content_length=len(full_response)
        )


@csrf_exempt
@login_required
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            conversation_id = data.get('conversation_id')
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)

            # Check Limit
            today = timezone.now().date()
            usage_count = MessageLog.objects.filter(
                user=request.user,
                timestamp__date=today,
                role='user'
            ).count()
            
            LIMIT = 50 if getattr(request.user, 'profile', None) and request.user.profile.is_premium else 10
            
            if usage_count >= LIMIT:
                 return JsonResponse({
                     "error": "LIMIT_REACHED", 
                     "response": f"🚫 **Limite Diário Atingido ({LIMIT}/{LIMIT})**"
                 }, status=403)

            # Get or Create Conversation
            conversation = None
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id, user=request.user)
                except Conversation.DoesNotExist:
                    pass
            
            if not conversation:
                title = (user_message[:30] + '..') if len(user_message) > 30 else user_message
                conversation = Conversation.objects.create(user=request.user, title=title)

            # Log User Message
            MessageLog.objects.create(
                user=request.user,
                conversation=conversation,
                role='user',
                content=user_message,
                content_length=len(user_message)
            )

            # Stream Response and save when complete
            return StreamingHttpResponse(
                stream_and_save_response(request.user, conversation, user_message), 
                content_type='text/plain',
                headers={'X-Conversation-Id': str(conversation.id)}
            )
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def get_conversation_history(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        messages = conversation.messages.order_by('timestamp').values('role', 'content')
        return JsonResponse({'messages': list(messages)})
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)

from .forms import CustomUserCreationForm

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

@csrf_exempt
@login_required
def delete_conversation(request, conversation_id):
    """Delete a conversation and all its messages."""
    if request.method == 'DELETE':
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
            conversation.delete()
            return JsonResponse({'success': True})
        except Conversation.DoesNotExist:
            return JsonResponse({'error': 'Conversation not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ============================================================================
# Project Collection Endpoints
# ============================================================================

@login_required
def projects_list(request):
    """List all user's projects."""
    try:
        projects = list(Project.objects.filter(user=request.user))
    except Exception:
        projects = []
    return render(request, 'core/projects.html', {
        'projects': projects,
        'user': request.user
    })

@csrf_exempt
@login_required
def create_project(request):
    """Create a new project from a conversation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', 'Meu Projeto')
            description = data.get('description', '')
            conversation_id = data.get('conversation_id')
            
            conversation = None
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id, user=request.user)
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
                'project_id': project.id,
                'message': 'Projeto salvo na sua coleção! 🎉'
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def update_project_status(request, project_id):
    """Update project status (complete, pause, etc)."""
    if request.method in ['POST', 'PATCH']:
        try:
            data = json.loads(request.body)
            status = data.get('status')
            
            if status not in ['in_progress', 'completed', 'paused']:
                return JsonResponse({'error': 'Invalid status'}, status=400)
            
            project = Project.objects.get(id=project_id, user=request.user)
            project.status = status
            project.save()
            
            return JsonResponse({'success': True, 'status': status})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def delete_project(request, project_id):
    """Delete a project from collection."""
    if request.method == 'DELETE':
        try:
            project = Project.objects.get(id=project_id, user=request.user)
            project.delete()
            return JsonResponse({'success': True})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
