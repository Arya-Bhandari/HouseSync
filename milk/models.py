from django.db import models
from django.conf import settings

MILK_CHOICES = [
  ('buffalo', 'Buffalo Milk'),
  ('cow', 'Cow Milk'),
]

# Create your models here.
class MilkPrice(models.Model):
  milk_type = models.CharField(max_length=155, choices=MILK_CHOICES)
  price_per_litre = models.DecimalField(max_digits=8, decimal_places=2)
  effective_from_date = models.DateField()

  def __str__(self):
      return f"{self.get_milk_type_display()} - Rs.{self.price_per_litre}/L"


class MilkEntry(models.Model):
  QUANTITY_CHOICES = [
      (0.25, '250ml'),
      (0.50, '500ml'),
      (0.75, '750ml'),
      (1.00, '1L'),
      (1.50, '1.5L'),
      (2.00, '2L'),
  ]
  date = models.DateField()
  milk_type = models.CharField(max_length=155, choices=MILK_CHOICES)
  quantity_litres = models.DecimalField(max_digits=6, decimal_places=2, choices=QUANTITY_CHOICES)
  logged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
  note = models.CharField(max_length=255, blank=True, null=True, help_text="Optional note for this entry")

  def __str__(self):
    return f"{self.date.strftime('%Y-%m-%d')} - {self.get_milk_type_display()}"


class MilkBill(models.Model):
  month = models.CharField(max_length=155)
  year = models.IntegerField()
  total_amount = models.DecimalField(max_digits=10, decimal_places=2)
  is_paid = models.BooleanField(default=False)
  paid_on_date = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return f"{self.month} {self.year} bill is paid: {self.is_paid}"