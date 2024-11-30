from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic, View

from . import forms
from . import models
from .models import CustomUser
from .models import Card

# Square用に追記
import json
from django.http import JsonResponse
from django.conf import settings
from square.client import Client

class UserDetailView(generic.DeleteView):
    model = CustomUser
    template_name = 'user/user_detail.html'

class UserUpdateView(generic.UpdateView):
    model = CustomUser
    template_name = 'user/user_update.html'
    form_class = forms.UserUpdateForm

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('user_detail', kwargs={'pk', pk})

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

# --- 有料プラン登録 --- #
class SubscribeRegisterView(View):
    template = 'subscribe/subscribe_register.html'

    # Getメソッド
    def get(self, request):
        context = {
            # Square決済の設定
            'square_application_id': settings.SQUARE_APPLICATION_ID,
            'square_location_id': settings.SQUARE_LOCATION_ID,
        }
        return render(request, self.template, context)

    # Postメソッド
    def post(self, request):
        user_id = request.user.id
        '''
        card_name = request.POST.get('card_name')
        card_number = request.POST.get('card_number')
        '''
        card_name = 'Taro Yamada'
        card_number = '4242424242424242'

        CustomUser.objects.filter(id=user_id) \
        .update(is_subscribed=True, card_name=card_name, card_number=card_number)

        # Square APIクライアントの初期化（本番環境では'sandbox'を'production'に変更）
        client = Client(access_token=settings.SQUARE_ACCESS_TOKEN, environment='sandbox')

        # フロントエンドから送られてきたデータを取得
        nonce = request.POST.get('nonce')
        idempotency_key = request.POST.get('idempotency_key')  # 一意のキー
        plan_id = "あなたのPLAN ID"  # Squareダッシュボードで作成したプランIDに置き換える

        # 顧客ID取得（subscribe_view関数は下記に記載）
        customer_id = subscribe_view(request, client, idempotency_key)

        # サブスクリプション作成リクエストのデータ
        body = {
            "idempotency_key": idempotency_key,
            "location_id": settings.SQUARE_LOCATION_ID,
            "plan_id": plan_id,
            "customer_id": customer_id,  # 顧客ID。SquareのCustomer APIで作成する必要あり
            "card_id": nonce  # フロントエンドでトークン化されたカード情報
        }

        # サブスクリプションの作成リクエストを送信  
        result = client.subscriptions.create_subscription(body)

        if result.is_success():
            # 成功したらカード情報をデータベースに登録（save_cards_to_db関数は下記に記載）
            save_cards_to_db(request, client, customer_id)

            # 成功時にトップページにリダイレクト
            return redirect(reverse_lazy('top_page'))
        else:
            # エラーが発生した場合、エラーメッセージを含むコンテキストを登録ページに渡す
            error_message = "サブスクリプションの登録に失敗しました。"
            if result.errors:
                error_message += ": ".join([error['detail'] for error in result.errors])
            
            context = {
                'error_message': error_message,
            }
            return render(request, self.template, context)
        
        '''
        correct_cord_number = '4242424242424242'
        if card_number != correct_cord_number:
            context = {
                'error_message': 'クレジットカード番号が正しくありません'
            }
            return render(self.request, self.template, context)
        models.CustomUser.objects.filter(id=user_id) \
        .update(is_subscribed=True, card_name=card_name, card_number=card_number)
        return redirect(reverse_lazy('top_page'))
        '''

# --- 有料プラン解約 --- #
class SubscribeCancelView(generic.TemplateView):
    template_name = 'subscribe/subscribe_cancel.html'

    def post(self, request):
        user_id = request.user.id
        models.CustomUser.objects.filter(id=user_id).update(is_subscribed=False)
        return redirect(reverse_lazy('top_view'))

# --- クレジットカード変更 --- #
class SubscribePaymentView(View):
    template = 'subscribe/subscribe_payment.html'

    def get(self, request):
        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)
        context = {
            'user': user,
            # Square決済の設定
            'square_application_id': settings.SQUARE_APPLICATION_ID,
            'square_location_id': settings.SQUARE_LOCATION_ID,
        }
        return render(self.request, self.template, context)

    def post(self, request):
        user_id = request.user.id
        card_name = request.POST.get('card_name')
        card_number = request.POST.get('card_number')

        print(card_name, card_number)
        CustomUser.objects.filter(id=user_id).update(card_name=card_name, card_number=card_number)

        # Square決済リクエストの処理
        client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN, 
            environment='sandbox' # 本番環境では'production'
        )

        body = {
            "source_id": request.POST.get('nonce'),
            "amount_money": {
                "amount": 5000,  # 例: 50.00 USD (最小単位で指定: 5000 cents)
                "currency": "USD"
            },
            "idempotency_key": request.POST.get('idempotency_key'),  # 一意のID
            "location_id": settings.SQUARE_LOCATION_ID,
        }

        result = client.payments.create_payment(body)
        if result.is_success():
            return JsonResponse({"message": "Payment successful!"})
        else:
            return JsonResponse({"errors": result.errors}, status=400)

        # return redirect(reverse_lazy('top_page'))

# --- Square関連関数 --- #
# 顧客ID取得のためのサブスクリプションページ設定
def subscribe_view(request, client, idempotency_key):
    # Squareで顧客を作成
    try:
        # 顧客IDを取得
        customer_id = create_customer(request, client, idempotency_key)

        # 取得した顧客IDをデータベースに保存する（CustomUserモデルに追加）
        user = CustomUser()
        user.square_customer_id = customer_id
        user.save()

        return customer_id
    except Exception as e:
        params = {
            'error_message': f"顧客情報登録に失敗しました: {str(e)}"
        }
        return render(request, 'subscribe/subscribe_register.html', params)

# 顧客IDを取得
def create_customer(request, client ,idempotency_key):
    # データベースからユーザー情報を取得
    email = CustomUser.get("email")

    body = {
        "idempotency_key": idempotency_key,
        "email_address": email, 
        # "given_name": given_name,
        # "family_name": family_name,
    }
    result = client.customers.create_customer(body)
    if result.is_success():
        return result.body["customer"]["id"]  # 顧客IDを取得
    else:
        params = {
            'error_message': Exception(f"顧客情報登録に失敗しました: {result.errors}")
        }
        return render(request, 'subscribe/subscribe_register.html', params)

# カード情報の取得
def fetch_customer_cards(request, client, customer_id):
    # Cards APIを使用して顧客に紐づくカード情報を取得
    response = client.cards.list_cards(customer_id=customer_id)

    if response.is_success():
        return response.body['cards']
    else:
        params = {
            'error_message': Exception(f"カード情報取得に失敗しました: {response.errors}")
        }
        return render(request, 'subscribe/subscribe_register.html', params)
    
# カード情報の一部をデータベースに登録
def save_cards_to_db(request, client, customer_id):
    try:
        # 顧客IDに紐づくカード情報を取得
        cards = fetch_customer_cards(request, client, customer_id)

        for card in cards:
            Card.objects.update_or_create(
                card_id=card['id'],
                defaults={
                    'customer_id': customer_id,
                    'cardholder_name': card.get('cardholder_name'),
                    'brand': card['card_brand'],
                    'last_4': card['last_4'],
                    'exp_month': card['exp_month'],
                    'exp_year': card['exp_year'],
                }
            )
    except Exception as e:
        params = {
            'error_message': f"カード情報登録に失敗しました: {str(e)}"
        }
        return render(request, 'subscribe/subscribe_register.html', params)