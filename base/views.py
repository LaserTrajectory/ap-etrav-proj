from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel, HotelRoom, RoomBooking, HotelReview
from .forms import DateForm
from django.contrib.auth import logout as log_out
from urllib.parse import urlencode
from django.conf import settings
from django.http import HttpResponseRedirect

# Create your views here.

def home(request):

    return render(request, "base/home.html")

def hotels(request, slug):

    hotel = get_object_or_404(Hotel, slug=slug)

    rooms = HotelRoom.objects.filter(hotel=hotel)

    if request.method == 'POST':

        rev_content = request.POST.get('review', '')

        rating = request.POST.get('rating', '')

        print(rev_content)
        print(type(rating))

        review = HotelReview.objects.create(user=request.user, hotel=hotel, review=rev_content, user_rating=int(rating))

    reviews_list = HotelReview.objects.filter(hotel=hotel)

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'reviews': reviews_list
    }

    return render(request, "base/hotel.html", context)

def hotel_list(request):

    queryset = Hotel.objects.all()

    context = {
        'hotels': queryset
    }

    return render(request, "base/hotel_list.html", context)

def hotel_rooms(request, slug):

    # https://stackoverflow.com/questions/3367091/whats-the-cleanest-simplest-to-get-running-datepicker-in-django

    hotel_room = get_object_or_404(HotelRoom, slug=slug)

    context = {
        'room': hotel_room
    }

    if request.method == 'GET':

        form = DateForm()
        print(request.GET.get(''))
        context['form'] = form
        return render(request, "base/hotel-room.html", context)

    if request.method == 'POST':

        form = DateForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['booking_start_date']
            end_date = form.cleaned_data['booking_end_date']
            # print("start:", start_date)
            # print("end:", end_date)
            RoomBooking.objects.create(user=request.user, 
            room=hotel_room, booking_start_date=start_date, 
            booking_end_date=end_date)
            hotel_room.is_booked = True
            hotel_room.save()
            return redirect("base:home")

    return render(request, "base/hotel-room.html", context)

def index(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'base/home.html')
    else:
        return render(request, 'base/index.html')

def logout(request):
    log_out(request)
    return_to = urlencode({"returnTo": request.build_absolute_uri("/")})
    logout_url = "https://{}/v2/logout?client_id={}&{}".format(
        settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to,
    )
    return HttpResponseRedirect(logout_url)