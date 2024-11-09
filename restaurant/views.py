from . import models
from django.views import generic

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
