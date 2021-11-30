from django import forms
from django.forms import ModelForm
from .models import RoomBooking
 
class DateInput(forms.DateInput):
    input_type = 'date'


class DateForm(forms.Form):

    booking_start_date = forms.DateField(widget=DateInput)
    booking_end_date = forms.DateField(widget=DateInput)