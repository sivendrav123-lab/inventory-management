from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "quantity",
            "price",
            "previous_sales",
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "quantity": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "price": forms.NumberInput(attrs={
                "class": "form-control"
            }),

            "previous_sales": forms.NumberInput(attrs={
                "class": "form-control"
            }),
        }