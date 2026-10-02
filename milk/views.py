from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from .forms import MilkEntryForm, DailyMilkEntryForm, MilkPriceForm
from .models import MilkEntry, MilkPrice
import calendar


# ─── Helpers ────────────────────────────────────────────────────────────────

def get_price_for_entry(entry):
    """Return the correct MilkPrice for a given entry based on its date."""
    price = MilkPrice.objects.filter(
        milk_type=entry.milk_type,
        effective_from_date__lte=entry.date
    ).order_by('-effective_from_date').first()
    return price.price_per_litre if price else Decimal('0')


def build_month_options(year, month):
    """Build a list of month picker dicts spanning from the earliest entry to today."""
    today = date.today()
    earliest = MilkEntry.objects.order_by('date').values('date').first()
    requested_start = date(year, month, 1)
    today_start = date(today.year, today.month, 1)

    if earliest:
        earliest_start = date(earliest['date'].year, earliest['date'].month, 1)
        cur = min(earliest_start, requested_start)
    else:
        cur = min(today_start, requested_start)

    end = max(today_start, requested_start)
    month_options = []
    while cur <= end:
        month_options.append({
            'year':   cur.year,
            'month':  cur.month,
            'label':  cur.strftime('%B %Y'),
            'active': cur.year == year and cur.month == month,
        })
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    month_options.reverse()
    return month_options


# ─── User Views ─────────────────────────────────────────────────────────────

@login_required
def add_milk_entry(request):
    if request.method == 'POST':
        form = DailyMilkEntryForm(request.POST)
        if form.is_valid():
            selected_date  = form.cleaned_data['date']
            cow_qty        = form.cleaned_data.get('cow_quantity')
            buffalo_qty    = form.cleaned_data.get('buffalo_quantity')
            note           = form.cleaned_data.get('note')
            clear_cow      = form.cleaned_data.get('clear_cow')
            clear_buffalo  = form.cleaned_data.get('clear_buffalo')

            # Handle Cow milk entry
            if clear_cow:
                MilkEntry.objects.filter(date=selected_date, milk_type='cow').delete()
            elif cow_qty:
                MilkEntry.objects.update_or_create(
                    date=selected_date,
                    milk_type='cow',
                    defaults={
                        'quantity_litres': cow_qty,
                        'logged_by': request.user,
                        'note': note or None,
                    }
                )

            # Handle Buffalo milk entry
            if clear_buffalo:
                MilkEntry.objects.filter(date=selected_date, milk_type='buffalo').delete()
            elif buffalo_qty:
                MilkEntry.objects.update_or_create(
                    date=selected_date,
                    milk_type='buffalo',
                    defaults={
                        'quantity_litres': buffalo_qty,
                        'logged_by': request.user,
                        'note': note or None,
                    }
                )

            # If only note was updated, apply it to existing entries for that date
            if not cow_qty and not buffalo_qty and not clear_cow and not clear_buffalo and note:
                MilkEntry.objects.filter(date=selected_date).update(note=note)

            # Redirect back to the same month that was active in the list
            next_year  = request.POST.get('next_year')
            next_month = request.POST.get('next_month')
            base_url   = reverse('milk_entry_list')
            if next_year and next_month:
                return redirect(f"{base_url}?year={next_year}&month={next_month}")
            return redirect('milk_entry_list')

    else:
        form = DailyMilkEntryForm()
    return render(request, 'milk/add_entry.html', {'form': form})


@login_required
def milk_entry_list(request):
    today = date.today()

    try:
        year  = int(request.GET.get('year',  today.year))
        month = int(request.GET.get('month', today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    month = max(1, min(12, month))

    entries = (
        MilkEntry.objects
        .filter(date__year=year, date__month=month)
        .select_related('logged_by')
        .order_by('-date')
    )

    # Group entries by date
    grouped = {}
    for entry in entries:
        d = entry.date
        if d not in grouped:
            grouped[d] = {
                'date': d,
                'cow_qty': None,
                'buffalo_qty': None,
                'note': None,
                'logged_by': set(),
            }
        display_qty = entry.get_quantity_litres_display()
        if entry.milk_type == 'cow':
            grouped[d]['cow_qty'] = display_qty
        elif entry.milk_type == 'buffalo':
            grouped[d]['buffalo_qty'] = display_qty
        if entry.note:
            grouped[d]['note'] = entry.note
        if entry.logged_by:
            grouped[d]['logged_by'].add(entry.logged_by.username)

    grouped_entries = []
    for item in grouped.values():
        item['logged_by'] = ", ".join(item['logged_by']) if item['logged_by'] else "-"
        grouped_entries.append(item)

    month_options = build_month_options(year, month)

    # Prev / Next month navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    is_current_month = (year > today.year or (year == today.year and month >= today.month))

    form = DailyMilkEntryForm()
    return render(request, 'milk/milk_entry_list.html', {
        'entries':            grouped_entries,
        'form':               form,
        'active_year':        year,
        'active_month':       month,
        'active_month_label': date(year, month, 1).strftime('%B %Y'),
        'month_options':      month_options,
        'prev_year':          prev_year,
        'prev_month':         prev_month,
        'next_year':          next_year,
        'next_month':         next_month,
        'is_current_month':   is_current_month,
    })


@login_required
def calculate_milk_bill(request):
    today = date.today()

    try:
        month = int(request.GET.get('month', today.month))
        year  = int(request.GET.get('year',  today.year))
    except (ValueError, TypeError):
        month, year = today.month, today.year

    month = max(1, min(12, month))

    entries = list(MilkEntry.objects.filter(date__month=month, date__year=year))

    total_qty_cow       = Decimal('0')
    total_qty_buffalo   = Decimal('0')
    total_price_cow     = Decimal('0')
    total_price_buffalo = Decimal('0')

    for e in entries:
        price = get_price_for_entry(e)
        qty   = Decimal(str(e.quantity_litres))
        if e.milk_type == 'cow':
            total_qty_cow    += qty
            total_price_cow  += qty * price
        elif e.milk_type == 'buffalo':
            total_qty_buffalo    += qty
            total_price_buffalo  += qty * price

    total_bill = total_price_cow + total_price_buffalo

    # Current active prices for display banner
    current_cow_price = MilkPrice.objects.filter(
        milk_type='cow', effective_from_date__lte=today
    ).order_by('-effective_from_date').first()
    current_buffalo_price = MilkPrice.objects.filter(
        milk_type='buffalo', effective_from_date__lte=today
    ).order_by('-effective_from_date').first()

    month_options = build_month_options(year, month)

    return render(request, 'milk/milk_bill.html', {
        'total_qty_cow':         total_qty_cow,
        'total_qty_buffalo':     total_qty_buffalo,
        'total_price_cow':       total_price_cow,
        'total_price_buffalo':   total_price_buffalo,
        'total_bill':            total_bill,
        'month':                 month,
        'year':                  year,
        'active_month_label':    date(year, month, 1).strftime('%B %Y'),
        'month_options':         month_options,
        'current_cow_price':     current_cow_price,
        'current_buffalo_price': current_buffalo_price,
        'no_price_set':          not current_cow_price and not current_buffalo_price,
    })


# ─── Admin Views ─────────────────────────────────────────────────────────────

@admin_required
def set_milk_price(request):
    """Redirect to unified milk management tab inside dashboard."""
    return redirect('dashboard_milk')


@admin_required
def milk_price_history(request):
    """Redirect to unified milk management tab inside dashboard."""
    return redirect('dashboard_milk')