from django.contrib import admin

from .models import Item, UserProfile, Order, OrderItem, Address, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ['title']
    list_display = ('id', 'title', 'price', 'discount_price', 'category')
    list_filter = ('category',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ordering = ['user']
    search_fields = ['user__username']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['user__user__username', 'id']
    list_display = ('id', 'user', 'ordered_date')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    ordering = ['-id']
    search_fields = ['user__user__username', 'id', 'item__title', 'quantity']
    list_display = ('id', 'user', 'item')
    list_filter = ('quantity', 'user', 'item__category__name')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    ordering = ['id']
    search_fields = ['user__user__username', 'id', 'country', 'city']
    list_filter = ('country', 'city')
    list_display = ['id', 'user', 'country', 'city']
