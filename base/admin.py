from django.contrib import admin
from .models import Location, Hotel, HotelRoom, RoomBooking, HotelReview
# Register your models here.

admin.site.register(Location)
admin.site.register(Hotel)
admin.site.register(HotelRoom)
admin.site.register(RoomBooking)
admin.site.register(HotelReview)
