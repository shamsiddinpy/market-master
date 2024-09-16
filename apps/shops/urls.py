from apps.shops.views.shops import SellerPageTemplateView
from django.urls import path

urlpatterns = [
    path('', SellerPageTemplateView.as_view(), name='seller_page'),
]
