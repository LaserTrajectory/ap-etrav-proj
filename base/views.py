from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel

# Create your views here.

def home(request):

    return render(request, "base/home.html")

def hotels(request, slug):

    hotel = get_object_or_404(Hotel, slug=slug)

    context = {
        'hotel': hotel
    }

    return render(request, "base/hotel.html", context)

def hotel_list(request):

    queryset = Hotel.objects.all()

    context = {
        'hotels': queryset
    }

    return render(request, "base/hotel_list.html", context)