import os
import requests
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ContactForm
from django.core.mail import send_mail
from .models import Product, Category, Order, OrderItem
from django.contrib import messages


def product_list(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search_query')

    products = Product.objects.filter(available=True)
    all_products = Product.objects.all()
    categories = Category.objects.all()

    if category_id:
        products = products.filter(category__id=category_id)

    if search_query:
        products = products.filter(title__icontains=search_query)

    return render(request, 'store/product_list.html', {
        'products': products,
        'all_products': all_products,
        'categories': categories
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})


def add_to_cart(request, product_id):
    cart = request.session.get('cart', [])
    if product_id not in cart:
        cart.append(product_id)
        request.session['cart'] = cart
        messages.success(request, "Товар додано в кошик.")
    return redirect('cart_view')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
        request.session['cart'] = cart
        messages.info(request, "Товар видалено з кошика.")
    return redirect('cart_view')


def cart_view(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    return render(request, 'store/cart.html', {'products': products})


def order_view(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        product_list = "\n".join([f"- {p.title} ({p.price} ₴)" for p in products])

        # Створення замовлення в базі
        order = Order.objects.create(
            name=name,
            phone=phone,
            address=address
        )

        # Додати кожен товар
        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price
            )

        # Email повідомлення
        email_subject = "Нове замовлення з ComfyDrive"
        email_message = f"""
Нове замовлення з сайту ComfyDrive:

👤 Ім’я: {name}
📞 Телефон: {phone}
🏠 Адреса: {address}

🛒 Товари:
{product_list}
"""
        send_mail(
            email_subject,
            email_message,
            None,
            [os.getenv('EMAIL_HOST_USER')],
        )

        # Telegram повідомлення
        telegram_text = f"""
📦 НОВЕ ЗАМОВЛЕННЯ:

👤 {name}
📞 {phone}
🏠 {address}

🛒 Товари:
{product_list}
"""
        send_telegram_message(telegram_text)

        # Очистити кошик і показати повідомлення
        request.session['cart'] = []
        messages.success(request, 'Замовлення оформлено. Очікуйте дзвінка!')
        return redirect('product_list')

    return render(request, 'store/order.html', {'products': products})


def about_view(request):
    return render(request, 'store/about.html')


def delivery_view(request):
    return render(request, 'store/delivery.html')


def contacts_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = f"Новий запит із сайту ComfyDrive від {form.cleaned_data['name']}"
            message = f"""
                Ім’я: {form.cleaned_data['name']}
                Email: {form.cleaned_data['email']}
                Повідомлення:
                {form.cleaned_data['message']}
                """
            send_mail(
                subject,
                message,
                None,  # from email
                ['yourname@gmail.com'],  # ← заміни на свою пошту
            )
            messages.success(request, 'Дякуємо! Ваше повідомлення надіслано.')
            form = ContactForm()
    return render(request, 'store/contacts.html', {'form': form})


def send_telegram_message(text):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {'chat_id': chat_id, 'text': text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Telegram Error:", e)
