from django.db.models import Avg
from django.db.models import Q
from django.shortcuts import render
from django.views import generic

from . import models

class TopPageView(generic.ListView):
  template_name = "top_page.html"
  model = models.Restaurant
  queryset = models.Restaurant.objects.order_by('-rate')
  context_object_name = 'restaurant_list'

# 会社概要
class CompanyView(generic.TemplateView):
    template_name = "layout/company.html"
# 利用規約
class TermsView(generic.TemplateView):
    template_name = "layout/terms.html"

# トップ画面
class TopPageView(generic.ListView):
    template_name = "top_page.html"
    model = models.Restaurant
    queryset = models.Restaurant.objects.order_by('-rate')
    context_object_name = 'restaurant_list'

    def get_context_data(self, **kwargs):
        if 'price_session' in self.request.session:
            self.request.session['price_session'] = 0
        if 'keyword_session' in self.request.session:
            self.request.session['keyword_session'] = ''
        if 'category_session' in self.request.session:
            self.request.session['category_session'] = ''
        if 'select_sort' in self.request.session:
            self.request.session['select_sort'] = '-created_at'

        context = super(TopPageView, self).get_context_data(**kwargs)
        category_list = models.Category.objects.all()
        new_restaurant_list = models.Restaurant.objects.all().order_by('-created_at')

        context.update({
            'category_list': category_list,
            'new_restaurant_list': new_restaurant_list,
        })
        return context
    
# レストラン詳細画面
class RestaurantDetailView(generic.DetailView):
    template_name = "restaurant/restaurant_detail.html"
    model = models.Restaurant

# レストラン一覧画面
class RestaurantListView(generic.ListView):
    template_name = "restaurant_list.html"
    model = models.Restaurant

    def get_context_data(self, **kwargs):
        context = super(RestaurantListView, self).get_context_data(**kwargs)

        # get input value
        keyword = self.request.GET.get('keyword')
        category = self.request.GET.get('category')
        price = self.request.GET.get('price')
        select_sort = self.request.GET.get('select_sort')
        button_type = self.request.GET.get('button_type')

        keyword = keyword if keyword is not None else ''
        category = category if category is not None else ''
        price = price if price is not None else '0'
        select_sort = select_sort if select_sort is not None else '-created_at'

        # session control
        self.request.session['select_sort'] = select_sort

        if button_type == 'keyword':
            self.request.session['keyword_session'] = keyword
            self.request.session['category_session'] = ''
            self.request.session['price_session'] = '0'

        if button_type == 'category':
            self.request.session['category_session'] = category
            self.request.session['keyword_session'] = ''
            self.request.session['price_session'] = '0'

        if button_type == 'price':
            self.request.session['price_session'] = price
            self.request.session['keyword_session'] = ''
            self.request.session['category_session'] = ''

        if button_type == 'select_sort':
            self.request.session['select_sort'] = select_sort

        keyword_session = self.request.session.get('keyword_session')
        category_session = self.request.session.get('category_session')
        price_session = self.request.session.get('price_session')
        select_sort_session = self.request.session.get('select_sort')

        # filtering queryset
        restaurant_list = models.Restaurant.objects.filter(
            Q(name__icontains=keyword_session) | Q(address__icontains=keyword_session) | Q(
                category__name__icontains=keyword_session))
        restaurant_list = restaurant_list.filter(category__name__icontains=category_session)

        if int(price_session) > 0:
            restaurant_data = models.Restaurant.objects.values('id', 'price')
            target_id_list = []

            for data in restaurant_data:
                price_str = data['price']
                price_str = price_str.replace('円', '')
                price_str = price_str.replace(',', '')
                price_list = price_str.split('～')

                if int(price_list[0]) <= int(price_session) <= int(price_list[1]):
                    target_id_list.append(data['id'])
            restaurant_list = restaurant_list.filter(id__in=target_id_list)

        # 表示順
        restaurant_list = restaurant_list.order_by(select_sort_session)

        category_list = models.Category.objects.all()

        # querysetに含まれるレストランの平均レートを、レストランごとに取得して配列に格納
        average_rate_list = []
        average_rate_star_list = []
        rate_num_list = []

        for restaurant in restaurant_list:
            average_rate = models.Review.objects.filter(restaurant=restaurant).aggregate(Avg('rate'))
            average_rate = average_rate['rate__avg'] if average_rate['rate__avg'] is not None else 0
            average_rate_list.append(round(average_rate, 2))

            if average_rate % 1 == 0:
                average_rate = int(average_rate)
            else:
                average_rate = round(average_rate * 2) / 2
            average_rate_star_list.append(average_rate)

            rate_num = models.Review.objects.filter(restaurant=restaurant).count()
            rate_num_list.append(rate_num)

        context.update({
            'category_list': category_list,
            'keyword_session': keyword_session,
            'category_session': category_session,
            'price_session': price_session,
            'select_sort_session': select_sort_session,
            'restaurant_list': zip(restaurant_list, average_rate_list, average_rate_star_list, rate_num_list),
        })

        return context
