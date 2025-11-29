from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .models import Product, Cart


def home(request):
    return render(request, 'shop/home.html')


def products(request):
    all_products = Product.objects.all() 
    return render(request, 'shop/products.html', {'products': all_products})

def product_detail(request, product_id):
    product_list = Product.objects.filter(id=product_id)
    if not product_list.exists():
        return redirect('products')

    product = product_list.first()

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_products_ids = cart.products.values_list('id', flat=True)
    else:
        cart_products_ids = []

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'cart_products_ids': cart_products_ids
    })


def cart_view(request):
    if request.user.is_authenticated:
        cart_list = Cart.objects.filter(user=request.user)
        if cart_list.exists():
            cart = cart_list.first()
            products = cart.products.all()
        else:
            products = []
    else:
        products = []
    return render(request, 'shop/cart.html', {'products': products})

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login') 

    product_list = Product.objects.filter(id=product_id)
    if not product_list.exists():
        return redirect('products')

    product = product_list.first()

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart.products.add(product)
    cart.save()

    return redirect('product_detail', product_id=product_id)

def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=product_id)
        cart.products.remove(product)
    return redirect('cart')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')


        if not username or not password or not password_confirm:
            messages.error(request, 'All fields are required.')
            return redirect('signup')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('signup')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('home')
    
    return render(request, 'shop/signup.html')

