# store/views.py
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from .models import Product, Category, Order, OrderItem
from .forms import OrderCreateForm
from .utils import send_telegram_message


# Helper to get cart items from session
def get_cart_products(request):
    cart = request.session.get('cart', [])  # список ID товарів
    return Product.objects.filter(id__in=cart)


# Base context processor for categories and cart count
def common_context(request):
    categories = Category.objects.all()
    cart_products = get_cart_products(request)
    return {
        'categories': categories,
        'cart_items': cart_products,
    }


# Product list view
def product_list(request):
    # Початковий queryset
    products = Product.objects.filter(available=True)

    # Фільтрація за категорією
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Пошук
    query = request.GET.get('q')
    if query:
        products = products.filter(title__icontains=query)

    context = common_context(request)
    context.update({'products': products})
    return render(request, 'store/product_list.html', context)


# Product detail view
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, available=True)
    context = common_context(request)
    context.update({'product': product})
    return render(request, 'store/product_detail.html', context)


# Cart view (simple display)
def cart_view(request):
    cart_products = get_cart_products(request)
    context = common_context(request)
    context.update({'cart_items': cart_products})
    return render(request, 'store/cart.html', context)


# Add to cart
def add_to_cart(request, product_id):
    cart = request.session.get('cart', [])
    if product_id not in cart:
        cart.append(product_id)
    request.session['cart'] = cart
    return redirect('cart_view')


# Remove from cart
def remove_from_cart(request, product_id):
    """
    Видаляє товар із сесійного кошика за його ID і редіректить назад у кошик.
    """
    cart = request.session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
    request.session['cart'] = cart
    return redirect('cart_view')


def order_view(request):
    # Загальний контекст
    categories = Category.objects.all()
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    cart_items = products

    if request.method == 'POST':
        # Забираємо і чистимо вхідні дані
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # Якщо хоч якесь поле пусте — повертаємо форму з помилкою
        if not (name and phone and address):
            messages.error(request, 'Будь ласка, заповніть усі поля форми.')
            return render(request, 'store/order.html', {
                'products': products,
                'categories': categories,
                'cart_items': cart_items,
                # щоб зберігся введений раніше текст
                'form_data': {'name': name, 'phone': phone, 'address': address},
            })

        # Формуємо текст списку товарів
        product_lines = [f"- {p.title} ({p.price} ₴)" for p in products]
        product_list = "\n".join(product_lines)

        # Створюємо замовлення
        order = Order.objects.create(
            name=name,
            phone=phone,
            address=address
        )
        for p in products:
            OrderItem.objects.create(order=order, product=p, price=p.price)

        # Email
        subject = "🔔 Нове замовлення з ComfyDrive"
        message = (
            f"👤 Ім’я: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"🏠 Адреса: {address}\n\n"
            f"🛒 Товари:\n{product_list}"
        )
        send_mail(
            subject,
            message,
            os.getenv('EMAIL_HOST_USER'),
            [os.getenv('EMAIL_NOTIFICATION_RECIPIENT', os.getenv('EMAIL_HOST_USER'))],
            fail_silently=False,
        )

        # Telegram
        telegram_text = (
                f"*Нове замовлення:*\n"
                f"👤 {name}\n"
                f"📞 {phone}\n"
                f"🏠 {address}\n\n"
                f"🛒 Товари:\n" + "\n".join(product_lines)
        )
        try:
            send_telegram_message(telegram_text)
        except Exception as e:
            print("Telegram send error:", e)

        # Очищуємо кошик і відправляємо успіх
        request.session['cart'] = []
        messages.success(request, 'Дякуємо! Ваше замовлення прийнято.')
        return redirect('product_list')

    # GET — відображаємо форму
    return render(request, 'store/order.html', {
        'products': products,
        'categories': categories,
        'cart_items': cart_items,
        'form_data': {'name': '', 'phone': '', 'address': ''},
    })


# Тепер додаємо нові в’юхи для статичних сторінок:
def about_view(request):
    context = common_context(request)
    return render(request, 'store/about.html', context)


def contacts_view(request):
    context = common_context(request)
    return render(request, 'store/contacts.html', context)


def delivery_view(request):
    context = common_context(request)
    return render(request, 'store/delivery.html', context)
