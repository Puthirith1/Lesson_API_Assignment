from rest_framework import serializers
from . import models
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_item = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = models.Order
        fields = fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
