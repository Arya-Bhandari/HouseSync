from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_overview, name='admin_dashboard'),
    path('milk/', views.dashboard_milk, name='dashboard_milk'),
    path('members/', views.dashboard_members, name='dashboard_members'),
]
