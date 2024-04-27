from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Burger)
admin.site.register(Category)
admin.site.register(Presintation)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(CartItem)

