from django.urls import path

from .views import (ItemListView, by_category,
                    ItemDetailView,
                    add_item_to_cart,
                    OrderSummaryView,
                    CartView,
                    CreateOrderAddressFormView,
                    remove_item_from_cart,
                    remove_one_item,
                    add_one_item,
                    success_order_view)


urlpatterns = [
    path('', ItemListView.as_view(), name='item-list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('item/<str:slug>/', ItemDetailView.as_view(), name='item-detail'),
    path('category/<str:category>/', by_category, name='item-list-by-category'),
    path(
        'create-address/',
        CreateOrderAddressFormView.as_view(),
        name='create-address'
        ),
    path('success-order/', success_order_view, name='success-order'),
    path(
        'remove-item-from-cart/<slug>/',
        remove_item_from_cart,
        name='remove-item-from-cart'
        ),
    path('remove-one-item/<slug>/', remove_one_item, name='remove-one-item'),
    path('add-one-item/<slug>/', add_one_item, name='add-one-item'),
    path('add-item/<str:slug>/', add_item_to_cart, name='add-item'),
]
