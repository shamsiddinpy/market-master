from django.urls import path, include

from apps.seller.shop.views.dashboard import DashboardTemplateView

urlpatterns = [
    path('dashboard', DashboardTemplateView.as_view(), name='dashboard'),
]
