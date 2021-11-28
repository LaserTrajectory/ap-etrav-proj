from django.contrib import admin
from .models import Location, Hotel, HotelRoom, RoomBooking
# Register your models here.

admin.site.register(Location)
admin.site.register(Hotel)
admin.site.register(HotelRoom)
admin.site.register(RoomBooking)
