from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(
        default=False,
        help_text="Designates whether this user has household admin privileges."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        role = "Admin" if self.is_admin else "Member"
        return f"{self.user.username} ({role})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # If this is the very first user in the system, grant admin status by default
        is_first_user = User.objects.count() == 1
        UserProfile.objects.create(user=instance, is_admin=is_first_user)
    else:
        # Ensure a profile exists for existing users
        UserProfile.objects.get_or_create(user=instance)
