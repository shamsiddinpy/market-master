from django.contrib.auth import views as auth_views
from django.urls import path

from apps.views.operator import OperatorIndexTemplateView, OperatorOrderListView, OperatorNewListView
from apps.views.products import ProductDetailView, ProductListView, OrderProductSuccessDetailView, \
    MarketProductListView, StreamOrderListView, StreamOrderFormView, StatsListView, \
    OrderListView, UserRequestsListView, AdminPageTemplateView, add_to_wishlist, WishlistCard, SellerPageTemplateView
from apps.views.users import UserSettingUpdateView, UserSettingsImageUpdateView, UserSettingsPassword, \
    CompetitionListView, LoginUserView, LoginBotTemplateView, \
    LoginCheckView, PaymeFormView, PaymeListView, ProfileTemplateView, FavoritesTemplateView, get_districts, \
    logout_view, RegistrationView

urlpatterns = [

    path('', ProductListView.as_view(), name='product_list_page'),
    path('product/<slug:slug>', ProductDetailView.as_view(), name='product_detail_page'),
    path('stream/<int:pk>', ProductDetailView.as_view(), name='product_detail_page'),
    path('product-success/<int:pk>', OrderProductSuccessDetailView.as_view(), name='product_success'),

    path('admin_page', AdminPageTemplateView.as_view(), name='admin_page'),
    path('admin_page/market', MarketProductListView.as_view(), name='market_page'),
    path('admin_page/requests', UserRequestsListView.as_view(), name='user_requests'),
    path('admin_page/urls', StreamOrderListView.as_view(), name='stream_order_list'),
    path('admin_page/stats', StatsListView.as_view(), name='stats_page'),
    path('admin_page/competition', CompetitionListView.as_view(), name='competition'),
    path('admin_page/withdraw', PaymeListView.as_view(), name='withdraw'),
    path('admin_page/payme_add', PaymeFormView.as_view(), name='payme_page'),
    path('admin_page/stream-order', StreamOrderFormView.as_view(), name='stream_order_form'),
    path('add-to-wishlist/<int:product_id>', add_to_wishlist, name='add_to_wishlist'),
    path('admin_page/wishlist', WishlistCard.as_view(), name='wishlist'),

    path('profile', ProfileTemplateView.as_view(), name='profile'),
    path('profile/settings', UserSettingUpdateView.as_view(), name='user_settings_update'),
    path('profile/settings/logout', logout_view, name='logout'),
    path('profile/settings/login', LoginUserView.as_view(), name='login_page'),
    path('profile/settings/register', RegistrationView.as_view(), name='register_page'),
    path('profile/settings/login-message', LoginBotTemplateView.as_view(), name='login_bot'),
    path('profile/settings/login-check', LoginCheckView.as_view(), name='login_check'),
    path('profile/settings/user-image-update', UserSettingsImageUpdateView.as_view(),
         name='settings_images_update'),
    path('profile/orderid-products', OrderListView.as_view(), name='order_products'),
    path('profile/liked-product', FavoritesTemplateView.as_view(), name='favorites'),
    path('profile/settings/user-password-update', UserSettingsPassword.as_view(), name='settings_update_password'),
    path('get_districts', get_districts, name='get_districts'),

]

urlpatterns += [
    path('operator', OperatorIndexTemplateView.as_view(), name='operator_page'),
    path('operator/new', OperatorNewListView.as_view(), name='operator_new'),
    path('operator/order/search', OperatorNewListView.as_view(), name='operator_search'),
    path('operator/prodcut_add', OperatorOrderListView.as_view(), name='operator_order'),

]
urlpatterns += [
    path('seller', SellerPageTemplateView.as_view(), name='seller_page'),
]
