from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.models import Product, Category, ProductImages, User
from apps.models.products import Order, Region, District, Stream, Competition, SiteSetting
from apps.models.users import PaymeRequest, BalanceReport


@admin.register(Product)
class ProductModelAdmin(TranslatableAdmin):
    pass


@admin.register(Category)
class CategoryModelAdmin(TranslatableAdmin):
    search_fields = ('name', 'author__name')


@admin.register(ProductImages)
class ProductImagesModelAdmin(ModelAdmin):
    list_display = ('headshot_image',)

    def headshot_image(self, obj):
        if obj.image:
            return mark_safe('<img src="{url}" width="{width}" height="{height}" />'.format(
                url=obj.image.url,
                width=obj.image.width,
                height=obj.image.height,
            ))

    headshot_image.short_description = 'Product Image'


@admin.register(Order)
class OrderModelAdmin(ModelAdmin):
    pass


@admin.register(Region)
class RegionModelAdmin(TranslatableAdmin):
    pass


@admin.register(District)
class DistrictModelAdmin(TranslatableAdmin):
    pass


@admin.register(Stream)
class StreamModelAdmin(ModelAdmin):
    pass


@admin.register(Competition)
class CompetitionModelAdmin(ModelAdmin):
    pass


@admin.register(SiteSetting)
class SiteSettingModelAdmin(TranslatableAdmin):
    list_display = ('name', 'delivery_to', 'operator_to', 'minimal_sum')
    search_fields = ('name',)


@admin.register(BalanceReport)
class BalanceReportModelAdmin(ModelAdmin):
    list_display = ('role', 'real_balance', 'expected_balance')
    search_fields = ('role',)


@admin.register(PaymeRequest)
class PaymeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'card_number')

    def save_model(self, request, obj, form, change):
        if obj.status == PaymeRequest.Status.PAID:
            user = obj.user
            user.amount_paid += obj.amount
            user.save()
        super().save_model(request, obj, form, change)


@admin.register(User)
class CustomUserModelAdmin(ModelAdmin):
    ordering = ['first_name']
    list_display = ("phone", "email", "first_name", "last_name", "is_staff")
    search_fields = ("phone", "first_name", "last_name", "email")

    fieldsets = (
        (None, {"fields": ("avatar", "phone", "password"), }),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "description", "amount_paid")}),
        (
            _("Permissions"),
            {
                'fields': (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")})
    )


def get_app_list(self, request):
    custom_order = [
        _('New Orders'),
        _('Visit Orders'),
        _('Ready Orders'),
        _('Delivery Orders'),
        _('Delivered Orders'),
        _('Cancelled Orders'),
        _('Missed Call Orders'),
        _('Archived Orders'),
        _('Courier Users'),
        _('Operator Users'),
        _('Manager Users'),
        _('Admin Users'),
        _('Users'),
        _('Orders'),
        _('Products'),
        _('Product Images'),
        _('Categories'),
        _('Regions'),
        _('Districts'),
        _('Site Settings'),
        _('Streams'),
        _('Competitions'),
        _('Payments'),
        _('User Balances'),
        _('Site Settings'),
        _('Balance Report')
    ]

    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

    def sort_key(model):
        try:
            return custom_order.index(model['name'])
        except ValueError:
            return len(custom_order)

    for app in app_list:
        if app['app_label'] == 'apps':
            app['models'].sort(key=sort_key)

    return app_list


admin.AdminSite.get_app_list = get_app_list
