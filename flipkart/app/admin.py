from django.contrib import admin
from .models import (
    UserProfile,
    Categories,
    SubCategories,
    Products,
    Carts,
    Orders,
    Payments,
    Country,
    City,
    Wishlist,
    Address,
)

# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["userid", "gender", "dob", "mobile", "photo"]


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ["name"]


class SubCategoriesAdmin(admin.ModelAdmin):
    list_display = ["name", "gender", "categories"]


class ProductsAdmin(admin.ModelAdmin):
    list_display = [
        "userid",
        "productid",
        "productname",
        "categories",
        "subcategories",
        "description",
        "price",
        "quantity_available",
        "images",
    ]


class CountryAdmin(admin.ModelAdmin):
    list_display = ["name"]


class CityAdmin(admin.ModelAdmin):
    list_display = ["name", "country"]


class AddressAdmin(admin.ModelAdmin):
    list_display = ["userid", "address", "city", "country", "pincode"]


class CartsAdmin(admin.ModelAdmin):
    list_display = ["userid", "productid", "qty"]


class WishlistAdmin(admin.ModelAdmin):
    list_display = ["userid", "productid"]


class OrdersAdmin(admin.ModelAdmin):
    list_display = [
        "orderid",
        "userid",
        "productid",
        "qty",
        "orderdate",
        "address",
        "payment_status",
    ]


class PaymentsAdmin(admin.ModelAdmin):
    list_display = [
        "receiptid",
        "orderid",
        "userid",
        "productid",
        "payment_mode",
        "payment_status",
    ]


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(SubCategories, SubCategoriesAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Carts, CartsAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Payments, PaymentsAdmin)
admin.site.register(Address, AddressAdmin)
