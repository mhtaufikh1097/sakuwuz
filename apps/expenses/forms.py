from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["tanggal", "nominal", "deskripsi"]
        widgets = {
            "tanggal": forms.DateInput(attrs={"type":"date"}),
            "deskripsi": forms.Textarea(attrs={"rows":2}),
        }
