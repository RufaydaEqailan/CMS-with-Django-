from django.urls import path
from ..views import views

urlpatterns = [
    # path('show',views.show),
    path('set', views.Set_test_old_users),
]
