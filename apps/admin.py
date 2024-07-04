from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, F, Value, DecimalField, Min, Max
from django.db.models.functions import Coalesce, TruncMonth
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from djangoql.admin import DjangoQLSearchMixin

from apps.models import Product, Category, ProductImages, User, Profile, PaymeRequest
from apps.models.products import Order, Region, District, Stream, Competition, SiteSetting
from apps.models.proxy import BalanceReport, AdminUser, CurrierUser, OperatorUser, ManagerUser, NewOrders, VisitOrders, \
    ReadyOrders, DeliveryOrders, DeliveredOrders, CanceledOrders, ArchivedOrders, PhoneOrder


@admin.register(Product)
class ProductModelAdmin(ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'name': ('name',)}
    list_per_page = 20


@admin.register(Category)
class CategoryModelAdmin(DjangoQLSearchMixin, ModelAdmin):
    search_fields = ('name',)


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
class RegionModelAdmin(ModelAdmin):
    pass


@admin.register(District)
class DistrictModelAdmin(ModelAdmin):
    pass


@admin.register(Stream)
class StreamModelAdmin(ModelAdmin):
    pass


@admin.register(Competition)
class CompetitionModelAdmin(ModelAdmin):
    pass


@admin.register(SiteSetting)
class SiteSettingModelAdmin(ModelAdmin):
    list_display = ('name', 'delivery_to', 'operator_to', 'minimal_sum')
    search_fields = ('name',)

    def has_add_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj)


@admin.register(BalanceReport)
class ReportModelAdmin(admin.ModelAdmin):
    change_list_template = "apps/admin/balance_report.html"
    date_hierarchy = 'created_at'
    list_filter = ("status",)

    def has_add_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request, extra_context=extra_context
        )

        try:
            queryset = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        # Calculate balances
        operator_balance = (
                User.objects.filter(status=User.Status.OPERATOR).aggregate(
                    total_balance=Sum("main_balance")
                )["total_balance"]
                or 0
        )
        admin_balance = (
                User.objects.filter(status=User.Status.ADMIN).aggregate(
                    total_balance=Sum("main_balance")
                )["total_balance"]
                or 0
        )
        user_balance = (
                User.objects.filter(status=User.Status.USERS).aggregate(
                    total_balance=Sum("main_balance")
                )["total_balance"]
                or 0
        )
        total_balance = (
                User.objects.aggregate(total_balance=Sum("main_balance"))[
                    "total_balance"
                ]
                or 0
        )

        site_settings = SiteSetting.objects.first()
        operator_to = site_settings.operator_to if site_settings else 0

        operator_order_count = Order.objects.filter(
            operator__isnull=False
        ).count()
        operator_possible_balance = (
                operator_balance + operator_order_count * operator_to
        )

        admin_possible_balance = admin_balance  # Assuming admin balance remains unchanged for estimation

        user_referral_reward = Order.objects.filter(
            referral_user__isnull=False
        ).aggregate(
            total_referral_reward=Coalesce(
                Sum(F("product__referral_reward"), output_field=DecimalField()),
                Value(0, output_field=DecimalField())
            )
        )["total_referral_reward"]
        user_possible_balance = user_balance + user_referral_reward

        possible_total_balance = (
                operator_possible_balance + user_possible_balance + admin_possible_balance
        )

        # Summary over time
        period = get_next_in_date_hierarchy(request, self.date_hierarchy)
        if period:
            summary_over_time = (
                queryset.annotate(
                    period=TruncMonth(
                        "created_at")
                )
                .values("period")
                .annotate(total_balance=Sum("main_balance"))
                .order_by("period")
            )

            summary_range = summary_over_time.aggregate(
                low=Min("total_balance"),
                high=Max("total_balance"),
            )
            high = summary_range.get("high", 0)
            low = summary_range.get("low", 0)

            response.context_data["summary_over_time"] = [
                {
                    "period": x["period"],
                    "total": x["total_balance"] or 0,
                    "pct": (
                        ((x["total_balance"] or 0) - low) / (high - low) * 100
                        if high > low
                        else 0
                    ),
                }
                for x in summary_over_time
            ]

        # Add balances to context
        response.context_data.update(
            {
                "operator_balance": operator_balance,
                "admin_balance": admin_balance,
                "user_balance": user_balance,
                "total_balance": total_balance,
                "operator_possible_balance": operator_possible_balance,
                "admin_possible_balance": admin_possible_balance,
                "user_possible_balance": user_possible_balance,
                "possible_total_balance": possible_total_balance,
            }
        )

        return response


