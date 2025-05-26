from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.core.paginator import Paginator
from decimal import Decimal
from .models import Product, Category, Address, Cart, CartItem, ProductImage, Order, OrderItem, Wishlist
from .forms import RegisterForm, LoginForm, AddressForm, ContactForm,ReviewForm




# Homepage View
from django.shortcuts import render
from .models import Product, Category

def home(request):
    featured_products = Product.objects.filter(is_featured=True)
    all_products = Product.objects.all()
    categories = Category.objects.all() if Category.objects.exists() else []
    top_products = Product.objects.all()[:3] if Product.objects.exists() else []

    context = {
        'featured_products': featured_products,
        'all_products': all_products,
        'products': top_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

# Product Detail View
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    images = product.images.all()
    # Lấy các review của sản phẩm
    reviews = product.reviews.all()
    # Tạo dãy sao (range) từ 1 đến 5
    star_range = range(1, 6)
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
            return redirect('product_detail', product_id=product.id)
        else:
            return redirect('login')
    else:
        form = ReviewForm()
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
        'reviews': reviews,
        'star_range': star_range,
        'form': form
    })

# Category View
def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    
    # Sorting
    sort = request.GET.get('sort', 'default')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 9)  # 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/category.html', {
        'category': category,
        'products': page_obj,
        'sort': sort
    })

# Search View
def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query)
    return render(request, 'store/search.html', {'products': products, 'query': query})
    
    # Sorting
    sort = request.GET.get('sort', 'default')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/search.html', {
        'products': page_obj,
        'query': query,
        'sort': sort
    })

# Authentication Views
class CustomLoginView(LoginView):
    template_name = 'store/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            Wishlist.objects.create(user=user)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return render(request, 'store/logged_out.html')

# About Us View
def about_us(request):
    return render(request, 'store/about_us.html')

# Contact Us View
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            try:
                send_mail(
                    f"Contact Us: {name}",
                    message,
                    email,
                    ['admin@clothingstore.com'],
                    fail_silently=False,
                )
                messages.success(request, "Thank you for your message! We'll get back to you soon.")
            except Exception as e:
                messages.error(request, f"Failed to send message: {str(e)}")
            return redirect('contact_us')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContactForm()
    return render(request, 'store/contact_us.html', {'form': form})

# Wishlist View
@login_required
def wishlist(request):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    products = wishlist.products.all()
    return render(request, 'store/wishlist.html', {'products': products})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if product not in wishlist.products.all():
        wishlist.products.add(product)
        messages.success(request, f"{product.name} added to wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    return redirect(request.GET.get('next', 'wishlist'))

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    wishlist.products.remove(product)
    messages.success(request, f"{product.name} removed from wishlist.")
    return redirect('wishlist')

# Cart Views
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    else:
        quantity = 1
    
    if quantity <= 0:
        messages.error(request, "Quantity must be at least 1.")
        return redirect('product_detail', product_id=product_id)
    
    if product.stock < quantity:
        messages.error(request, f"Sorry, only {product.stock} items available.")
        return redirect('product_detail', product_id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity = quantity if created else cart_item.quantity + quantity
    cart_item.save()
    
    messages.success(request, f"{product.name} added to cart.")
    next_url = request.POST.get('next', 'cart')
    return redirect(next_url)

@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')

@login_required
def update_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            if cart_item.product.stock < quantity:
                messages.error(request, f"Sorry, only {cart_item.product.stock} items available.")
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, "Cart updated.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
    return redirect('cart')

@login_required
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    messages.success(request, "Cart cleared successfully.")
    return redirect('cart')

@login_required
def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('product').all()
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('10.00') if cart_items else Decimal('0.00')
    grand_total = total + shipping
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
        'shipping': shipping,
        'grand_total': grand_total
    })

# User Profile View
@login_required
def user_profile(request):
    user = request.user
    addresses = user.addresses.all()
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        address_id = request.POST.get('address_id')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=user)
            form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if not address_id:
                address.user = user
            address.save()
            messages.success(request, f"Address {'updated' if address_id else 'added'} successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddressForm()
    
    return render(request, 'store/profile.html', {
        'user': user,
        'addresses': addresses,
        'form': form
    })

# Add Address View
@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AddressForm()
    return render(request, 'store/add_address.html', {'form': form})

# Order Checkout
@login_required
@transaction.atomic
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')
    
    addresses = request.user.addresses.all()
    if not addresses.exists():
        messages.error(request, "Please add an address before checking out.")
        return redirect('add_address')
    
    cart_items = cart.items.select_related('product').all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    shipping = Decimal('10.00') if cart_items else Decimal('0.00')
    grand_total = total + shipping
    
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('checkout')
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Lock products to prevent race conditions
        for item in cart_items:
            product = Product.objects.select_for_update().get(id=item.product.id)
            if product.stock < item.quantity:
                messages.error(request, f"Sorry, only {product.stock} of {product.name} available.")
                return redirect('cart')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_price=grand_total
        )
        
        # Create order items and update stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
        
        # Clear cart
        cart.items.all().delete()
        messages.success(request, "Đơn Hàng Đã Đặt Thành Công!")
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'addresses': addresses,
        'total': total,
        'shipping': shipping,
        'grand_total': grand_total
    })

# Order Confirmation
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})

# Footer Views
def returns(request):
    return render(request, 'store/returns.html')

def faqs(request):
    return render(request, 'store/faqs.html')

def careers(request):
    return render(request, 'store/careers.html')

def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')