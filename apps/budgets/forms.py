from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["month", "year", "nominal_max"]
        widgets = {
            "month": forms.NumberInput(attrs={"min":1, "max":12}),
            "year": forms.NumberInput(attrs={"min":2000, "max":2100}),
        }
