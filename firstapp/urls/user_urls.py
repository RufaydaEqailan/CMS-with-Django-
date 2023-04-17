from django.urls import path
# from ..views.user_views import set_old_users,delete_user
from ..views import user_views, views,modify_user
 
urlpatterns = [
    path('setold', user_views.set_old_users),
    path('cleanup',user_views.delete_user),
    path('delete',modify_user.delete_one_user),
    path('modify',modify_user.modify_master_category),
    path('show',user_views.show_users),
    path('payment',user_views.show_payment_methods),
    path('search',user_views.search_by_value),
    path('add',user_views.add_user),
    path('test',views.show),
    
]
