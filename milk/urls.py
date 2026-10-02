from django.urls import path
from . import views

urlpatterns = [
    path('', views.milk_entry_list, name='milk_home'),
    path('add/', views.add_milk_entry, name='add_milk_entry'),
    path('list/', views.milk_entry_list, name='milk_entry_list'),
    path('bill/', views.calculate_milk_bill, name='calculate_milk_bill'),
    # Admin-only price management
    path('price/set/', views.set_milk_price, name='set_milk_price'),
    path('price/history/', views.milk_price_history, name='milk_price_history'),
]
