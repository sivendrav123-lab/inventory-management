from reportlab.pdfgen import canvas
from django.http import HttpResponse
from openpyxl import Workbook
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductForm
import joblib
import os
def home(request):
    return render(request, "inventory/home.html")

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

    # Dashboard Statistics
    low_stock = Product.objects.filter(quantity__lt=5).count()
    high_stock = Product.objects.filter(quantity__gte=20).count()

    # Chart Data
    chart_labels = [product.name for product in products]
    chart_values = [product.quantity for product in products]

    # ==========================
    # AI SUMMARY
    # ==========================

    high_demand = 0
    medium_demand = 0
    low_demand_count = 0

    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sales_model.pkl"
    )

    model = joblib.load(model_path)

    for product in products:

        prediction = model.predict(
            [[product.quantity, product.previous_sales]]
        )[0]

        if prediction >= 80:
            high_demand += 1
        elif prediction >= 40:
            medium_demand += 1
        else:
            low_demand_count += 1

    paginator = Paginator(products, 5)

    page = request.GET.get("page")

    products = paginator.get_page(page)

    return render(request, "inventory/product_list.html", {

        "products": products,

        "total_products": total_products,

        "total_quantity": total_quantity,

        "total_value": total_value,

        "low_stock": low_stock,

        "high_stock": high_stock,

        "chart_labels": chart_labels,

        "chart_values": chart_values,

        "high_demand": high_demand,

        "medium_demand": medium_demand,

        "low_demand": low_demand_count,

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

        # Chart values
        "stock": current_stock,
        "sales": previous_sales,
        "predicted": round(prediction, 2),
    },
)
def export_excel(request):

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "Inventory Report"

    worksheet.append([
        "Product Name",
        "Quantity",
        "Price",
        "Previous Sales"
    ])

    products = Product.objects.all()

    for product in products:

        worksheet.append([
            product.name,
            product.quantity,
            float(product.price),
            product.previous_sales
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename=Inventory_Report.xlsx'

    workbook.save(response)

    return response
def download_report(request, id):

    product = get_object_or_404(Product, id=id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{product.name}_Report.pdf"'

    pdf = canvas.Canvas(response)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "AI Inventory Report")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(50, 750, f"Product Name : {product.name}")
    pdf.drawString(50, 730, f"Quantity : {product.quantity}")
    pdf.drawString(50, 710, f"Price : ₹{product.price}")
    pdf.drawString(50, 690, f"Previous Sales : {product.previous_sales}")

    pdf.drawString(50, 650, "Generated by:")
    pdf.drawString(180, 650, "AI Powered Smart Inventory Management System")

    pdf.drawString(50, 620, "Developed By:")
    pdf.drawString(180, 620, "Sivendra Viswanath")

    pdf.save()

    return response
def ai_dashboard(request):

    products = Product.objects.all()

    ai_products = []

    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sales_model.pkl"
    )

    model = joblib.load(model_path)

    for product in products:

        current_stock = product.quantity
        previous_sales = product.previous_sales

        prediction = model.predict([[current_stock, previous_sales]])[0]

        if prediction >= 80:
            demand = "High"
        elif prediction >= 40:
            demand = "Medium"
        else:
            demand = "Low"

        if current_stock > 0:
            health_score = min(100, int((previous_sales/current_stock)*100))
        else:
            health_score = 0

        if health_score >= 80:
            health = "Excellent"
        elif health_score >= 50:
            health = "Average"
        else:
            health = "Poor"

        if prediction > current_stock:
            recommendation = "Increase Stock"
        elif prediction < current_stock / 2:
            recommendation = "Reduce Stock"
        else:
            recommendation = "Maintain Stock"

        ai_products.append({
            "name": product.name,
            "stock": current_stock,
            "sales": previous_sales,
            "prediction": round(prediction,2),
            "demand": demand,
            "health": health,
            "recommendation": recommendation,
        })

    return render(
        request,
        "inventory/ai_dashboard.html",
        {
            "products": ai_products,
        }
    )
def analytics(request):
    return render(request, "inventory/product_list.html")

def reports(request):
    return render(request, "inventory/product_list.html")
def about(request):
    return render(request, "inventory/about.html")
def analytics(request):

    products = Product.objects.all()

    high_demand = 0
    medium_demand = 0
    low_demand = 0

    chart_labels = []
    chart_values = []

    model_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sales_model.pkl"
    )

    model = joblib.load(model_path)

    for product in products:

        prediction = model.predict(
            [[product.quantity, product.previous_sales]]
        )[0]

        chart_labels.append(product.name)
        chart_values.append(product.quantity)

        if prediction >= 80:
            high_demand += 1
        elif prediction >= 40:
            medium_demand += 1
        else:
            low_demand += 1

    low_stock = Product.objects.filter(quantity__lt=5).count()
    high_stock = Product.objects.filter(quantity__gte=20).count()

    return render(
        request,
        "inventory/analytics.html",
        {
            "high_demand": high_demand,
            "medium_demand": medium_demand,
            "low_demand": low_demand,
            "chart_labels": chart_labels,
            "chart_values": chart_values,
            "low_stock": low_stock,
            "high_stock": high_stock,
        }
    )
    
def reports(request):
    return render(request, "inventory/reports.html")