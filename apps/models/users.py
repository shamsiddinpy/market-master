from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import TextChoices, CharField, TextField, BooleanField, ForeignKey, CASCADE, DecimalField, \
    DateTimeField, ImageField, Model
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from parler.models import TranslatableModel

from apps.manager import CustomerUserManager

phone_regex = RegexValidator(regex=r'^\d{9,15}$',
                             message=_(
                                 "Phone number must be entered in the format: '9999999999'. Up to 10 digits allowed."))


class User(AbstractUser):
    class Type(TextChoices):
        ADMIN = 'admin', _("Admin")
        CURRIER = "currier", _("Currier")
        OPERATOR = 'operator', _("Operator")
        USERS = "user", _("Users")
        MANAGER = "manager", _("Manager")

    username = None
    phone = CharField(_('Phone'), max_length=17, unique=True, validators=[phone_regex])
    type = CharField(_('Type'), max_length=20, choices=Type.choices)
    main_balance = DecimalField(_('Main_balance'), max_digits=10, decimal_places=0, default=0)
    amount_paid = DecimalField(_('Amount_paid'), max_digits=10, decimal_places=0, default=0)
    intro = TextField(_('Intro'), max_length=2000, blank=True, null=True, default=_("To enter"))
    avatar = ImageField(_('Avatar'), upload_to='users/images', null=True,
                        blank=True, default='users/images/')
    banner = ImageField(_('Banner'), upload_to='users/banner/images', null=True,
                        blank=True)
    address = CharField(_('Address'), max_length=200, blank=True, null=True)
    description = CKEditor5Field(_('Description'), null=True, blank=True)
    is_activate = BooleanField(_('is_activate'), default=False)
    region = ForeignKey('apps.Region', CASCADE, blank=True, null=True)
    district = ForeignKey('apps.District', CASCADE, blank=True, null=True)
    telegram_id = CharField(_('Telegram_id'), max_length=200, blank=True, null=True, unique=True)
    status = CharField(_('Status'), max_length=25, choices=Type.choices, default=Type.USERS)

    objects = CustomerUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class PaymeRequest(TranslatableModel):
    class Status(TextChoices):
        PAID = 'paid', _('Paid')
        PROGRESS = 'progress', _('Progress')
        CANCELLED = 'canceled', _('Canceled')

    user = ForeignKey('apps.User', CASCADE, blank=True, null=True)
    card_number = CharField(_('Card_number'), max_length=16)
    amount = DecimalField(_('Amount'), max_digits=10, decimal_places=0)
    status = CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PROGRESS)
    message = TextField(_('Message'), blank=True, null=True)
    created_at = DateTimeField(_('Created_at'), auto_now_add=True)

    def __str__(self):
        return f'Ismi: {self.user.username} - miqdor: {self.amount}'

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class BalanceReport(Model):
    role = ForeignKey('apps.User', CASCADE, related_name='account')
    real_balance = DecimalField(_('Real Balance'), max_digits=10, decimal_places=0, default=0)
    expected_balance = DecimalField(_('Expected Balance'), max_digits=10, decimal_places=0, default=0)

    class Meta:
        verbose_name = _('Sale Summary')
        verbose_name_plural = _('Sales Summary')
