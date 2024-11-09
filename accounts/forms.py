from allauth.account.forms import SignupForm, LoginForm
from django import forms

from .models import CustomUser

class MySignupForm(SignupForm):
    user_name = forms.CharField(max_length=255, label='氏名')
    hurigana = forms.CharField(max_length=255, label='フリガナ')
    zip_code = forms.CharField(max_length=255, label='郵便番号')
    address = forms.CharField(max_length=255, label='住所')
    phone_number = forms.CharField(max_length=255, label='電話番号')
    birthday = forms.CharField(max_length=255, label='誕生日')
    job = forms.CharField(max_length=255, label='職業')
    is_subscribed = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(MySignupForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '侍 太郎'})
        self.fields['hurigana'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'サムライ タロウ'})
        self.fields['zip_code'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1010022'})
        self.fields['address'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '東京都千代田区神田棟堀町300番地'})
        self.fields['phone_number'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '09012345678'})
        self.fields['birthday'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '19950401'})
        self.fields['job'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'エンジニア'})

        self.fields['email'].widget = forms.TextInput(
            attrs={'type': 'email', 'class': 'form-control', 'placeholder': 'taro.samurai@example.com'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})

    def signup(self, request, user):
        user.user_name = self.cleaned_data['user_name']
        user.hurigana = self.cleaned_data['hurigana']
        user.zip_code = self.cleaned_data['zip_code']
        user.address = self.cleaned_data['address']
        user.phone_number = self.cleaned_data['phone_number']
        user.birthday = self.cleaned_data['birthday']
        user.job = self.cleaned_data['job']
        user.save()
        return user


class MyLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(
            attrs={'type': 'email', 'class': 'form-control', 'placeholder': 'メールアドレス'})
        self.fields['password'].widget = forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'パスワード'})


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'user_name', 'hurigana', 'zip_code', 'address', 'phone_number', 'birthday', 'job', 'email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '侍 太郎'})
        self.fields['hurigana'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'サムライ タロ'})
        self.fields['zip_code'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1010022'})
        self.fields['address'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '東京都千代田区神田棟堀町300番地'})
        self.fields['phone_number'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': '09012345678'})
        self.fields['birthday'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': '19950401'})
        self.fields['job'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'エンジニア'})

        self.fields['email'].widget = forms.TextInput(
            attrs={'type': 'email', 'class': 'form-control', 'placeholder': 'taro.samurai@example.com'})
