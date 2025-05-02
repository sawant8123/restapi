from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class CustomManager(models.Manager):
    def electronics_list(self):
        ele_category = Categories.objects.get(name="Electronics")  # (=) for single row
        return self.filter(categories__exact=ele_category)

    def cloths_list(self):
        cloth_category = Categories.objects.get(name="Cloths")
        return self.filter(categories__exact=cloth_category)

    def shoes_list(self):
        shoe_category = Categories.objects.get(name="Shoes")
        return self.filter(categories__exact=shoe_category)

    def pricerange(self, r1, r2):
        return self.filter(price__range=(r1, r2))


class UserProfile(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    type = (("Male", "Male"), ("Female", "Female"))
    gender = models.CharField(max_length=30, choices=type)
    dob = models.DateField(null=True, default=None)
    mobile = models.PositiveIntegerField()
    photo = models.ImageField(upload_to="images")


class Categories(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SubCategories(models.Model):
    name = models.CharField(max_length=100)
    type = (("Male", "Male"), ("Female", "Female"), ("None", "None"))
    gender = models.CharField(max_length=30, choices=type, default=None, null=True)
    categories = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, null=True, default=None
    )

    def __str__(self):
        return self.name


class Products(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    productid = models.PositiveIntegerField(primary_key=True)
    productname = models.CharField(max_length=50)
    categories = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, null=True, default=None
    )
    subcategories = models.ForeignKey(
        SubCategories, on_delete=models.SET_NULL, null=True, default=None
    )
    description = models.TextField()
    price = models.FloatField()
    quantity_available = models.PositiveIntegerField(default=0)
    images = models.ImageField(upload_to="images")
    objects = models.Manager()
    productmanager = CustomManager()

    def __str__(self):
        return self.productname


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, null=True, default=None
    )

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Address(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    pincode = models.PositiveIntegerField(
        validators=[MaxValueValidator(999999), MinValueValidator(100000)]
    )

    def __str__(self):
        return f"{self.address}, {self.city.name}, {self.city.country.name}"


class Carts(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    productid = models.ForeignKey(
        Products, on_delete=models.SET_NULL, null=True, default=None
    )
    qty = models.PositiveIntegerField(default=0)


class Wishlist(models.Model):
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    productid = models.ForeignKey(
        Products, on_delete=models.SET_NULL, null=True, default=None
    )


class Orders(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("PAID", "PENDING"),
        ("FAILED", "FAILED"),
        ("REFUNDED", "REFUNDED"),
    )

    orderid = models.PositiveIntegerField(primary_key=True)
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    productid = models.ForeignKey(
        Products, on_delete=models.SET_NULL, null=True, default=None
    )
    qty = models.PositiveIntegerField(default=0)
    orderdate = models.DateField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="PENDING"
    )

    def __str__(self):
        return f"Order #{self.orderid} - {self.userid}"


# Payments Table
class Payments(models.Model):
    PAYMENT_MODE_CHOICES = (
        ("Online", "Online"),
        ("Cash On Delivery", "Cash On Delivery"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("DONE", "DONE"),
        ("FAILED", "FAILED"),
    )

    receiptid = models.PositiveIntegerField(primary_key=True)
    orderid = models.ForeignKey(
        Orders, on_delete=models.SET_NULL, null=True, default=None
    )
    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)
    productid = models.ForeignKey(
        Products, on_delete=models.SET_NULL, null=True, default=None
    )
    payment_mode = models.CharField(max_length=30, choices=PAYMENT_MODE_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)

    def __str__(self):
        return f"Payment #{self.receiptid} - {self.payment_status}"
