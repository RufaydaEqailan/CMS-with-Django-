from django.urls import path
from ..views import  total_views

urlpatterns = [
    path('showuser', total_views.show_user_carts_price),
    path('revenu', total_views.get_total_revenu_by_year),
    path('location', total_views.search_by_location)

]
