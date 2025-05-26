from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.db.models import Count, Sum
from django.shortcuts import render
from .models import Product, Category, Address, ProductImage, Order, OrderItem, Cart, CartItem

# Inline for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

# Inline for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['price']

# Inline for CartItem
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ['product', 'quantity', 'added_at']
    readonly_fields = ['added_at']

# Admin for Product
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ['name', 'category', 'price', 'stock']
    list_filter = ['category']
    search_fields = ['name', 'description']

# Admin for Order
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'user', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    date_hierarchy = 'created_at'

# Admin for Category
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

# Admin for Address
class AddressAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'city', 'state']
    list_filter = ['city', 'state']
    search_fields = ['name', 'user__username']

# Admin for Cart
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ['user', 'created_at', 'updated_at', 'item_count']
    search_fields = ['user__username']
    list_filter = ['created_at', 'updated_at']

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items in Cart'

# Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = "Clothing Store Admin"
    site_title = "Clothing Store Admin Portal"


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('logout/', self.admin_view(LogoutView.as_view(
                template_name='registration/logged_out.html',
            )), name='logout'),
            path('stats/', self.admin_view(self.stats_view), name='stats'),
            path('user-activity/', self.admin_view(self.user_activity_view), name='user_activity'),
        ]
        return custom_urls + urls

    def stats_view(self, request):
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
        top_products = Product.objects.annotate(
            order_count=Count('order_items')
        ).order_by('-order_count')[:5]

        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'orders_by_status': orders_by_status,
            'top_products': top_products,
            'site_header': self.site_header,
        }
        return render(request, 'admin/stats.html', context)

    def user_activity_view(self, request):
        # Get users with carts or orders
        users_with_carts = Cart.objects.select_related('user').all()
        users_with_orders = Order.objects.select_related('user').all()

        context = {
            'users_with_carts': users_with_carts,
            'users_with_orders': users_with_orders,
            'site_header': self.site_header,
        }
        return render(request, 'admin/user_activity.html', context)

# Instantiate and register models
admin_site = CustomAdminSite(name='custom_admin')

admin_site.register(Product, ProductAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Address, AddressAdmin)
admin_site.register(ProductImage)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem)
admin_site.register(Cart, CartAdmin)
admin_site.register(CartItem)