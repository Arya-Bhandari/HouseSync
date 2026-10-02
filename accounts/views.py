from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Profile is automatically created by post_save signal
            messages.success(request, f"Account created for {user.username}! Please log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def home_view(request):
    return render(request, 'accounts/home.html')

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    is_admin = profile.is_admin or request.user.is_superuser

    members = []
    if is_admin:
        # Load all members and make sure each user has a profile record
        users = User.objects.all().order_by('id')
        for u in users:
            p, _ = UserProfile.objects.get_or_create(user=u)
            members.append({
                'user': u,
                'profile': p,
                'is_admin': p.is_admin or u.is_superuser,
                'is_self': u == request.user,
            })

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'is_admin': is_admin,
        'members': members,
    })

@login_required
@require_POST
def toggle_admin_status(request, user_id):
    next_url = request.POST.get('next') or 'profile'
    current_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not (current_profile.is_admin or request.user.is_superuser):
        messages.error(request, "Permission denied: Only household administrators can modify roles.")
        return redirect(next_url)

    target_user = get_object_or_404(User, id=user_id)
    target_profile, _ = UserProfile.objects.get_or_create(user=target_user)

    # Safety check: Prevent revoking admin from yourself if you are the only admin
    if target_user == request.user and (target_profile.is_admin or request.user.is_superuser):
        admin_count = UserProfile.objects.filter(is_admin=True).count()
        if admin_count <= 1:
            messages.error(request, "You cannot revoke your own admin rights because you are the only administrator.")
            return redirect(next_url)

    # Toggle admin status
    target_profile.is_admin = not target_profile.is_admin
    target_profile.save()

    new_role = "Administrator" if target_profile.is_admin else "Standard Member"
    messages.success(request, f"Updated role: {target_user.username} is now a {new_role}.")
    return redirect(next_url)

def logout_view(request):
    logout(request)
    return redirect('login')