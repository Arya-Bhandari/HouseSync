from django.urls import path
from accounts import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('members/toggle/<int:user_id>/', views.toggle_admin_status, name='toggle_admin_status'),
    path('logout/', views.logout_view, name='logout'),
]
