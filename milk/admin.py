from django.contrib import admin
from .models import MilkPrice, MilkEntry, MilkBill

# Register your models here.
class MilkPriceAdmin(admin.ModelAdmin):
    list_display = ('milk_type', 'price_per_litre', 'effective_from_date')

class MilkEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'milk_type', 'quantity_litres', 'logged_by')

class MilkBillAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'total_amount', 'is_paid')

admin.site.register(MilkPrice, MilkPriceAdmin)
admin.site.register(MilkEntry, MilkEntryAdmin)
admin.site.register(MilkBill, MilkBillAdmin)