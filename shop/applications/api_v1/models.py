import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from shop.applications.common.functions import send_email
from shop.settings import URL_SERVER

# Create your models here.


class AppVersion(models.Model):
    version = models.CharField(max_length=10, default='')
    last_update = models.DateTimeField(auto_now=False, default=timezone.now)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    def send_email(self, template_path, title, data):
        content = render_to_string(template_path, data)
        send_email(title, content=content, to=[
            self.email], content_type="text/html")

    def send_update_email(self, message):
        try:
            app_version = AppVersion.objects.all().order_by(
                '-last_update')[0].version
        except:
            app_version = '1.0'
        data = {
            'url_server': URL_SERVER,
            'version': '1',
            'first_name': self.first_name,
            'message': message
        }
        content = render_to_string('emails/update.html', data)
        send_email('¡Nueva actualización!', content=content,
                   to=[self.email], content_type='text/html')

    def get_profile(self):
        return Profile.objects.get(user=self)

    def __str__(self):
        return self.email

    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Profile(BaseModel):
    def image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        file_name = os.path.splitext(filename)[0]
        url = "users/%s/profile/%s.%s" % (self.user.id,
                                          slugify(str(file_name)), extension)
        return url
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Attributes
    image_profile = models.ImageField(
        upload_to=image_path, null=True, blank=True, verbose_name='Profile image')
    facebook_id = models.CharField(
        max_length=75, null=True, blank=True, verbose_name='Facebook id')

    def __str__(self):
        return self.user.email


class Business(BaseModel):
    def image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        file_name = os.path.splitext(filename)[0]
        url = "business/%s/%s.%s" % (self.id,
                                     slugify(str(file_name)), extension)
        return url

    # Relations
    users = models.ManyToManyField(User)

    # Attributes
    name = models.CharField(max_length=300, default='')
    description = models.TextField()
    active = models.BooleanField(default=False)
    logo = models.ImageField(
        upload_to=image_path, null=True, blank=True, verbose_name='Logo url')

    def __str__(self):
        return self.name


class Category(BaseModel):
    def image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        file_name = os.path.splitext(filename)[0]
        url = "business/%s/categories/%s/%s.%s" % (self.business.id, self.id,
                                                   slugify(str(file_name)), extension)
        return url

    # Relations
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    # Attributes
    name = models.CharField(max_length=300, default='')
    description = models.TextField()
    image = models.ImageField(
        upload_to=image_path, null=True, blank=True, verbose_name='Image url')

    def __str__(self):
        return self.name


class SubCategory(BaseModel):
    def image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        file_name = os.path.splitext(filename)[0]
        url = "business/%s/categories/%s/subcategories/%s/%s.%s" % (self.category.business.id, self.category.id, self.id,
                                                                    slugify(str(file_name)), extension)
        return url

    # Relations
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # Attributes
    name = models.CharField(max_length=300, default='')
    description = models.TextField()
    image = models.ImageField(
        upload_to=image_path, null=True, blank=True, verbose_name='Image url')

    def __str__(self):
        return self.name


class Collection(BaseModel):
    def image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        file_name = os.path.splitext(filename)[0]
        url = "business/%s/collections/%s/%s.%s" % (self.business.id, self.id,
                                                    slugify(str(file_name)), extension)
        return url

    # Relations
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    # Attributes
    name = models.CharField(max_length=300, default='')
    description = models.TextField()
    image = models.ImageField(
        upload_to=image_path, null=True, blank=True, verbose_name='Image url')

    def __str__(self):
        return self.name


class Product(BaseModel):
    # Relations
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.SET_NULL, blank=True, null=True)

    # Attributes
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField(default=0.0)
    shipping_price = models.FloatField(default=0.0)
    # Control attributes
    published = models.BooleanField(default=True)
    publish_at = models.DateTimeField(default=timezone.now)
    # This var is for always show in home page for example
    promote = models.BooleanField(default=False)
    # SEO controls
    engine_title = models.CharField(max_length=255)
    engine_description = models.TextField()

    def __str__(self):
        return self.name


