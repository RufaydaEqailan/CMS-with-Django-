from django.urls import path
# from ..views.products_views import set_old_users,delete_user
from ..views import  views,modify_product,products_views
 
urlpatterns = [
    path('setold', products_views.set_old_products),
    path('cleanup',products_views.delete_products),
    path('delete',modify_product.delete_one_product),
    path('modify',modify_product.modify_master_category),
    path('show',products_views.show_products),
    path('caterories',products_views.show_categories_product),
    path('search',products_views.search_by_value),
    path('add',products_views.add_product),
    
]
       