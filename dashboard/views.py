from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.decorators import admin_required
from accounts.models import UserProfile
from milk.models import MilkEntry, MilkPrice
from milk.forms import MilkPriceForm
from milk.views import get_price_for_entry, build_month_options

@admin_required
def dashboard_overview(request):
    """Admin Dashboard Tab 1: Executive Overview & KPIs."""
    today = date.today()
    month = today.month
    year = today.year

    # Household member metrics
    total_users = User.objects.count()
    total_admins = UserProfile.objects.filter(is_admin=True).count()
    total_members = total_users - total_admins

    # Active month milk metrics
    entries_this_month = list(MilkEntry.objects.filter(date__month=month, date__year=year).select_related('logged_by'))

    total_qty_cow = Decimal('0.0')
    total_qty_buffalo = Decimal('0.0')
    total_price_cow = Decimal('0.0')
    total_price_buffalo = Decimal('0.0')

    for e in entries_this_month:
        price = Decimal(str(get_price_for_entry(e)))
        qty = Decimal(str(e.quantity_litres))
        if e.milk_type == 'cow':
            total_qty_cow += qty
            total_price_cow += qty * price
        elif e.milk_type == 'buffalo':
            total_qty_buffalo += qty
            total_price_buffalo += qty * price

    total_liters = total_qty_cow + total_qty_buffalo
    total_bill = total_price_cow + total_price_buffalo

    # Recent activities (last 8 entries)
    recent_entries = MilkEntry.objects.select_related('logged_by').order_by('-date', '-id')[:8]

    # Recent registered users
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:5]

    context = {
        'active_tab': 'overview',
        'today': today,
        'month_name': today.strftime('%B %Y'),
        'total_users': total_users,
        'total_admins': total_admins,
        'total_members': total_members,
        'total_qty_cow': total_qty_cow,
        'total_qty_buffalo': total_qty_buffalo,
        'total_liters': total_liters,
        'total_bill': total_bill,
        'entries_count': len(entries_this_month),
        'recent_entries': recent_entries,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/dashboard.html', context)


@admin_required
def dashboard_milk(request):
    """Admin Dashboard Tab 2: Complete Milk Management (Prices, History, Billing)."""
    today = date.today()

    # Handle Set New Price Form submission directly within dashboard tab
    if request.method == 'POST':
        form = MilkPriceForm(request.POST)
        if form.is_valid():
            form.save()
            milk_type = form.cleaned_data['milk_type']
            price = form.cleaned_data['price_per_litre']
            eff_date = form.cleaned_data['effective_from_date']
            messages.success(
                request,
                f"New price configured: {milk_type.title()} Milk → ₹{price}/L effective from {eff_date.strftime('%d %b %Y')}."
            )
            return redirect('dashboard_milk')
    else:
        form = MilkPriceForm(initial={'effective_from_date': today})

    # Month filter for billing breakdown
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        month, year = today.month, today.year
    month = max(1, min(12, month))

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

    total_bill = total_price_cow + total_price_buffalo
    total_liters = total_qty_cow + total_qty_buffalo

    # Active prices
    current_cow = MilkPrice.objects.filter(
        milk_type='cow', effective_from_date__lte=today
    ).order_by('-effective_from_date').first()
    current_buffalo = MilkPrice.objects.filter(
        milk_type='buffalo', effective_from_date__lte=today
    ).order_by('-effective_from_date').first()

    # Full price histories
    cow_prices = MilkPrice.objects.filter(milk_type='cow').order_by('-effective_from_date')
    buffalo_prices = MilkPrice.objects.filter(milk_type='buffalo').order_by('-effective_from_date')

    month_options = build_month_options(year, month)

    context = {
        'active_tab': 'milk',
        'form': form,
        'current_cow': current_cow,
        'current_buffalo': current_buffalo,
        'cow_prices': cow_prices,
        'buffalo_prices': buffalo_prices,
        'month': month,
        'year': year,
        'active_month_label': date(year, month, 1).strftime('%B %Y'),
        'month_options': month_options,
        'total_qty_cow': total_qty_cow,
        'total_qty_buffalo': total_qty_buffalo,
        'total_price_cow': total_price_cow,
        'total_price_buffalo': total_price_buffalo,
        'total_bill': total_bill,
        'total_liters': total_liters,
        'entries_count': len(entries),
    }
    return render(request, 'dashboard/milk_management.html', context)


@admin_required
def dashboard_members(request):
    """Admin Dashboard Tab 3: Household Members & Role Management."""
    users = User.objects.all().order_by('id')
    members = []
    total_admins = 0
    total_members = 0

    for u in users:
        p, _ = UserProfile.objects.get_or_create(user=u)
        is_u_admin = p.is_admin or u.is_superuser
        if is_u_admin:
            total_admins += 1
        else:
            total_members += 1
        members.append({
            'user': u,
            'profile': p,
            'is_admin': is_u_admin,
            'is_self': u == request.user,
        })

    context = {
        'active_tab': 'members',
        'members': members,
        'total_users': len(members),
        'total_admins': total_admins,
        'total_members': total_members,
    }
    return render(request, 'dashboard/members.html', context)
