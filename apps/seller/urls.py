from django.urls import path, include

# from apps.seller.view.base import SellerHomeView

urlpatterns = [
    path('', include('apps.seller.telegram.urls')),
    path('', include('apps.seller.shop.urls')),
    path('', include('apps.seller.orders.urls')),

]
