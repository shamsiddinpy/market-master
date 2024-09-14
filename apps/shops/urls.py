from django.contrib.auth import views as auth_views
from django.urls import path

from apps.views.operator import OperatorIndexTemplateView, OperatorOrderListView, OperatorNewListView
from apps.views.products import ProductDetailView, ProductListView, OrderProductSuccessDetailView, \
    MarketProductListView, StreamOrderListView, StreamOrderFormView, StatsListView, \
    OrderListView, UserRequestsListView, AdminPageTemplateView, add_to_wishlist, WishlistCard
from apps.views.users import UserSettingUpdateView, UserSettingsImageUpdateView, UserSettingsPassword, \
    CompetitionListView, LoginUserView, LoginBotTemplateView, \
    LoginCheckView, PaymeFormView, PaymeListView, ProfileTemplateView, FavoritesTemplateView, get_districts, \
    logout_view, RegistrationView

urlpatterns = [

    # path('', ProductListView.as_view(), name='product_list_page'),

]
