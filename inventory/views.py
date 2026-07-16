from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductForm
import joblib
import os


def product_list(request):

    search = request.GET.get("search")

    products = Product.objects.all()

    if search:
        products = products.filter(name__icontains=search)

    total_products = Product.objects.count()

    total_quantity = Product.objects.aggregate(
        Sum("quantity")
    )["quantity__sum"] or 0

    total_value = Product.objects.aggregate(
        total=Sum(F("quantity") * F("price"))
    )["total"] or 0

    paginator = Paginator(products, 5)

    page = request.GET.get("page")

    products = paginator.get_page(page)

    return render(request, "inventory/product_list.html", {
        "products": products,
        "total_products": total_products,
        "total_quantity": total_quantity,
        "total_value": total_value,
    })


def add_product(request):

    if request.method == "POST":

        form = ProductForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:

        form = ProductForm()

    return render(request, "inventory/add_product.html", {
        "form": form
    })


def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("product_list")

    else:

        form = ProductForm(instance=product)

    return render(request, "inventory/add_product.html", {
        "form": form
    })


def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect("product_list")

    return render(request, "inventory/delete_product.html", {
        "product": product
    })


def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    return render(request, "inventory/product_detail.html", {
        "product": product
    })


# ===========================
# AI DEMAND PREDICTION
# ===========================
def ai_prediction(request, id):

    product = get_object_or_404(Product, id=id)

    current_stock = product.quantity
    previous_sales = product.previous_sales

    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sales_model.pkl"
    )

    model = joblib.load(model_path)

    prediction = model.predict([[current_stock, previous_sales]])[0]

    # Demand Level
    if prediction >= 80:
        demand = "High"
    elif prediction >= 40:
        demand = "Medium"
    else:
        demand = "Low"

    # Health Score
    if current_stock > 0:
        health_score = min(100, int((previous_sales / current_stock) * 100))
    else:
        health_score = 0

    if health_score >= 80:
        health = "Excellent"
    elif health_score >= 50:
        health = "Average"
    else:
        health = "Poor"

    # Recommendation
    if prediction > current_stock:
        recommendation = "Increase Stock"
    elif prediction < current_stock / 2:
        recommendation = "Reduce Stock"
    else:
        recommendation = "Maintain Current Stock"

    return render(
        request,
        "inventory/ai_prediction.html",
        {
            "product": product,
            "current_stock": current_stock,
            "previous_sales": previous_sales,
            "prediction": round(prediction, 2),
            "demand": demand,
            "health": health,
            "health_score": health_score,
            "recommendation": recommendation,
        },
    )