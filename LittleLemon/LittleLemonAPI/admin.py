from django.contrib import admin
from . import models

# Register your models here.
admin.register(models.MenuItem)
admin.register(models.Cart)
admin.register(models.Order)
admin.register(models.OrderItem)