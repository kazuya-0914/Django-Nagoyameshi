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
    square_customer_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='Square顧客ID')  # Squareの顧客IDを保存
    
    # ダミーフィールド（不要の場合は削除）
    card_name = models.CharField(max_length=128, null=True, blank=True, verbose_name='カード名義')
    card_number = models.CharField(max_length=128, null=True, blank=True, verbose_name='カード番号')

    class Meta:
        verbose_name_plural = 'CustomUser'

    def __str__(self):
        return self.username

# カード情報モデル
class Card(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cards')
    cardholder_name = models.CharField(max_length=128, verbose_name='カード名義')
    brand = models.CharField(max_length=50, verbose_name='カードブランド')
    last_4 = models.CharField(max_length=4, verbose_name='カード番号下4桁')
    exp_month = models.IntegerField(verbose_name='有効期限（月）')
    exp_year = models.IntegerField(verbose_name='有効期限（年）')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日')

    class Meta:
        verbose_name_plural = 'Card'

    def __str__(self):
        return f"{self.brand} - **** **** **** {self.last_4}"