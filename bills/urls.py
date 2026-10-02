from django.urls import path
from . import views

urlpatterns = [
    path('', views.aggregate_monthly_bill, name='aggregate_monthly_bill'),
]
