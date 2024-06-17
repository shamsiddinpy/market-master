from django.core.validators import RegexValidator
from django.db.models import DateTimeField, Model, CharField, SlugField, ForeignKey, CASCADE, PositiveIntegerField, \
    JSONField, FloatField, TextChoices, IntegerField, BooleanField, DateField, DecimalField, ImageField
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from parler.models import TranslatableModel, TranslatedFields

from apps.models.users import User
from apps.utils import resize_image

phone_regex = RegexValidator(
    regex=r'^\d{7,12}$',
    message=_("Phone number must be entered in the format: '9999999999'. Up to 12 digits allowed.")
)


class CreatedBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProductImages(CreatedBaseModel):
    image = ImageField(upload_to='product/images', null=True, blank=True)
    product = ForeignKey('apps.Product', CASCADE, related_name='product_images', verbose_name=_("Product"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            resize_image(self.image.path, size=(390, 390))

    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')


class Category(CreatedBaseModel, TranslatableModel):
    translations = TranslatedFields(
        name=CharField(_('Name'), max_length=100)
    )
    slug = SlugField(unique=True, editable=False)
    image = ImageField(upload_to='category/images', verbose_name=_("Image"))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.safe_translation_getter('name', any_language=True))
        super().save(*args, **kwargs)
        if self.image:
            resize_image(self.image.path, size=(86, 86))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)


class Product(CreatedBaseModel, TranslatableModel):
    translations = TranslatedFields(
        name=CharField(_('Name'), max_length=100),
        description=CKEditor5Field(_('Description'), null=True, blank=True)
    )
    slug = SlugField(max_length=100, unique=True, editable=False)
    category = ForeignKey('apps.Category', CASCADE, related_name='products', to_field='slug',
                          verbose_name=_("Category"))
    price = IntegerField(_("Price"))
    quantity = PositiveIntegerField(_("Quantity"), default=0)
    spec = JSONField(_("Specifications"), null=True, blank=True)
    discount = FloatField(_("Discount"), null=True, blank=True)

    @property
    def delivery_price(self):
        return self.discount * self.price / 100

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = slugify(self.safe_translation_getter('name', any_language=True))
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    @property
    def first_image(self):
        return self.product_images.first()


class SiteSetting(TranslatableModel):
    translations = TranslatedFields(
        name=CharField(_('Name'), max_length=100, blank=True, null=True)
    )
    delivery_to = IntegerField(_("Delivery To"))
    operator_to = IntegerField(_("Operator To"))
    minimal_sum = DecimalField(_("Minimal Sum"), max_digits=10, decimal_places=0)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)

    class Meta:
        verbose_name = _('Site Setting')
        verbose_name_plural = _('Site Settings')


class Order(CreatedBaseModel):
    class Status(TextChoices):
        NEW = "new", _("New")
        VISIT = "visit", _("Visit")
        READY = "ready", _("Ready")
        DELIVERY = "delivery", _("Delivery")
        DELIVERED = "delivered", _("Delivered")
        CANCELED = "canceled", _("Canceled")
        ARCHIVED = "archived", _("Archived")
        PHONE = "phone", _("Phone")

    name = CharField(_("Name"), max_length=100)
    phone = CharField(_("Phone"), max_length=20, blank=True, validators=[phone_regex])
    comment = CharField(_("Comment"), max_length=255, blank=True, null=True)
    count = PositiveIntegerField(_("Count"), default=1)
    status = CharField(_("Status"), max_length=30, choices=Status.choices, default=Status.NEW)
    product = ForeignKey('apps.Product', CASCADE, verbose_name=_("Product"), to_field='slug')
    currier = ForeignKey('apps.User', CASCADE, limit_choices_to={'type': User.Type.CURRIER}, null=True, blank=True,
                         verbose_name=_("Currier"))
    region = ForeignKey('apps.Region', CASCADE, verbose_name=_('Region'), blank=True, null=True)
    district = ForeignKey('apps.District', CASCADE, verbose_name=_('District'), null=True, blank=True)
    street = CharField(_("Street"), max_length=25, blank=True, null=True)
    stream = ForeignKey('apps.Stream', CASCADE, null=True, blank=True, related_name='orders', verbose_name=_("Stream"))
    operator = ForeignKey('apps.User', CASCADE, limit_choices_to={'type': User.Type.OPERATOR},
                          related_name='operator_orders', blank=True, null=True, verbose_name=_('Operator'))
    user = ForeignKey('apps.User', CASCADE, blank=True, null=True, related_name='user', verbose_name=_('User'))
    referral_user = ForeignKey('apps.User', CASCADE, related_name='referral_user', blank=True, null=True,
                               verbose_name=_("Referral User"))

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')


class Region(TranslatableModel):
    translations = TranslatedFields(
        name=CharField(_('Name'), max_length=100),
    )

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')


class District(TranslatableModel):
    translations = TranslatedFields(
        name=CharField(_('Name'), max_length=30)
    )
    region = ForeignKey('apps.Region', CASCADE, verbose_name=_("Region"))

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True)

    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')


class Stream(Model):
    name = CharField(_("Name"), max_length=100)
    counter = IntegerField(_("Counter"), default=0)
    product = ForeignKey('apps.Product', CASCADE, verbose_name=_("Product"))
    user = ForeignKey('apps.User', CASCADE, verbose_name=_("User"))
    created_at = DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = DateTimeField(_("Updated At"), auto_now=True)
    discount = PositiveIntegerField(_("Discount"), default=0, blank=True, null=True)
    benefit = PositiveIntegerField(_("Benefit"), default=0, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Stream')
        verbose_name_plural = _('Streams')


class Competition(Model):
    image = ImageField(upload_to='competition/images', null=True, blank=True, verbose_name=_("Image"))
    is_active = BooleanField(_("Is Active"), default=False)
    start_date = DateField(_("Start Date"), null=True, blank=True)
    end_date = DateField(_("End Date"), null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            resize_image(self.image.path, size=(1220, 1220))

    class Meta:
        verbose_name = _('Competition')
        verbose_name_plural = _('Competitions')
