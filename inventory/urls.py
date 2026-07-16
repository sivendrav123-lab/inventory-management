from django.urls import path
from . import views

urlpatterns = [

    # Home
    path("", views.home, name="home"),

    # Inventory
    path("inventory/", views.product_list, name="product_list"),

    # Product CRUD
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:id>/", views.edit_product, name="edit_product"),
    path("delete/<int:id>/", views.delete_product, name="delete_product"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),

    # AI Prediction
    path("ai/<int:id>/", views.ai_prediction, name="ai_prediction"),

    # AI Dashboard
    path("ai-dashboard/", views.ai_dashboard, name="ai_dashboard"),

    # Analytics
    path("analytics/", views.analytics, name="analytics"),

    # Reports
    path("reports/", views.reports, name="reports"),

    # PDF Report
    path("report/<int:id>/", views.download_report, name="download_report"),

    # Excel Export
    path("export-excel/", views.export_excel, name="export_excel"),

    # About
    path("about/", views.about, name="about"),
]
path("analytics/", views.analytics, name="analytics"),
path("reports/", views.reports, name="reports"),