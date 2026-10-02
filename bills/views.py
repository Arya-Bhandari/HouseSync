from datetime import date
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from milk.models import MilkEntry, MilkPrice
from milk.views import get_price_for_entry, build_month_options

@login_required
def aggregate_monthly_bill(request):
    """Aggregate household expenses view for active month (Milk + future Kirana/Electricity)."""
    today = date.today()

    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        month, year = today.month, today.year

    month = max(1, min(12, month))

    # --- Milk Bill Calculation ---
    entries = list(MilkEntry.objects.filter(date__month=month, date__year=year))

    total_qty_cow = Decimal('0')
    total_qty_buffalo = Decimal('0')
    total_price_cow = Decimal('0')
    total_price_buffalo = Decimal('0')

    for e in entries:
        price = get_price_for_entry(e)
        qty = Decimal(str(e.quantity_litres))
        if e.milk_type == 'cow':
            total_qty_cow += qty
            total_price_cow += qty * price
        elif e.milk_type == 'buffalo':
            total_qty_buffalo += qty
            total_price_buffalo += qty * price

    total_milk_bill = total_price_cow + total_price_buffalo
    total_milk_liters = total_qty_cow + total_qty_buffalo

    # --- Future Modules (Placeholders) ---
    kirana_total = Decimal('0.00')
    electricity_total = Decimal('0.00')

    # Grand total across all household utilities
    grand_total = total_milk_bill + kirana_total + electricity_total

    month_options = build_month_options(year, month)

    context = {
        'month': month,
        'year': year,
        'active_month_label': date(year, month, 1).strftime('%B %Y'),
        'month_options': month_options,
        'total_milk_bill': total_milk_bill,
        'total_milk_liters': total_milk_liters,
        'total_qty_cow': total_qty_cow,
        'total_qty_buffalo': total_qty_buffalo,
        'total_price_cow': total_price_cow,
        'total_price_buffalo': total_price_buffalo,
        'kirana_total': kirana_total,
        'electricity_total': electricity_total,
        'grand_total': grand_total,
    }
    return render(request, 'bills/monthly_bill.html', context)
