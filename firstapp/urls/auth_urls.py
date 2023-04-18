from django.urls import path
# from ..views.products_views import set_old_users,delete_user
from ..views import  auth_views
 
urlpatterns = [
    path('login', auth_views.login),
    path('logout',auth_views.logout),
    path('register',auth_views.register),

    
]
       