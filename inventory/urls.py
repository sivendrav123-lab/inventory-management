from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.product_list, name="product_list"),

    # Product CRUD
    path("add/", views.add_product, name="add_product"),
    path("edit/<int:id>/", views.edit_product, name="edit_product"),
    path("delete/<int:id>/", views.delete_product, name="delete_product"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),

    # AI Prediction (Automatic)
    path("ai/<int:id>/", views.ai_prediction, name="ai_prediction"),
]