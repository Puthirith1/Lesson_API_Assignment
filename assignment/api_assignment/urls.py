from django.urls import path, include
from . import views

urlpatterns = [
     path('menu-items', views.menu_items, name='menu-items'),
]