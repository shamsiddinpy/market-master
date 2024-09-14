from django.db.models import Model, CharField, ForeignKey, CASCADE


class ShopCategory(Model):
    name = CharField(max_length=255, help_text="Do'kon nomini kiriting")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Do'koni nomi"
        verbose_name_plural = "Do'koni nomlari"


class Shop(Model):
    name = CharField(max_length=255, unique=True, null=True)
    shop_category = ForeignKey("apps.ShopCategory", CASCADE, help_text="Do'kon nomini")
    category = ForeignKey('apps.Category', CASCADE, verbose_name="Kategoriyalar", help_text="Do'kon toifasi")
