import datetime

from accounts.models import CustomUser
from django.db import models

# カテゴリーモデル
class Category(models.Model):
    name = models.CharField(verbose_name='カテゴリー名', max_length=64)
    photo = models.ImageField(verbose_name='写真', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Category'

    def __str__(self):
        return self.name

# レストランモデル
class Restaurant(models.Model):
    name = models.CharField(verbose_name='店舗名', max_length=64)
    description = models.CharField(verbose_name='説明', max_length=128)
    price = models.CharField(verbose_name='価格帯', max_length=32)
    zip_code = models.CharField(verbose_name='郵便番号', max_length=32)
    address = models.CharField(verbose_name='住所', max_length=128)
    business_time = models.CharField(verbose_name='営業時間', max_length=64)
    close_day_of_week = models.CharField(verbose_name='定休日', max_length=32)
    seats_number = models.CharField(verbose_name='座席数', max_length=32)
    category = models.ForeignKey(Category, verbose_name='カテゴリー', on_delete=models.PROTECT)
    rate = models.FloatField(verbose_name='レート', default=0.0)
    review_num = models.IntegerField(verbose_name='レビュー数', default=0)
    reservation_num = models.IntegerField(verbose_name='予約数', default=0)
    photo = models.ImageField(verbose_name='写真', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Restaurant'
    
    def __str__(self):
        return self.name

# 予約モデル
class Reservation(models.Model):
    TIMES = (
        ('', '選択してください'), (datetime.time(2, 3), '2:30'),
        (datetime.time(3, 0), '3:00'), (datetime.time(3, 30), '3:30'), (datetime.time(4, 0), '4:00'),
        (datetime.time(4, 30), '4:30'),
        (datetime.time(5, 0), '5:00'), (datetime.time(5, 30), '5:30'), (datetime.time(6, 0), '6:00'),
        (datetime.time(6, 30), '6:30'),
        (datetime.time(7, 0), '7:00'), (datetime.time(7, 30), '7:30'), (datetime.time(8, 0), '8:00'),
        (datetime.time(8, 30), '8:30'),
        (datetime.time(9, 0), '9:00'), (datetime.time(9, 30), '9:30'), (datetime.time(10, 0), '10:00'),
        (datetime.time(10, 30), '10:30'),
    )

    NUMBER_OF_PEOPLE = (
        ('', '選択してください'), (1, '1名'), (2, '2名'), (3, '3名'), (4, '4名'), (5, '5名'), (6, '6名'), (7, '7名'),
        (8, '8名'), (9, '9名'), (10, '10名'),
        (11, '11名'), (12, '12名'), (13, '13名'), (14, '14名'), (15, '15名'), (16, '16名'), (17, '17名'), (18, '18名'),
        (19, '19名'), (20, '20名'),
        (21, '21名'), (22, '22名'), (23, '23名'), (24, '24名'), (25, '25名'), (26, '26名'), (27, '27名'), (28, '28名'),
        (29, '29名'), (30, '30名'),
        (31, '31名'), (32, '32名'), (33, '33名'), (34, '34名'), (35, '35名'), (36, '36名'), (37, '37名'), (38, '38名'),
        (39, '39名'), (40, '40名'),
        (41, '41名'), (42, '42名'), (43, '43名'), (44, '44名'), (45, '45名'), (46, '46名'), (47, '47名'), (48, '48名'),
        (49, '49名'), (50, '50名'),
    )

    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
    date = models.DateField(verbose_name='予約日')
    time = models.TimeField(verbose_name='時間', choices=TIMES, default='')
    number_of_people = models.IntegerField(verbose_name='人数', choices=NUMBER_OF_PEOPLE, default='')
    created_at = models.DateTimeField(verbose_name='予約申し込み日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='予約更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Reservation'

    def __str__(self):
        return self.restaurant.name
# レビューモデル
class Review(models.Model):
    RATES = ((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'))

    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
    rate = models.IntegerField(verbose_name='レート', default=5, choices=RATES)
    comment = models.TextField(verbose_name='コメント', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='レビュー作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='レビュー更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Review'

    def __str__(self):
        return self.restaurant.name
# お気に入りモデル
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, verbose_name='レストラン', on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name='お気に入り登録日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='お気に入り更新日時', auto_now=True)

    class Meta:
        verbose_name_plural = 'Favorite'

    def __str__(self):
        return self.restaurant.name
