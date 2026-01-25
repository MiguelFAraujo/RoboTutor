import json
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import MessageLog
from .ai_tutor import get_response_stream

@login_required
def index(request):
    # Daily Limit Logic
    today = timezone.now().date()
    usage_count = MessageLog.objects.filter(
        user=request.user,
        timestamp__date=today
    ).count()
    
    LIMIT = 10
    remaining = max(0, LIMIT - usage_count)
    
    return render(request, 'core/index.html', {
        'remaining': remaining,
        'user': request.user
    })

@csrf_exempt # Simplification for fetch API, ideally use CSRF token in JS
@login_required
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)

            # Check Limit
            today = timezone.now().date()
            usage_count = MessageLog.objects.filter(
                user=request.user,
                timestamp__date=today
            ).count()
            
            if usage_count >= 10:
                 return JsonResponse({
                     "error": "LIMIT_REACHED", 
                     "response": "🚫 **Limite Diário Atingido!**\n\nVocê usou suas 10 mensagens gratuitas de hoje.\n\nAmanhã tem mais! 🌙"
                 }, status=403)

            # Log Message
            MessageLog.objects.create(
                user=request.user,
                content_length=len(user_message)
            )

            # Stream Response
            return StreamingHttpResponse(
                get_response_stream(user_message), 
                content_type='text/plain'
            )
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

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
