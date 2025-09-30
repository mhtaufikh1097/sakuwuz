from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from .models import Budget
from .forms import BudgetForm
from apps.expenses.models import Expense
from django.contrib.auth.decorators import login_required

def _active_period():
    now = timezone.localdate()
    return now.month, now.year

@login_required(login_url="/admin/login/")  # sementara pakai admin login
def dashboard_view(request):
    month, year = _active_period()
    budget = Budget.objects.filter(user=request.user, month=month, year=year).first()

    total_terpakai = 0
    expenses_today = []
    if budget:
        total_terpakai = Expense.objects.filter(budget=budget).aggregate(total=Sum("nominal"))["total"] or 0
    expenses_today = Expense.objects.filter(
        budget=budget, tanggal=timezone.localdate()
    ).order_by("-waktu_input")

    sisa = (budget.nominal_max - total_terpakai) if budget else None
    percent = 0
    if budget and budget.nominal_max > 0:
        percent = min(100, round((total_terpakai / budget.nominal_max) * 100, 2))
    over = sisa is not None and sisa < 0

    context = {
    "budget": budget,
    "total_terpakai": total_terpakai,
    "sisa": sisa,
    "percent": percent,
    "over": over,
    "expenses_today": expenses_today,
    "month": month, "year": year,
    }   

    if over:
        messages.error(request, "Tolong jangan terlalu boros — Anda sudah melebihi batas pengeluaran bulanan.")
    return render(request, "dashboard.html", context)

@login_required(login_url="/admin/login/")
def set_budget_view(request):
    # ambil bulan/tahun aktif dari query, fallback ke bulan berjalan
    today = timezone.localdate()
    month = int(request.GET.get("month", today.month))
    year = int(request.GET.get("year", today.year))

    # cari budget existing utk user+bulan+tahun itu
    instance = Budget.objects.filter(user=request.user, month=month, year=year).first()

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=instance)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            # hitung sisa berdasarkan pengeluaran yg sudah ada (jika edit)
            from apps.expenses.models import Expense
            from django.db.models import Sum
            total = Expense.objects.filter(budget=instance).aggregate(total=Sum("nominal"))["total"] or 0 if instance else 0
            budget.sisa = budget.nominal_max - total
            budget.save()
            messages.success(request, "Budget bulanan disimpan.")
            return redirect("calendar")  # atau redirect("dashboard")
    else:
        # prefill form sesuai bulan/tahun target
        initial = {"month": month, "year": year}
        form = BudgetForm(instance=instance, initial=initial)

    return render(request, "budget_set.html", {"form": form, "month": month, "year": year})
