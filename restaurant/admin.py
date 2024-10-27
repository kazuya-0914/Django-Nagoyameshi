from django.contrib import admin
from .models import Category, Restaurant, Reservation, Review, Favorite

admin.site.register(Category)
admin.site.register(Restaurant)
admin.site.register(Reservation)
admin.site.register(Review)
admin.site.register(Favorite)
