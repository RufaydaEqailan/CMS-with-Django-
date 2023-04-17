from django.urls import path
from ..views import  views,modify_cart,carts_views
 
urlpatterns = [
    path('setold', carts_views.set_old_carts),
    path('cleanup',carts_views.delete_carts),
    path('delete',modify_cart.delete_one_cart),
    path('modify',modify_cart.modify_master_category),
    path('show',carts_views.show_carts),
    path('status', carts_views.show_by_status),
    path('search',carts_views.search_by_value),
    path('price', modify_cart.calculate_cart_total_price),
    path('location',carts_views.search_by_location)
    
]
  