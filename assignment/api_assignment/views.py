from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAuthenticated

from .models import MenuItem
from .serializers import MenuItemSerializer

@api_view(['GET'])
@permission_classes(IsAuthenticated)
def menu_items(request):
     items = MenuItem.objects.all()
     serialize_items = MenuItemSerializer(items, many=True)
     Response(serialize_items, status=status.HTTP_200_OK)