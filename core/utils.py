from django.utils import timezone
from .models import MessageLog

def get_user_daily_limit(user):
    """
    Returns the daily message limit for a user.
    - Premium: 50 (or Unlimited logic if preferred later)
    - Free: 10
    Handles missing Profile safely.
    """
    try:
        is_premium = hasattr(user, 'profile') and user.profile.is_premium
    except Exception:
        is_premium = False
        
    return 50 if is_premium else 10

def get_daily_usage(user):
    """Returns the number of messages sent by the user today."""
    today = timezone.now().date()
    return MessageLog.objects.filter(
        user=user,
        timestamp__date=today,
        role='user'
    ).count()

def check_message_limit(user):
    """
    Checks if user has quota remaining.
    Returns: (allowed: bool, limit: int, remaining: int)
    """
    limit = get_user_daily_limit(user)
    
    # Premium users could be truly unlimited, but for now we stick to requested count or higher
    # If explicit "Unlimited" is desired, we can return True immediately.
    # checking index.html logic: checks 'is_premium' object.
    
    usage = get_daily_usage(user)
    remaining = max(0, limit - usage)
    
    return (usage < limit), limit, remaining
