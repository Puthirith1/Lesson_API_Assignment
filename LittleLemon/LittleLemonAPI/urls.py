from django.urls import path
from . import views

urlpatterns = [
     path('categories', views.CategoryView.as_view()),
     path('menu-items', views.MenuItemView.as_view()),
     path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
     path('groups/manager/users', views.ManagerGroupView.as_view()),
     path('groups/manager/users/<int:pk>', views.SingleManagerGroupView.as_view()),
     path('groups/delivery-crew/users', views.DeliveryCrewGroupView.as_view()),
     path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryCrewGroupView.as_view()),
     path('carts/menu-items', views.CartMenuItemView.as_view()),
     path('orders', views.OrderView.as_view()),
     path('orders/<int:pk>', views.SingleOrderView.as_view())
]