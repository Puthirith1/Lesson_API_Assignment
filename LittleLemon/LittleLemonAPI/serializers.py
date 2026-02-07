from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class MenuItemSerializer(serializers.ModelSerializer):
    inventory = serializers.IntegerField(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price', 'inventory']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'menu_item_name', 'menu_item_price']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order_id', 'menu_item_name', 'menu_item_price']

class OrderSerializer(serializers.ModelSerializer):
    order_item = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'delivery_crew_id', 'status', 'order_item']
