from django.contrib import admin
from .models import Category, Restaurant, Reservation, Review, Favorite, Coupon, UsedCoupon, ViewHistory

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Reservation)
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(Coupon) # ■ 2025/1/10 追記 ■
admin.site.register(UsedCoupon) # ■ 2025/1/10 追記 ■
admin.site.register(ViewHistory) # ■ 2025/1/17 追記 ■