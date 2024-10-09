import re

from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm, UserCreationForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.forms import CharField, PasswordInput, ModelForm, ModelChoiceField, TextInput

from apps.websayt.models import Product, User
from apps.websayt.models import Order, Stream, Region, District
from apps.websayt.models import PaymeRequest


class RegisterModelForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['phone', 'status', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
        return phone

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Ikkala parol mos kelmadi.")
        if len(password1) < 8:
            raise ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
        if password1.isdigit():
            raise ValidationError("Parol faqat raqamlardan iborat bo'lmasligi kerak.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone')
        pattern = re.compile(r'\d+')
        digits = pattern.findall(phone)
        formatted_number = ''.join(digits[1:])
        return formatted_number


class LoginModelForm(AuthenticationForm):
    username = CharField(label='Telefon raqam', max_length=20)

    class Meta:
        model = User
        fields = ('username', 'password1')

    def clean(self):
        phone = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if phone and password:
            self.user_cache = authenticate(self.request, phone=phone, password=password)
            if self.user_cache is None:
                raise ValidationError("Telefon raqami yoki parol noto'g'ri")
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


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
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'region', 'district', 'address', 'telegram_id', 'description', 'avatar']
        widgets = {
            'description': TextInput(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].queryset = Region.objects.all()
        self.fields['district'].queryset = District.objects.all()


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
