from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["month", "year", "nominal_max"]
        widgets = {
            "month": forms.NumberInput(attrs={"min": 1, "max": 12, "class": "form-control"}),
            "year": forms.NumberInput(attrs={"min": 2000, "max": 2100, "class": "form-control"}),
            "nominal_max": forms.NumberInput(attrs={"class": "form-control"}),
        }
