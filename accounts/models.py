from django.db import models
from django.contrib.auth.models import AbstractUser

# 拡張ユーザーモデル
class CustomUser(AbstractUser):
    user_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='ユーザー名前')
    hurigana = models.CharField(max_length=128, null=True, blank=True, verbose_name='フリガナ')
    zip_code = models.CharField(max_length=16, null=True, blank=True, verbose_name='郵便番号')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='住所')
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name='電話番号')
    birthday = models.CharField(max_length=20, null=True, blank=True, verbose_name='誕生日')
    job = models.CharField(max_length=255, null=True, blank=True, verbose_name='職業')
    # 有料会員情報　
    is_subscribed = models.BooleanField(default=False, verbose_name='有料会員')
    card_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='カード名義')
    card_number = models.CharField(max_length=128, null=True, blank=True, verbose_name='カード番号')

    class Meta:
        verbose_name_plural = 'CustomUser'

    def __str__(self):
        return self.username

