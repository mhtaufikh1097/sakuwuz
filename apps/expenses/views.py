from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal

from .forms import ExpenseForm
from .models import Expense
from apps.budgets.models import Budget

@login_required(login_url="/admin/login/")
def add_expense_view(request):
    today = timezone.localdate()
    month, year = today.month, today.year
    budget = Budget.objects.filter(user=request.user, month=month, year=year).first()
    if not budget:
        messages.warning(request, "Silakan set budget bulan ini dulu.")
        return redirect("set_budget")

    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.budget = budget
            exp.save()
            # update sisa
            total = Expense.objects.filter(budget=budget).aggregate_sum()
            budget.sisa = budget.nominal_max - total
            budget.save(update_fields=["sisa"])
            # alert jika over
            if budget.sisa < 0:
                messages.error(request, "Tolong jangan terlalu boros — Anda sudah melebihi batas pengeluaran bulanan.")
            else:
                messages.success(request, "Pengeluaran tersimpan.")
            return redirect("dashboard")
    else:
        form = ExpenseForm(initial={"tanggal": today})
    return render(request, "expense_form.html", {"form": form, "budget": budget})
