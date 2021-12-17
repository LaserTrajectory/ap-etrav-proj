from django.urls import path, include
from . import views

app_name = 'base'

urlpatterns = [
    path('home', views.home, name='home'),
    path('hotel/<slug>', views.hotels, name='hotel'),
    path('hotels', views.hotel_list, name='hotels'),
    path('hotel-room/<slug>', views.hotel_rooms, name='hotel-room'),
    path('', views.index, name='auth'),
    path('', include("django.contrib.auth.urls")),
    path('', include("social_django.urls", namespace='social')),
    path("logout", views.logout),
    path('profile', views.profile, name='profile'),
    path('recommendations', views.recommendations, name='recommendations'),
    path('success', views.success, name='success'),
    path('booking-pdf', views.booking_pdf, name='booking-pdf'),
    path('search-form', views.search_filter_view, name='search-filter')
]