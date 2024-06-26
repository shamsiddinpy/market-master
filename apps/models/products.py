from django.core.validators import RegexValidator
from django.db.models import DateTimeField, Model, CharField, SlugField, ForeignKey, CASCADE, PositiveIntegerField, \
    JSONField, FloatField, TextChoices, IntegerField, BooleanField, DateField, DecimalField, ImageField
from django.utils.text import slugify
from django.views.generic import TemplateView
from django_ckeditor_5.fields import CKEditor5Field

from apps.models.users import User

phone_regex = RegexValidator(
    regex=r'^\d{7,12}$',
    message="Phone number must be entered in the format: '9999999999'. Up to 12 digits allowed."
)


class CreatedBaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ProductImages(CreatedBaseModel):
    image = ImageField(upload_to='product/images', null=True, blank=True)
    product = ForeignKey('apps.Product', CASCADE, related_name='product_images', verbose_name="Product")

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'


class Category(CreatedBaseModel):
    name = CharField(max_length=100)
    slug = SlugField(unique=True, editable=False)
    image = ImageField(upload_to='category/images', verbose_name="Image")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(CreatedBaseModel):
    name = CharField(max_length=100)
    description = CKEditor5Field(null=True, blank=True)
    slug = SlugField(max_length=25, unique=True, editable=False)
    category = ForeignKey('apps.Category', CASCADE, related_name='products', to_field='slug',
                          verbose_name="Category")
    price = IntegerField()
    quantity = PositiveIntegerField(default=0)
    spec = JSONField(null=True, blank=True)
    discount = FloatField(null=True, blank=True)
    referral_reward = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    @property
    def first_image(self):
        return self.product_images.first()

    def __str__(self):
        return self.name

    @property
    def delivery_price(self):
        return self.discount * self.price / 100

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(force_insert, force_update, using, update_fields)


class SiteSetting(Model):
    name = CharField(max_length=100, blank=True, null=True)
    delivery_to = IntegerField()
    operator_to = IntegerField()
    minimal_sum = DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'


class Order(CreatedBaseModel):
    class Status(TextChoices):
        NEW = "new", "New"
        VISIT = "visit", "Visit"
        READY = "ready", "Ready"
        DELIVERY = "delivery", "Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELED = "canceled", "Canceled"
        ARCHIVED = "archived", "Archived"
        PHONE = "phone", "Phone"

    name = CharField(max_length=100)
    phone = CharField(max_length=20, blank=True, validators=[phone_regex])
    comment = CharField(max_length=255, blank=True, null=True)
    count = PositiveIntegerField(default=1)
    status = CharField(max_length=30, choices=Status.choices, default=Status.NEW)
    product = ForeignKey('apps.Product', CASCADE, verbose_name="Product", to_field='slug')
    currier = ForeignKey('apps.User', CASCADE, limit_choices_to={'type': User.Status.CURRIER}, null=True, blank=True,
                         verbose_name="Currier")
    region = ForeignKey('apps.Region', CASCADE, verbose_name='Region', blank=True, null=True)
    district = ForeignKey('apps.District', CASCADE, verbose_name='District', null=True, blank=True)
    street = CharField(max_length=25, blank=True, null=True)
    stream = ForeignKey('apps.Stream', CASCADE, null=True, blank=True, related_name='orders', verbose_name="Stream")
    operator = ForeignKey('apps.User', CASCADE, limit_choices_to={'status': User.Status.OPERATOR},
                          related_name='operator_orders', blank=True, null=True, verbose_name='Operator')
    user = ForeignKey('apps.User', CASCADE, blank=True, null=True, related_name='user', verbose_name='User')
    referral_user = ForeignKey('apps.User', CASCADE, related_name='referral_user', blank=True, null=True,
                               verbose_name="Referral User")

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class Region(Model):
    name = CharField(max_length=100)

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'

    def __str__(self):
        return self.name


class District(Model):
    name = CharField(max_length=30)
    region = ForeignKey('apps.Region', CASCADE, verbose_name="District")

    class Meta:
        verbose_name = 'District'
        verbose_name_plural = 'Districts'


class Stream(Model):
    name = CharField(max_length=100)
    counter = IntegerField(default=0)
    product = ForeignKey('apps.Product', CASCADE, verbose_name="Product")
    user = ForeignKey('apps.User', CASCADE, verbose_name="User")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    discount = PositiveIntegerField(blank=True, null=True)
    benefit = PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stream'
        verbose_name_plural = 'Streams'


class Competition(Model):
    image = ImageField(upload_to='competition/images', null=True, blank=True, verbose_name='Image')
    is_active = BooleanField(default=False)
    start_date = DateField(null=True, blank=True)
    end_date = DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Competition'
        verbose_name_plural = 'Competitions'


class AdminPageTemplateView(TemplateView):
    template_name = 'apps/admin/admin_page.html'
