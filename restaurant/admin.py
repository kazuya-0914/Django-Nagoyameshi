from django.contrib import admin
from .models import Category, Restaurant, Reservation, Review, Favorite

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Reservation)
admin.site.register(Review)
admin.site.register(Favorite)
