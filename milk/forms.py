from django import forms
from django.utils import timezone
from .models import MilkEntry, MilkPrice

QUANTITY_OPTIONS = [('', 'None')] + [(str(val), label) for val, label in MilkEntry.QUANTITY_CHOICES]

class DailyMilkEntryForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    cow_quantity = forms.ChoiceField(
        choices=QUANTITY_OPTIONS,
        required=False,
        label="Cow Milk",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    buffalo_quantity = forms.ChoiceField(
        choices=QUANTITY_OPTIONS,
        required=False,
        label="Buffalo Milk",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    note = forms.CharField(
        required=False,
        max_length=255,
        label="Note (Optional)",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Guests visiting, extra milk needed',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm'
        })
    )
    clear_cow = forms.BooleanField(
        required=False,
        label="Clear Cow Milk",
    )
    clear_buffalo = forms.BooleanField(
        required=False,
        label="Clear Buffalo Milk",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['date'].initial = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        cow = cleaned_data.get('cow_quantity')
        buffalo = cleaned_data.get('buffalo_quantity')
        note = cleaned_data.get('note')
        clear_cow = cleaned_data.get('clear_cow')
        clear_buffalo = cleaned_data.get('clear_buffalo')
        # Require at least one meaningful action
        if not cow and not buffalo and not note and not clear_cow and not clear_buffalo:
            raise forms.ValidationError("Please fill in at least one field.")
        return cleaned_data


class MilkEntryForm(forms.ModelForm):
    class Meta:
        model = MilkEntry
        fields = ['date', 'milk_type', 'quantity_litres', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.now().date()


class MilkPriceForm(forms.ModelForm):
    class Meta:
        model = MilkPrice
        fields = ['milk_type', 'price_per_litre', 'effective_from_date']
        labels = {
            'milk_type': 'Milk Type',
            'price_per_litre': 'Price per Litre (₹)',
            'effective_from_date': 'Effective From Date',
        }
        widgets = {
            'milk_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'price_per_litre': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0',
                'placeholder': 'e.g. 65.00',
            }),
            'effective_from_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
        }