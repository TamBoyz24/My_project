from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return self.name

    def clean(self):
        if len(self.description) > 500:
            raise ValidationError({'description': 'Description cannot exceed 500 characters.'})

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False) 
    image = models.CharField(max_length=255, default='default_image_path.jpg')  # Cung cấp giá trị mặc định ở đây

    def __str__(self):
        return self.name


    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

# ProductImage Model
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name_plural = "Product Images"

# Review Model (merged)
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, f"{i} ") for i in range(1, 6)])  # Rating từ 1 đến 5 sao
    comment = models.TextField(blank=True, null=True)  # Bình luận của người dùng (có thể trống)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} sao"

    class Meta:
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']

# Address Model
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=200)
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")],
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{5}(-\d{4})?$', message="Enter a valid ZIP code.")],
        blank=True,
    )

    def __str__(self):
        return f"{self.name} - {self.locality}, {self.city}"

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['user', 'name']
        indexes = [
            models.Index(fields=['user']),
        ]

# Order Model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')],
        default='pending',
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def update_status(self, new_status):
        valid_transitions = {
            'pending': ['shipped', 'canceled'],
            'shipped': ['delivered', 'canceled'],
            'delivered': [],
            'canceled': [],
        }
        if new_status not in valid_transitions[self.status]:
            raise ValidationError(f"Cannot change status from {self.status} to {new_status}.")
        self.status = new_status
        self.save()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    class Meta:
        verbose_name_plural = "Order Items"
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

# Cart Model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    class Meta:
        verbose_name_plural = "Carts"

# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"

    class Meta:
        verbose_name_plural = "Cart Items"
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]

# Wishlist Model
class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField(Product, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for {self.user.username}"

    class Meta:
        verbose_name_plural = "Wishlists"
