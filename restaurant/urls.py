from django.urls import path
from . import views

urlpatterns = [
  path('', views.TopPageView.as_view(), name="top_page"),
  path("company/", views.CompanyView.as_view(), name="company_page"),
  path("terms/", views.TermsView.as_view(), name="terms_page"),
]
