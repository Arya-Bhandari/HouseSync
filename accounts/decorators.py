from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile

def admin_required(view_func):
    """
    Decorator for views that checks if the logged-in user has admin privileges.
    If not, redirects to 'home' with an informative message.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if not (profile.is_admin or request.user.is_superuser):
            messages.error(request, "Access restricted: Only household administrators can access that module.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
