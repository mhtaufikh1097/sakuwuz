from django.db import models
from apps.budgets.models import Budget

class Expense(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    tanggal = models.DateField()
    waktu_input = models.DateTimeField(auto_now_add=True)
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    deskripsi = models.TextField()

    def __str__(self):
        return f"{self.tanggal} - {self.nominal}"
    
from decimal import Decimal

def _sum_queryset(qs):
    total = Decimal("0.00")
    for x in qs.values_list("nominal", flat=True):
        total += x
    return total

# monkey-patch helper agar bisa dipanggil .aggregate_sum()
from django.db.models import QuerySet
def _aggregate_sum(self):
    return _sum_queryset(self)
QuerySet.aggregate_sum = _aggregate_sum