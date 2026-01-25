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
from .models import MessageLog, Conversation
from .ai_tutor import get_response_stream

@login_required
def index(request):
    # Tiered Limit Logic
    today = timezone.now().date()
    usage_count = MessageLog.objects.filter(
        user=request.user,
        timestamp__date=today,
        role='user' # Count only user messages
    ).count()
    
    LIMIT = 50 if getattr(request.user, 'profile', None) and request.user.profile.is_premium else 10
    remaining = max(0, LIMIT - usage_count)
    is_premium = getattr(request.user, 'profile', None) and request.user.profile.is_premium
    
    # Conversations for Sidebar
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'core/index.html', {
        'remaining': remaining,
        'limit': LIMIT,
        'is_premium': is_premium,
        'user': request.user,
        'conversations': conversations
    })

@csrf_exempt # Simplification for fetch API, ideally use CSRF token in JS
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
            
            # Limites
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
                # Create title from first 30 chars
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

            # Stream Response
            return StreamingHttpResponse(
                get_response_stream(user_message), 
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

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
