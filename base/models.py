from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from country_list import countries_for_language
from django.core.validators import MaxValueValidator, MinValueValidator

countries = countries_for_language('en')

# Create your models here.

class Location(models.Model):

    COUNTRY_CHOICES = countries

    country = models.CharField(
        max_length=30,
        choices=COUNTRY_CHOICES,
        default='IN'
    )
    city = models.CharField(max_length=100)

    def __str__(self):

        return "{0}, {1}".format(self.city, self.country)

class Hotel(models.Model):

    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=True, null=True)

    hotel_name = models.CharField(max_length=100)

    hotel_rating = models.IntegerField(default=1, validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])

    def __str__(self):

        return "{0}: {1} | {2} stars".format(self.hotel_name, self.location, self.hotel_rating)

class HotelRoom(models.Model):

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_number = models.IntegerField(blank=False, default='000')
    is_booked = models.BooleanField(default=False)

    def __str__(self):

        return "{0}: #{1}".format(self.hotel.hotel_name, self.room_number)

class RoomBooking(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            blank=True, null=True)
    room = models.ForeignKey(HotelRoom, on_delete=models.CASCADE)
    date_booked = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return "{0}: {1} #{2} @ {3}".format(self.user.username, 
                                         self.room.hotel.hotel_name, 
                                         self.room.room_number,
                                         self.date_booked)