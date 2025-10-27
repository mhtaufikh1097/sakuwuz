# apps/expenses/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Q
from django.urls import reverse

import calendar as pycal
from datetime import date as dt_date

from .forms import ExpenseForm
from .models import Expense
from apps.budgets.models import Budget


@login_required(login_url="/admin/login/")
def add_expense_view(request):
    """Form tambah pengeluaran, otomatis pakai budget bulan berjalan."""
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

            # update sisa budget
            total = (
                Expense.objects.filter(budget=budget)
                .aggregate(total=Sum("nominal"))["total"] or 0
            )
            budget.sisa = budget.nominal_max - total
            budget.save(update_fields=["sisa"])

            if budget.sisa < 0:
                messages.error(request, "Tolong jangan terlalu boros — Anda sudah melebihi batas pengeluaran bulanan.")
            else:
                messages.success(request, "Pengeluaran tersimpan.")
            return redirect("dashboard")
    else:
        # baca ?date=YYYY-MM-DD kalau datang dari halaman detail
        qd = request.GET.get("date")
        try:
            initial_date = dt_date.fromisoformat(qd) if qd else today
        except ValueError:
            initial_date = today
        form = ExpenseForm(initial={"tanggal": initial_date})

    return render(request, "expense_form.html", {"form": form, "budget": budget})


def _get_month_year(request):
    """Ambil year & month dari querystring; fallback ke hari ini."""
    t = timezone.localdate()
    try:
        return int(request.GET.get("year", t.year)), int(request.GET.get("month", t.month))
    except (TypeError, ValueError):
        return t.year, t.month


@login_required(login_url="/admin/login/")
def calendar_view(request):
    """Kalender bulanan + total per tanggal (sum nominal)."""
    year, month = _get_month_year(request)
    budget = Budget.objects.filter(user=request.user, month=month, year=year).first()

    totals = {}
    if budget:
        # group by tanggal untuk bulan & tahun yang dipilih
        qs = (
            Expense.objects.filter(budget=budget, tanggal__year=year, tanggal__month=month)
            .values("tanggal")
            .annotate(total=Sum("nominal"))
        )
        totals = {x["tanggal"].day: x["total"] for x in qs}

    first_weekday, days_in_month = pycal.monthrange(year, month)

    # bangun grid 6 minggu x 7 hari
    weeks, day = [], 1
    for _ in range(6):
        row = []
        for dow in range(7):
            if (len(weeks) == 0 and dow < first_weekday) or day > days_in_month:
                row.append(None)
            else:
                row.append({
                    "day": day,
                    "total": totals.get(day, 0),
                    "url": reverse("day_detail", args=[year, month, day]),
                })
                day += 1
        weeks.append(row)

    # link prev/next month
    prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)

    return render(request, "calendar.html", {
        "year": year,
        "month": month,
        "weeks": weeks,
        "days_in_month": days_in_month,
        "budget": budget,
        "totals": totals,
        "prev_link": f"{reverse('calendar')}?year={prev_y}&month={prev_m}",
        "next_link": f"{reverse('calendar')}?year={next_y}&month={next_m}",
        "today": timezone.localdate(),
    })


@login_required(login_url="/admin/login/")
def day_detail_view(request, year, month, day):
    """
    Detail pengeluaran per tanggal.
    Menggunakan field yang ada di model kamu:
      - tanggal (DateField)
      - nominal (angka)
      - waktu_input (DateTimeField) untuk urutan tampilan
      - relasi ke Budget (filter per user & bulan-tahun)
    """
    # validasi tanggal
    try:
        d = dt_date(year, month, day)
    except ValueError:
        messages.error(request, "Tanggal tidak valid.")
        return redirect("calendar")

    budget = Budget.objects.filter(user=request.user, month=month, year=year).first()
    if not budget:
        messages.warning(request, "Belum ada budget untuk bulan tersebut.")
        return redirect(f"{reverse('calendar')}?year={year}&month={month}")

    items = (
        Expense.objects
        .filter(budget=budget, tanggal=d)
        .order_by("-waktu_input")  # sesuaikan jika nama field beda
    )
    subtotal = items.aggregate(total=Sum("nominal"))["total"] or 0

    context = {
        "date": d,
        "items": items,
        "subtotal": subtotal,
        "year": year,
        "month": month,
        "day": day,
    }
    return render(request, "day_detail.html", context)


# Opsional: alias agar rute "expense_by_day" juga pakai logic yang sama
expense_by_day = day_detail_view
