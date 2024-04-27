from django.contrib.auth.models import User
from django.db import models



LABEL_CHOICES = (
    ('S', 'sale'),
    ('N', 'new'),
    ('P', 'promotion')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Category(models.Model):
    name = models.CharField(max_length=125)

    def __str__(self):
        return self.name


class Burger(models.Model):
    name = models.CharField(max_length=125)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    gram = models.IntegerField()
    photo = models.ImageField(upload_to='uploads/% Y/% m/% d/')
    about = models.TextField()
    price = models.IntegerField(default=0)
    digital = models.BooleanField(default=False, null=True, blank=False)
    published_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Presintation(models.Model):
    name = models.CharField(max_length=60)
    title = models.CharField(max_length=60)
    photo = models.ImageField(upload_to='presintation/% Y/% m/% d/')
    published_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now=True)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, unique=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Burger, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f'{self.product}'