def get_next_in_date_hierarchy(request, date_hierarchy):
    if date_hierarchy is None:
        return None
    if date_hierarchy + "__day" in request.GET:
        return "hour"
    elif date_hierarchy + "__month" in request.GET:
        return "day"
    elif date_hierarchy + "__year" in request.GET:
        return "month"
    else:
        return "year"


@admin.register(PaymeRequest)
class PaymeRequestAdmin(ModelAdmin):
    list_display = ('user', 'card_number', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'card_number')

    def save_model(self, request, obj, form, change):
        if obj.status == PaymeRequest.Status.PAID:
            user = obj.user
            user.amount_paid += obj.amount
            user.save()
        super().save_model(request, obj, form, change)


class CustomUserAdmin(UserAdmin):
    ordering = 'phone',
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2"),
            },
        ),
    )

    class Media:
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/jquery.inputmask/5.0.6/jquery.inputmask.min.js',
            'apps/custom/admin.js',
        )

    def save_model(self, request, obj: User, form, change):
        obj.status = self._status
        super().save_model(request, obj, form, change)

        if self._status == obj.Status.MANAGER:
            obj.is_staff = True
            content_type = ContentType.objects.get_for_model(PaymeRequest)
            name = PaymeRequest.__name__.lower()
            perm_codename_1 = f'change_{name}'
            perm_codename_2 = f'view_{name}'
            permissions = Permission.objects.filter(content_type=content_type,
                                                    codename__in=(perm_codename_1, perm_codename_2))
            obj.user_permissions.add(*permissions)
            obj.save()

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=self._status)


@admin.register(ManagerUser)
class ManagerUserModelAdmin(CustomUserAdmin):
    list_display = 'phone',
    _status = User.Status.MANAGER


@admin.register(AdminUser)
class AdminUserModelAdmin(CustomUserAdmin):
    _status = User.Status.ADMIN


@admin.register(CurrierUser)
class CurrierUserModelAdmin(CustomUserAdmin):
    _status = User.Status.CURRIER


@admin.register(OperatorUser)
class OperatorUserModelAdmin(CustomUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'status')
    list_filter = ('status',)
    _status = User.Status.OPERATOR


@admin.register(Profile)
class OperatorProfileModelAdmin(ModelAdmin):
    pass


def get_app_list(self, request):
    custom_order = [
        _('Products'),
        _('Orders'),
        _('Categories'),
        _('Product Images'),
        _('Streams'),
        _('Payments'),
        _('Profiles'),
        _('Regions'),

        _('Users'),
        _('Operator Users'),
        _('Admin Users'),
        _('Manager Users'),
        _('Currie Users'),

        _('New Orders'),
        _('Visit Orders'),
        _('Ready Orders'),
        _('Delivery Orders'),
        _('Delivered Orders'),
        _('Canceled Orders'),
        _('Missed Call Orders'),
        _('Archived Orders'),

        _('Districts'),
        _('Site Settings'),
        _('Competitions'),
        _('User Balances'),
        _('Payme Requests'),
        _('Balances'),
    ]
    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())
    for app in app_list:
        if app["app_label"] == "apps":
            app["models"].sort(key=lambda x: custom_order.index(x["name"]))

    return app_list


admin.AdminSite.get_app_list = get_app_list


class OrderStatus(ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=self._status)


@admin.register(NewOrders)
class NewOrdersAdmin(OrderStatus):
    list_display = ['status']

    _status = Order.Status.NEW


@admin.register(VisitOrders)
class VisitOrdersAdmin(OrderStatus):
    _status = Order.Status.VISIT


@admin.register(ReadyOrders)
class ReadyOrdersAdmin(OrderStatus):
    _status = Order.Status.READY


@admin.register(DeliveryOrders)
class DeliveryOrdersAdmin(OrderStatus):
    _status = Order.Status.DELIVERY


@admin.register(DeliveredOrders)
class DeliveredOrdersAdmin(OrderStatus):
    _status = Order.Status.DELIVERED


@admin.register(CanceledOrders)
class CanceledOrdersAdmin(OrderStatus):
    _status = Order.Status.CANCELED


@admin.register(ArchivedOrders)
class ArchivedOrdersAdmin(OrderStatus):
    _status = Order.Status.ARCHIVED


@admin.register(PhoneOrder)
class PhoneOrderAdmin(OrderStatus):
    _status = Order.Status.PHONE
