from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import TextChoices, CharField, TextField, BooleanField, ForeignKey, CASCADE, DecimalField, \
    DateTimeField, ImageField, Model, OneToOneField
from django_ckeditor_5.fields import CKEditor5Field

from apps.manager import CustomerUserManager

phone_regex = RegexValidator(regex=r'^\d{9,15}$',
                             message=
                             "Phone number must be entered in the format: '9999999999'. Up to 10 digits allowed.")


class User(AbstractUser):
    class Status(TextChoices):
        ADMIN = 'admin', "Admin"
        CURRIER = "currier", "Currier"
        OPERATOR = 'operator', "Operator"
        USERS = "user", "Users"
        MANAGER = "manager", "Manager"

    username = None
    phone = CharField(max_length=17, unique=True, validators=[phone_regex])
    status = CharField(max_length=20, choices=Status.choices)
    main_balance = DecimalField(max_digits=10, decimal_places=0, default=0)
    amount_paid = DecimalField(max_digits=10, decimal_places=0, default=0)
    intro = TextField(max_length=2000, blank=True, null=True, default="To enter")
    avatar = ImageField(upload_to='users/images', null=True,
                        blank=True, default='images/icon-256x256.png')
    banner = ImageField(upload_to='users/banner/images', null=True,
                        blank=True)
    address = CharField(max_length=200, blank=True, null=True)
    description = CKEditor5Field(null=True, blank=True)
    is_activate = BooleanField(default=False)
    region = ForeignKey('apps.Region', CASCADE, blank=True, null=True)
    district = ForeignKey('apps.District', CASCADE, blank=True, null=True)
    telegram_id = CharField(max_length=200, blank=True, null=True, unique=True)
    users = CharField(max_length=25, choices=Status.choices, default=Status.USERS)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = CustomerUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class PaymeRequest(Model):
    class Status(TextChoices):
        PAID = 'paid', 'Paid'
        PROGRESS = 'progress', 'Progress'
        CANCELLED = 'canceled', 'Canceled'

    user = ForeignKey('apps.User', CASCADE)
    card_number = CharField(max_length=16)
    amount = DecimalField(max_digits=10, decimal_places=0, default=0)
    status = CharField(max_length=20, choices=Status.choices, default=Status.PROGRESS)
    image = ImageField(upload_to='payme/images', null=True,
                       blank=True)
    message = TextField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Ismi: {self.user.phone} - miqdor: {self.amount}'

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"


class ProfileModel(Model):
    name = OneToOneField('apps.User', CASCADE)
    from_working_time = DateTimeField(null=True, blank=True),
    to_working_time = DateTimeField(null=True, blank=True),

    def __str__(self):
        return self.name.phone
