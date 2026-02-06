from django.db import models

# Create your models here.
class MenuItem(models.Model):
     name = models.CharField(max_length=255, unique=True)
     price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
     user_id = models.BigIntegerField()
     menu_item_name = models.CharField(max_length=255)
     menu_item_price = models.DecimalField(max_digits=6, decimal_places=2)

class Order(models.Model):
     user_id = models.BigIntegerField()
     delivery_crew_id = models.CharField(max_length=255)
     status = models.SmallIntegerField()

class OrderItem(models.Model):
     order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_item")
     menu_item_name = models.CharField(max_length=255)
     menu_item_price = models.DecimalField(max_digits=6, decimal_places=2)
