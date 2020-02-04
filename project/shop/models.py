import os

from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.db.models.signals import post_save

from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )


class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='img')
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def sum_total_price(self):
        if self.item.discount_price:
            return round(self.quantity * self.item.discount_price, 2)
        return round(self.quantity * self.item.price, 2)

    def __str__(self):
        return '{} {}'.format(self.id, self.item.title)


class Order(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    address = models.ForeignKey(
        'Address',
        related_name='shipping_address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )

    def __str__(self):
        return '{} Username {} Date {}.{}.{}'.format(
            self.id,
            self.user,
            self.ordered_date.month,
            self.ordered_date.day,
            self.ordered_date.year
            )


class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=9)
    home_address = models.TextField()
    phone = PhoneNumberField()
    email = models.EmailField()
    default = False

    def __str__(self):
        return '{} {} {} {} {}'.format(
            self.id,
            self.first_name,
            self.last_name,
            self.country.name,
            self.city
            )


def user_profile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)

post_save.connect(user_profile_receiver, sender=settings.AUTH_USER_MODEL)
