from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_expense_view, name="add_expense"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("calendar/<int:year>/<int:month>/<int:day>/",
         views.day_detail_view, name="day_detail"),
    path("<int:year>/<int:month>/<int:day>/",
         views.expense_by_day, name="expense_by_day"),
]