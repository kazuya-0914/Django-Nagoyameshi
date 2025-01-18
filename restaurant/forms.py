from django import forms
from django.utils import timezone  # ■ 2025/1/10 追記 ■
from .models import Reservation, Review, Coupon  # ■ 2025/1/10 追記 ■
from django.core.exceptions import ValidationError  # ■ 2025/1/10 追記 ■

class ReservationCreateForm(forms.ModelForm):
    # ■ 2025/1/10 追記 ■
    coupon = forms.ModelChoiceField(
        queryset=Coupon.objects.filter(expiration_date__gte=timezone.now()),
        required=False,  # クーポンは必須ではない
        label='クーポン'
    )
    class Meta:
        model = Reservation
        fields = ('date', 'time', 'number_of_people', 'coupon',) # ■ 2025/1/10 追記 ■

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None) # ■ 2025/1/18 追記 ■
        super().__init__(*args, **kwargs)

        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['date'].widget.attrs['id'] = 'reservation_date'
        self.fields['date'].widget.attrs['name'] = 'reservation_date'
        self.fields['time'].widget.attrs['class'] = 'form-control'
        self.fields['number_of_people'].widget.attrs['class'] = 'form-control'
        self.fields['coupon'].widget.attrs['class'] = 'form-control'  # ■ 2025/1/10 追記 ■

        # ■ 2025/1/18 追記 ■
        if restaurant:
            self.fields['coupon'].queryset = Coupon.objects.filter(
            restaurant=restaurant,
            expiration_date__gte=timezone.now()
        )
        
    # ■ 2025/1/10 追記 ■
    def clean_coupon(self):
        coupon = self.cleaned_data.get('coupon')
        if coupon and coupon.expiration_date < timezone.now().date():
            raise ValidationError("選択したクーポンは有効期限が切れています。")
        return coupon

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

