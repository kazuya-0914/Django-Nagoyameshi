from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic, View

from . import forms
from . import models
from .models import CustomUser
from .models import Card

# Square用に追記
import datetime
import json
import uuid
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

# ----- (1) 有料プラン登録 ----- #
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
        # フロントエンドから送られてきたJSONデータを取得
        try:
            data = json.loads(request.body.decode('utf-8'))
            nonce = data.get('nonce')
            idempotency_key = data.get('idempotency_key')  # 一意のキー
        except json.JSONDecodeError:
            # エラーが発生した場合、エラーメッセージをJSONで登録ページに渡す
            error_message = "JSONデータの取得に失敗しました。"
            return JsonResponse({
                'status': 'error',
                'error_message': error_message,
            }, status=400)

        # Square APIクライアントの初期化（本番環境では'sandbox'を'production'に変更）
        client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN,
            environment='sandbox',
        )
        '''
        顧客IDを発行し取得する（subscribe_view関数は下記に記載）
        発行した顧客IDをデータベースに保存する（CustomUserモデルに追加）
        '''
        customer_id = subscribe_view(request, client)
        customer_id = '9QHG1REFKB35NV0VGQ4Y3MYYZG'
        # Squareダッシュボードで作成したPlan Variation IDに置き換える
        plan_variation_id = "WICZNCINOMBV4QUHAXXI7NXL"
        # カードトークンからカードIDを発行する（必ず文字列型）
        card_id = str(save_card(request, client, customer_id, nonce))

        # サブスクリプション作成リクエストのデータ
        body = {
            "idempotency_key": idempotency_key,
            "location_id": settings.SQUARE_LOCATION_ID,
            "plan_variation_id": plan_variation_id,
            "customer_id": customer_id,  # 顧客ID。SquareのCustomer APIで作成する必要あり
            "card_id": card_id,  # 保存済みのカードID
            "start_date": str(datetime.date.today()),  # サブスクリプション開始日
        }

        # サブスクリプションの作成リクエストを送信  
        result = client.subscriptions.create_subscription(body)
        print(result.body)

        if result.is_success():
            # 成功したらカード情報をデータベースに登録し、有料会員に変更（save_cards_to_db関数は下記に記載）
            save_cards_to_db(request, client, customer_id)

            # 成功時にトップページにリダイレクトするようにJSONで返答
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse_lazy('top_page'),  # フロントエンドでリダイレクトするURLを提供
            })
        elif result.is_error():
            # エラーが発生した場合、エラーメッセージをJSONで登録ページに渡す
            error_message = f"【Squareのサブスクリプション登録に失敗しました】<br>{result.errors}"
            return JsonResponse({
                'status': 'error',
                'error_message': error_message,
            }, status=400)

# ----- (2) 有料プラン解約 ----- #
class SubscribeCancelView(generic.TemplateView):
    template_name = 'subscribe/subscribe_cancel.html'

    def post(self, request):
        user_id = request.user.id
        models.CustomUser.objects.filter(id=user_id).update(is_subscribed=False)
        return redirect(reverse_lazy('top_view'))

# ----- (3) クレジットカード変更 ----- #
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

        # print(card_name, card_number)
        # CustomUser.objects.filter(id=user_id).update(card_name=card_name, card_number=card_number)

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

# ----- ■ Square関連関数 ■ ----- #
'''
顧客IDを発行し取得する
発行した顧客IDをデータベースに保存する（CustomUserモデルに追加）
'''
def subscribe_view(request, client):
    # Squareで顧客を作成
    try:
        # 顧客IDを発行し取得する
        customer_id = create_customer(request, client)

        # 取得した顧客IDをデータベースに保存する（CustomUserモデルに追加）
        user = request.user
        user.square_customer_id = customer_id
        user.save()

        return customer_id
    except Exception as e:
        # エラーメッセージをJSONで返す
        error_message = f"【顧客IDのDB登録に失敗しました】<br>{str(e)}"
        return JsonResponse({
            'status': 'error',
            'error_message': error_message,
        }, status=400)

# 顧客IDを発行し取得する
def create_customer(request, client):
    # データベースからユーザー情報を取得
    email = request.user.email

    body = {
        "idempotency_key": str(uuid.uuid4()),  # ユニークキー発行
        "email_address": email, 
    }
    result = client.customers.create_customer(body) # 顧客IDを発行
    if result.is_success():
        return result.body["customer"]["id"]  # 顧客IDを取得
    else:
        # エラーメッセージをJSONで返す
        error_message = f"【Squareの顧客ID発行に失敗しました】<br>{result.errors}"
        return JsonResponse({
            'status': 'error',
            'error_message': error_message,
        }, status=400)

'''
CARD IDを発行し取得する
カード情報をデータベースに登録する（Cardモデルに登録）
有料会員に変更する（CustomUserモデルを更新）
'''
# トークンのカード情報からカードIDを取得する
def save_card(request, client, customer_id, nonce):
    body = {
        "idempotency_key": str(uuid.uuid4()),  # ユニークキー発行
        "source_id": nonce,  # フロントエンドから取得したカードトークン
        "customer_id": customer_id,  # Square API で作成された顧客 ID
    }

    response = client.cards.create_card(body)

    if response.is_success():
        card_id = response.body["card"]["id"]
        return card_id  # 保存されたカードIDを取得
    else:
        # エラーメッセージをJSONで返す
        error_message = f"【カードの保存に失敗しました】<br>{response.errors}"
        return JsonResponse({
            'status': 'error',
            'error_message': error_message,
        }, status=400)

# カード情報の取得
def fetch_customer_cards(request, client, customer_id):
    # Cards APIを使用して顧客に紐づくカード情報を取得
    response = client.cards.list_cards(customer_id=customer_id)

    if response.is_success():
        return response.body.get('cards', [])
    else:
        # エラーメッセージをJSONで返す
        error_message = f"【Squareのカード情報取得に失敗しました】<br>{response.errors}"
        return JsonResponse({
            'status': 'error',
            'error_message': error_message,
        }, status=400)
    
# カード情報をデータベースに登録し、有料会員に変更
def save_cards_to_db(request, client, customer_id):
    try:
        # 有料会員に変更
        CustomUser.objects.filter(id=request.user.id).update(is_subscribed=True)
        # 顧客IDに紐づくカード情報を取得
        cards = fetch_customer_cards(request, client, customer_id)

        for card in cards:
            Card.objects.update_or_create(
                card_id=card['id'],
                defaults={
                    'user': request.user,
                    'cardholder_name': card.get('cardholder_name'),
                    # 以下はSquareで情報取得可能
                    'brand': card['card_brand'],
                    'last_4': card['last_4'],
                    'exp_month': card['exp_month'],
                    'exp_year': card['exp_year'],
                }
            )
    except Exception as e:
        # エラーメッセージをJSONで返す
        error_message = f"【カード情報のDB登録に失敗しました】<br>{str(e)}"
        return JsonResponse({
            'status': 'error',
            'error_message': error_message,
        }, status=400)