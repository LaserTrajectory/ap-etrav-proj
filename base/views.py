from django.shortcuts import render, redirect, get_object_or_404
from .models import Hotel, HotelRoom, Location, RoomBooking, HotelReview
from .forms import DateForm
from django.contrib.auth import logout as log_out
from urllib.parse import urlencode
from django.conf import settings
from django.http import HttpResponseRedirect, response
import datetime

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Create your views here.

def booking_pdf(request):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter, bottomup=0)
    text_object = c.beginText()
    text_object.setTextOrigin(inch, inch)
    text_object.setFont("Helvetica", 14)

    booking_list = RoomBooking.objects.filter(user=request.user)
    latest_index = len(booking_list) - 1
    booking = booking_list[latest_index]


    # format the lines properly so that the pdf looks decent
    lines = []
    lines.append("Booked by: " + str(booking.user.username))
    lines.append("Booked at: " + str(booking.date_booked))
    lines.append("Booked from: " + str(booking.booking_start_date))
    lines.append("Booked till: " + str(booking.booking_end_date))
    lines.append("Hotel: " + str(booking.room.hotel))
    lines.append("Hotel room:" + str(booking.room.room_number))

    print(lines)

    for line in lines:
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="booking.pdf")


def home(request):

    context = {}

    return render(request, "base/home.html", context)

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

    print(datetime.datetime.now())

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
            return redirect("base:success")

    return render(request, "base/hotel-room.html", context)

def index(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'base/recommendations.html')
    else:
        return render(request, 'base/index.html')

def logout(request):
    log_out(request)
    return_to = urlencode({"returnTo": request.build_absolute_uri("/")})
    logout_url = "https://{}/v2/logout?client_id={}&{}".format(
        settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to,
    )
    return HttpResponseRedirect(logout_url)

def profile(request):

    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    bookings = RoomBooking.objects.filter(user=user)

    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        'email': auth0user.extra_data['email'],
    }

    user_name = user.first_name

    context = {
        'auth0User': auth0user,
        'userdata': userdata,
        'user_name': user_name,
        'bookings': bookings
    }

    return render(request, "base/profile.html", context)

def recommendations(request):

    return render(request, "base/recommendations.html")

def success(request):

    booking_list = RoomBooking.objects.filter(user=request.user)
    latest_index = len(booking_list) - 1
    print(booking_list[latest_index])
    print(booking_list[latest_index].user.username)

    return render(request, "base/success.html")

def search_filter_view(request):

    location_contains = request.GET.get('location_contains')
    hotel_contains = request.GET.get('hotel_contains')
    locations = Location.objects.all()
    location_set = []
    for loc in locations:
        location_set.append(loc.country)
    location_selected = request.GET.get('location')
    # print(location_contains)
    # print("cat sel:", location_selected)
    # print(location_set)
    ratings = request.GET.get('ratings')
    print('val:', ratings)
    queryset = Hotel.objects.all()

    # print(location_contains)

    if location_contains != '' and location_contains is not None:

        queryset = Hotel.objects.filter(location__city__icontains=location_contains)
        print(queryset)

    elif hotel_contains != '' and hotel_contains is not None:

        queryset = Hotel.objects.filter(hotel_name__icontains=hotel_contains)
        print(queryset)

    elif location_selected != '' and location_selected is not None and location_selected != "Choose...":

        queryset = Hotel.objects.filter(location__country=location_selected)
 
    elif ratings != '' and ratings is not None:

        queryset = Hotel.objects.filter(hotel_rating=ratings)


    context = {
        'loc_set': location_set,
        'queryset': queryset,
    }


    return render(request, "base/search_filter_form.html", context)    

def my_booking_view(request):

    bookings = RoomBooking.objects.filter(user=request.user)

    context = {
        'bookings': bookings
    }

    return render(request, "base/my-bookings.html", context)

def contact_us_view(request):

    return render(request, "base/contact-us.html")