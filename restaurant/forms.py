from django import forms
from .models import Reservation, Review

class ReservationCreateForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('date', 'time', 'number_of_people',)

    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)

        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'reservation_date'
        self.fields['date'].widget.attrs['name'] = 'reservation_date'
        self.fields['time'].widget.attrs['class'] = 'form-control'
        self.fields['number_of_people'].widget.attrs['class'] = 'form-control'

class ReviewCreateForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('comment', 'rate')
        widgets = {'rate': forms.RadioSelect()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['comment'].widget.attrs['class'] = 'form-control'
        self.fields['comment'].widget.attrs['cols'] = '30'
        self.fields['comment'].widget.attrs['rows'] = '5'
        self.fields['rate'].widget.attrs['class'] = 'form-check-input'

