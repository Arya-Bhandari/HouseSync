from .models import UserProfile

def user_role(request):
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        is_admin = profile.is_admin or request.user.is_superuser
        return {
            'is_admin': is_admin,
            'user_profile': profile,
        }
    return {
        'is_admin': False,
        'user_profile': None,
    }
