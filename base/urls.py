from django.urls import path, include
from . import views

app_name = 'base'

urlpatterns = [
    path('home', views.home, name='home'),
    path('hotel/<slug>', views.hotels, name='hotel'),
    path('hotels', views.hotel_list, name='hotels')
]