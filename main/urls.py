from django.urls import path
from .views import *

urlpatterns = [
    path('',index_view),
    path('cart/',cart_view),
    path('detail/',product_detail),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/<str:action>/', update_quantity, name='update_quantity'),
    path('payment/<int:order_id>/', payment_page, name='payment_page'),
    path('free-products/<int:order_id>/', free_view, name='free-products'),
    path('free/',free_info_view),
    path('thanks/', thanks_view, name='thanks'),
    path('api/reverse/', reverse_geocode, name='reverse_geocode'),
    
    #sidebar
    path('media/',media_view),
    path('about/',about_view),
    path('contact/',contact_view),
    
    #admin
    path('orders/', admin_orders_view, name='admin_orders'),
    path('orders/update/<int:order_id>/', update_order_status, name='update_order_status'),
    path('orders/delete/<int:order_id>/', delete_order, name='delete_order'),
]
