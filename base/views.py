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
import random

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

    text_object.textLine("Ayubowan")
    text_object.textLine("------------------------------------------------------------------")
    text_object.textLine("Hotel Room Booking Acknowledgement")
    text_object.textLine("------------------------------------------------------------------")


    # format the lines properly so that the pdf looks decent
    lines = []
    # lines.append("AYUBOWAN Hotel Booking")
    lines.append("")
    lines.append("Booked by: " + str(booking.user.username))
    lines.append("")
    lines.append("Booked at: " + str(booking.date_booked))
    lines.append("")
    lines.append("Booked from: " + str(booking.booking_start_date))
    lines.append("")
    lines.append("Booked till: " + str(booking.booking_end_date))
    lines.append("")
    lines.append("Hotel: " + str(booking.room.hotel))
    lines.append("")
    lines.append("Hotel room: " + str(booking.room.room_number))

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

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

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

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    print(datetime.datetime.now())

    return render(request, "base/hotel.html", context)

def hotel_list(request):

    queryset = Hotel.objects.all()

    context = {
        'hotels': queryset
    }

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/hotel_list.html", context)

def hotel_rooms(request, slug):

    # https://stackoverflow.com/questions/3367091/whats-the-cleanest-simplest-to-get-running-datepicker-in-django

    hotel_room = get_object_or_404(HotelRoom, slug=slug)

    context = {
        'room': hotel_room
    }

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

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

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/profile.html", context)

def recommendations(request):

    top_3_locations = []
    loc_set = set()

    bookings = RoomBooking.objects.filter(user=request.user)

    # print(bookings)
    book_count = bookings.count()

    top_3_locations.append("US")
    top_3_locations.append("IN")
    top_3_locations.append("LK")

    if book_count != 0:

        for booking in bookings:

            loc_set.add(booking.room.hotel.location.country)

    for loc in top_3_locations:

        loc_set.add(loc)

    # print(loc_set)

    final_locs = random.sample(list(loc_set), 3)

    # print(final_locs)

    qs_loc_1 = Hotel.objects.filter(location__country=final_locs[0])
    qs_loc_2 = Hotel.objects.filter(location__country=final_locs[1])
    qs_loc_3 = Hotel.objects.filter(location__country=final_locs[2])

    # print(qs_loc_1)
    # print(qs_loc_2)
    # print(qs_loc_3)


    context = {
        'final_loc_1': final_locs[0],
        'final_loc_2': final_locs[1],
        'final_loc_3': final_locs[2],
        'qs_loc_1': qs_loc_1,
        'qs_loc_2': qs_loc_2,
        'qs_loc_3': qs_loc_3

    }

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/recommendations.html", context)

def success(request):

    booking_list = RoomBooking.objects.filter(user=request.user)
    latest_index = len(booking_list) - 1
    print(booking_list[latest_index])
    print(booking_list[latest_index].user.username)

    context = {}

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/success.html", context)

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
    loc_set = set(location_set)

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

    qs_count = 0

    for i in queryset:
        qs_count += 1

    context = {
        'loc_set': loc_set,
        'queryset': queryset,
        'qs_count': qs_count
    }

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/search_filter_form.html", context)

def my_booking_view(request):

    bookings = RoomBooking.objects.filter(user=request.user)

    context = {
        'bookings': bookings
    }

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/my-bookings.html", context)

def contact_us_view(request):

    context = {}

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/contact-us.html", context)

def about_us_view(request):

    context = {}

    context['picture'] = request.user.social_auth.get(provider='auth0').extra_data['picture']

    return render(request, "base/about-us.html", context)