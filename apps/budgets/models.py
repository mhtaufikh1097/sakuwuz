from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    nominal_max = models.DecimalField(max_digits=12, decimal_places=2)
    sisa = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}"