import re

from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import CharField, PasswordInput, ModelForm, ModelChoiceField

from apps.models import Product, User
from apps.models.products import Order, Stream, Region, District
from apps.models.users import PaymeRequest


class LoginModelForm(AuthenticationForm):
    confirm_password = CharField(max_length=255, widget=PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['phone', 'password']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        pattern = re.compile(r'\d+')
        digits = pattern.findall(phone_number)
        formatted_number = ''.join(digits[1:])
        return formatted_number


class OrderModelForm(ModelForm):
    product = ModelChoiceField(queryset=Product.objects.all())
    stream = ModelChoiceField(queryset=Stream.objects.all(), required=False)

    class Meta:
        model = Order
        fields = 'name', 'phone', 'product', 'stream'

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        pattern = re.compile(r'\d+')
        digits = pattern.findall(phone_number)
        formatted_number = ''.join(digits[1:])
        return formatted_number


class StreamOrderModelForm(ModelForm):
    product = ModelChoiceField(queryset=Product.objects.all())

    class Meta:
        model = Stream
        fields = 'name', 'product', 'discount', 'benefit'


class UserSettingsModelForm(ModelForm):
    region = ModelChoiceField(queryset=Region.objects.all(), required=False)
    district = ModelChoiceField(queryset=District.objects.all(), required=False)

    class Meta:
        model = User
        fields = 'first_name', 'last_name', 'address', 'telegram_id', 'description', 'region', 'district'


class UserSettingsImageModelForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'banner']


class UserSettingsPasswordChangeForm(PasswordChangeForm):
    old_password = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = CharField(widget=PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        fields = 'old_password', 'new_password1', 'new_password2'

    def clean_password(self):
        new_password1 = self.data.get('new_password1')
        new_password2 = self.data.get('new_password2')
        if new_password1 != new_password2:
            raise ("Parol mos emas")
        return make_password(new_password1)


class PaymeModelForm(ModelForm):
    class Meta:
        model = PaymeRequest
        fields = 'card_number', 'amount'

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        if card_number:
            if len(card_number) != 16:
                raise ValidationError("Karta raqami aniq 16 ta raqamdan iborat bo'lishi kerak.")
            if not card_number.isdigit():
                raise ValidationError("Karta raqami faqat raqamlardan iborat bo'lishi kerak.")
        return card_number
