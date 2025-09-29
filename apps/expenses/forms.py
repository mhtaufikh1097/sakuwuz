from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["tanggal", "nominal", "deskripsi"]
        widgets = {
            "tanggal": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "nominal": forms.NumberInput(attrs={"step": "0.01", "class": "form-control"}),
            "deskripsi": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }
