from django.db.models import Model, CharField, ForeignKey, CASCADE, PositiveSmallIntegerField, TextChoices, \
    JSONField, BooleanField, TextField, ImageField, URLField, EmailField, FloatField

from apps.websayt.models.products import CreatedBaseModel


class Country(CreatedBaseModel):
    name = CharField(max_length=255, verbose_name='davlatlar nomi')
    code = CharField(max_length=255, verbose_name='davlatlar kodi')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Davlat'
        verbose_name_plural = 'Davlatlar'


class Currency(Model):
    name = CharField(max_length=255, verbose_name='Nomi')
    symbol = PositiveSmallIntegerField(default=1, db_default=1, verbose_name='rangi')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Pul birlgi'
        verbose_name_plural = 'Pul birlklari'


class ShopCategory(Model):
    name = CharField(max_length=255, help_text="Do'kon nomini kiriting")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Do'koni nomi"
        verbose_name_plural = "Do'koni nomlari"


class Shop(CreatedBaseModel):
    class Status(TextChoices):
        ACTIVE = 'active', 'Active'  # Faol
        IN_ACTIVE = 'inactive', 'Inactive'

    status = CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    name = CharField(max_length=255, unique=True, null=True)
    shop_category = ForeignKey("sh.ShopCategory", CASCADE, help_text="Do'kon nomini")
    phone_number = CharField(max_length=20, unique=True, help_text="Do'konchini nomeri")
    country = ForeignKey('apps.Country', on_delete=CASCADE, help_text="Qaysi davlatdan o'tganligi")
    currency = ForeignKey('apps.Currency', on_delete=CASCADE, help_text="Davlat pul birligi")
    owner = ForeignKey('apps.User', on_delete=CASCADE, null=True, related_name="owned_shops")
    working_hours = JSONField(default=dict, null=True, blank=True, help_text="Do'konchini ish vaqti")
    shop_delete = BooleanField(default=False,
                               help_text="Ushbu operatsiya yordamida do'koningizni o'chirishingiz mumkin."
                                         " Ushbu do'kon bilan bog'liq barcha ma'lumotlar do'kon bilan birga o'chirib tashlanadi,"
                                         " shu jumladan toifalar(kategoriyalar),"
                                         " mahsulotlar, buyurtmalar, mijozlar, foydalanuvchilar va boshqalar.")
    about_us = TextField(blank=True, null=True, help_text="Biz haqimizda")
    about_us_image = ImageField(blank=True, null=True, upload_to='shops/about/')
    telegram = URLField(blank=True, null=True, max_length=255, help_text="Teligram kanalingizni ulang")
    shop_contact = ForeignKey('apps.ShopContact', on_delete=CASCADE, null=True)
    lat = FloatField('Location lat', blank=True, null=True)
    lon = FloatField('Location lon', blank=True, null=True)


class ShopContact(CreatedBaseModel):
    email = EmailField(max_length=255, blank=True, null=True, help_text="emailingiz")
    phone = CharField(max_length=20, blank=True, null=True, help_text="telfon raqamingiz")
    address = CharField(max_length=255, blank=True, null=True, help_text="manzilingiz")

    def __str__(self):
        return f"{self.email}, {self.phone}, {self.address}"

    class Meta:
        verbose_name = "Do'konchini kontact"
        verbose_name_plural = "Do'konchini kontactlari"