class ProductVariant(BaseModel):
    # Relations
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Attributes
    name = models.CharField(max_length=255)
    # This var allows to the user change the original price
    price = models.FloatField(default=None, null=True, blank=True)
    shipping_price = models.FloatField(default=None, null=True, blank=True)
    sku = models.CharField(max_length=255)
    stock = models.IntegerField(default=0)
    # Control vars
    # This var is used to know if the user wants to control the stock
    use_stock = models.BooleanField(default=True)

    def getProductImage(self):
        product_images = ProductImage.objects.filter(
            product=self.product).order_by('created_at')
        if len(product_images) > 0:
            return product_images[0].image
        else:
            return None

    def __str__(self):
        return self.name


class ProductImage(BaseModel):
    def image_path(self, filename):
        extension = os.path.splitext(filename)[1][1:]
        file_name = os.path.splitext(filename)[0]
        url = "business/%s/products/%s/images/%s.%s" % (self.product.business.id, self.product.id,
                                                        slugify(str(file_name)), extension)
        return url

    # Relations
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Attributes
    image = models.ImageField(
        upload_to=image_path, null=True, blank=True, verbose_name='Image url')

    def __str__(self):
        return self.product.name


class Customer(BaseModel):
    # Relations
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    # Attributes
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    colony = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)

    def __str__(self):
        return "%s - %s" % (self.name, self.email)


class Order(BaseModel):
    STATUS = (
        (0, 'fallido'),
        (1, 'pago procesando'),
        (2, 'enviado'),
        (3, 'completado'),
        (4, 'cancelado')
    )
    METHODS = (
        ('openpay', 'OpenPay'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash')
    )

    # Relations
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, null=True, blank=True)

    # Attributes
    order_id = models.CharField(max_length=255)
    shipping_track_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS)
    method = models.CharField(max_length=155, choices=METHODS, default='cash')
    shipping_cost = models.FloatField(default=0)
    amount = models.FloatField(default=0)
    # PayPal
    paypal_order_id = models.CharField(max_length=255, null=True, blank=True)
    # Openpay attributes
    openpay_id = models.CharField(max_length=255, null=True, blank=True)
    openpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    authorization = models.CharField(max_length=255, null=True, blank=True)
    openpay_status_text = models.CharField(
        max_length=255, null=True, blank=True)
    error_message = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.order_id, self.customer.name)


class OrderProduct(BaseModel):
    # Relations
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE)

    # Attributes
    price = models.FloatField(default=0)
    quantity = models.IntegerField(default=1)

    def getTotal(self):
        return self.quantity * self.price

    def __str__(self):
        return "%s - %s - %s" % (self.order.id, self.product_variant.name, self.quantity)


class Discount(BaseModel):
    TYPE = (
        (0, 'Precio fijo'),
        (1, 'Porcentaje'),
    )
    # Business
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    # Attributes
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=TYPE)
    value = models.FloatField()

    def __str__(self):
        return self.name


class Subscription(BaseModel):
    PERIOD = (
        (0, 'Days'),
        (1, 'Month'),
        (2, 'Year'),
    )

    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    period = models.IntegerField(choices=PERIOD)
    period_number = models.IntegerField()


class BusinessSetting(BaseModel):
    # Relations
    business = models.ForeignKey(Business, on_delete=models.CASCADE)

    # Attributes
    free_delivery_amount = models.FloatField(default=0.0, null=True)


class UserSubscription(BaseModel):
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)

    # Attributes
    started_date = models.DateTimeField(default=timezone.now)
    ended_date = models.DateTimeField(default=timezone.now)
    last_paid = models.FloatField(default=0.0)


class SubscriptionPayment(BaseModel):
    # Relations
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Attributes
    subscription_name = models.CharField(max_length=255)

    # Openpay attributes
    amount = models.FloatField(default=0)
    order_id = models.CharField(max_length=255)
    openpay_id = models.CharField(max_length=255, null=True, blank=True)
    openpay_order_id = models.CharField(max_length=255, null=True, blank=True)
    authorization = models.CharField(max_length=255, null=True, blank=True)
    openpay_status_text = models.CharField(
        max_length=255, null=True, blank=True)
    error_message = models.CharField(max_length=255, null=True, blank=True)


class ReviewPurchase(BaseModel):
    # Relations
    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE)

    # Attributes
    rating = models.IntegerField(default=5, null=True)
    review = models.CharField(max_length=255, null=True)
