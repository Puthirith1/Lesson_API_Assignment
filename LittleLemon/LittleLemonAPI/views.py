from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction
from .models import MenuItem, Cart, Order, OrderItem, Category
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, CategorySerializer
from django.core.paginator import Paginator, EmptyPage
from django.utils.timezone import now

def is_manager(user: User):
     return user.groups.filter(name="Manager").exists()
def is_delivery_crew(user: User):
     return user.groups.filter(name="Delivery crew").exists()

class ManagerGroupView(APIView):
     permission_classes = [IsAuthenticated]

     def get(self, request):
          if not request.user.is_superuser:
               return Response('You do not have permission to get manager list.', status.HTTP_403_FORBIDDEN)
          
          users = User.objects.all()
          managers = []
          
          for user in users:
               if is_manager(user):
                    managers.append(user)
                    
          serializer = UserSerializer(managers, many=True)
          return Response(serializer.data, status.HTTP_200_OK)
     
     def post(self, request):
          if not request.user.is_superuser:
               return Response('You do not have permission to assign manager.', status.HTTP_403_FORBIDDEN)
          
          user_id = request.data.get('id')
          username = request.data.get('username')

          if user_id:
               user = User.objects.filter(id=user_id).first()
          elif username:
               user = User.objects.filter(username=username).first()
          else:
               return Response({'id or username is required.'}, status=status.HTTP_400_BAD_REQUEST)

          if not user:
               return Response({'You can not assign group to user. User not found.'}, status=status.HTTP_404_NOT_FOUND)

          group = Group.objects.filter(name='Manager').first()
          group.user_set.add(user)

          return Response({'detail': f'User {user.username} assigned to manager group.'}, status=status.HTTP_201_CREATED)
     
class SingleManagerGroupView(APIView):
     permission_classes = [IsAuthenticated]

     def delete(self, request, pk):
          if not request.user.is_superuser:
               return Response('You do not have permission to assign manager.', status.HTTP_403_FORBIDDEN)

          user = User.objects.filter(id=pk).first()

          if not user:
               return Response({'You can not remove group to user. User not found.'}, status=status.HTTP_404_NOT_FOUND)

          group = Group.objects.filter(name='Manager').first()
          group.user_set.remove(user)

          return Response({'detail': f'User {user.username} removed from manager group.'}, status=status.HTTP_200_OK)

class CategoryView(APIView):
     permission_classes=[IsAuthenticated]

     def get(self, request):
          categories = Category.objects.all()
          serializer = CategorySerializer(categories, many=True)
          return Response(serializer.data, status.HTTP_200_OK)
     
     def post(self, request):
          if not request.user.is_superuser:
               return Response('You do not have permission to create category.', status.HTTP_403_FORBIDDEN)
          serializer = CategorySerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response('Category create successfully!', status.HTTP_201_CREATED)
     
class MenuItemView(APIView):
     permission_classes=[IsAuthenticated]
     
     def get(self, request):
          items = MenuItem.objects.select_related('category').all()
          category_name=request.query_params.get("category")
          ordering = request.query_params.get("ordering")
          perpage = request.query_params.get("perpage", default=2)
          page = request.query_params.get("page", default=1)
          search = request.query_params.get("search")
          if category_name:
               items.filter(category__title=category_name)
          if ordering:
               ordering_fields = ordering.split(",")
               items = items.order_by(*ordering_fields)
          if search:
               items = items.filter(title_contain=search)
          paginator = Paginator(items, per_page=perpage)
          try:
               items = paginator.page(number=page)
          except EmptyPage:
               items = []
          serializer = MenuItemSerializer(items, many=True)
          return Response(serializer.data, status.HTTP_200_OK)
     
     def post(self, request):
          if not request.user.is_superuser:
               return Response('You do not have permission to create menu item.', status.HTTP_403_FORBIDDEN)
          serializer = MenuItemSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data, status.HTTP_201_CREATED)

class SingleMenuItemView(APIView):
     permission_classes=[IsAuthenticated]

     def get (self, request, pk):
          if not is_manager(request.user):
               return Response('You do not have permission to get menu item.', status.HTTP_403_FORBIDDEN)
          try:
               item = MenuItem.objects.get(pk=pk)
          except MenuItem.DoesNotExist:
               return Response('Menu item not found.', status=status.HTTP_404_NOT_FOUND)
          serializer = MenuItemSerializer(item)
          return Response(serializer.data, status=status.HTTP_200_OK)

     def put(self, request, pk):
          if not is_manager(request.user):
               return Response('You do not have permission to update menu item.', status.HTTP_403_FORBIDDEN)
          try:
               item = MenuItem.objects.get(pk=pk)
          except MenuItem.DoesNotExist:
               return Response('You can not update menu item because menu item not found.', status=status.HTTP_404_NOT_FOUND)
          serializer = MenuItemSerializer(item, data=request.data)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data, status=status.HTTP_200_OK)
          
     def patch(self, request, pk):
          if not is_manager(request.user):
               return Response('You do not have permission to update menu item field.', status.HTTP_403_FORBIDDEN)
          try:
               item = MenuItem.objects.get(pk=pk)
          except MenuItem.DoesNotExist:
               return Response('You can not update menu item because menu item not found.', status=status.HTTP_404_NOT_FOUND)
          serializer = MenuItemSerializer(item, data=request.data, partial=True)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(serializer.data, status=status.HTTP_200_OK)
          
     def delelte(self, request, pk):
          if not is_manager(request.user):
               return Response('You do not have permission to delete menu item.', status.HTTP_403_FORBIDDEN)
          try:
               item = MenuItem.objects.get(pk=pk)
          except MenuItem.DoesNotExist:
               return Response('You can not delete menu item because menu item not found.', status=status.HTTP_404_NOT_FOUND)
          item.delete()
          return Response(f"Menu item {item.id}: {item.title} delete successfully!",status.HTTP_204_NO_CONTENT)
     
class DeliveryCrewGroupView(APIView):
     permission_classes = [IsAuthenticated]

     def get(self, request):
          if not is_manager(request.user):
               return Response('You do not have permission to get delivery crew list.', status.HTTP_403_FORBIDDEN)
          users = User.objects.all()
          delivery_crews = []
          for user in users:
               if is_delivery_crew(user):
                    delivery_crews.append(user)
          serializer = UserSerializer(delivery_crews, many=True)
          return Response(serializer.data, status.HTTP_200_OK)
     
     def post(self, request):
          if not is_manager(request.user):
               return Response('You do not have permission to assign delivery crew.', status.HTTP_403_FORBIDDEN)
          user_id = request.data.get('id')
          username = request.data.get('username')

          if user_id:
               user = User.objects.filter(id=user_id).first()
          elif username:
               user = User.objects.filter(username=username).first()
          else:
               return Response({'id or username is required.'}, status=status.HTTP_400_BAD_REQUEST)

          if not user:
               return Response({'You can not assign group to user. User not found.'}, status=status.HTTP_404_NOT_FOUND)

          group = Group.objects.filter(name='Delivery crew').first()
          group.user_set.add(user)

          return Response({'detail': f'User {user.username} assigned to delivery crew group.'}, status=status.HTTP_201_CREATED)
     
class SingleDeliveryCrewGroupView(APIView):
     permission_classes = [IsAuthenticated]

     def delete(self, request, pk):
          if not is_manager(request.user):
               return Response('You do not have permission to assign delivery crew.', status.HTTP_403_FORBIDDEN)

          user = User.objects.filter(id=pk).first()

          if not user:
               return Response({'You can not remove group to user. User not found.'}, status=status.HTTP_404_NOT_FOUND)

          group = Group.objects.filter(name='Delivery crew').first()
          group.user_set.remove(user)

          return Response({'detail': f'User {user.username} removed from delivery crew group.'}, status=status.HTTP_200_OK)
     
class CartMenuItemView(APIView):
     permission_classes = [IsAuthenticated]

     def get(self, request):
          items = Cart.objects.filter(user=request.user.id)
          serializer = CartSerializer(items, many=True)
          return Response(serializer.data, status.HTTP_200_OK)
     
     def post(self, request):
          item_id = request.data.get("id") 
          qty = request.data.get("quantity", default=1)
          if not item_id:
               return Response('Menu item id required', status.HTTP_400_BAD_REQUEST)
          try:
               item = MenuItem.objects.get(pk=item_id)
          except User.DoesNotExist:
               return Response('Can not find menu item', status.HTTP_404_NOT_FOUND)
          cart_line = {
               "user": request.user.id,
               "menuitem": item.id,
               "unit_price": item.price,
               "quantity": qty,
               "price": item.price*qty
          }
          serializer = CartSerializer(data=cart_line)
          serializer.is_valid(raise_exception=True)
          serializer.save()
          return Response(f'{item.title} is add to cart successfully.', status.HTTP_201_CREATED)
     
     def delete(self, request):
          cart = Cart.objects.filter(user=request.user.id)
          cart.delete()
          return Response('Cart items deleted successfully', status.HTTP_200_OK)
     
class OrderView(APIView):
     permission_classes = [IsAuthenticated]

     def get(self, request):
          if is_manager(request.user):
               orders = Order.objects.all()
               serializer = OrderSerializer(orders, many=True)
               return Response(serializer.data, status.HTTP_200_OK)
          
          if is_delivery_crew(request.user):
               orders = Order.objects.filter(delivery_crew=request.user.id)
               serializer = OrderSerializer(orders, many=True)
               return Response(serializer.data, status.HTTP_200_OK)
          
          orders = Order.objects.filter(user=request.user.id)
          serializer = OrderSerializer(orders, many=True)
          return Response(serializer.data, status.HTTP_200_OK)
     
     def post(self, request):
          items = Cart.objects.filter(user=request.user.id)
          if not items.exists():
               return Response("Cart is empty", status=400)
          
          with transaction.atomic():
               order_data = {
                    "user": request.user.id,
                    "total": 0,
                    "date": now()
               }
               order_serializer = OrderSerializer(data=order_data)
               order_serializer.is_valid(raise_exception=True)
               new_order = order_serializer.save()

               order_lines = []

               total = 0
               for item in items:
                    line = {
                         "order": new_order.id,
                         "menuitem": item.menuitem,
                         "unit_price": item.unit_price,
                         "quantity": item.quantity,
                         "price": item.price
                    }
                    order_lines.append(line)
                    total += item.price
               new_order.total = total
               new_order.save()

               order_item_serializer = OrderItemSerializer(data=order_lines, many=True)
               order_item_serializer.is_valid(raise_exception=True)
               order_item_serializer.save()

               items.delete()

          return Response("Order created successfully", status=status.HTTP_201_CREATED)

class SingleOrderView(APIView):
     permission_classes=[IsAuthenticated]

     def get(self, request, pk):
          item = get_object_or_404(Order, pk=pk)
          if item.user != request.user.id:
               return Response('You do not have permission to view this order.', status.HTTP_403_FORBIDDEN)
          serializer = OrderSerializer(item)
          return Response(serializer.data, status=status.HTTP_200_OK)

     def patch(self, request, pk):
          item = get_object_or_404(Order, pk=pk)
          
          if is_manager(request.user):
               delivery_crew_id = request.data.get("delivery_crew_id")
               delivery_status = request.data.get("status")
               new_item = {}
               if delivery_crew_id:
                    new_item["delivery_crew_id"] = delivery_crew_id
               if delivery_status:
                    new_item["status"] = delivery_status
               serializer = OrderSerializer(item, data=new_item, partial=True)
               serializer.is_valid(raise_exception=True)
               serializer.save()
               return Response("Order successfully update delivery status.", status.HTTP_200_OK)

          if is_delivery_crew(request.user):
               new_item = { "status": 1 }
               serializer = OrderSerializer(item, data=new_item, partial=True)
               serializer.is_valid(raise_exception=True)
               serializer.save()
               return Response("Order successfully update delivery crew.", status.HTTP_200_OK)
          
          return Response("You do not have permission to update.", status.HTTP_403_FORBIDDEN)

     def delete(self, request, pk):
          item = get_object_or_404(Order, pk=pk)

          if not is_manager(request.user):
               return Response("You do not have permission to delete order.", status.HTTP_403_FORBIDDEN)
          
          item.delete()
          return Response("Order delete successfully.", status.HTTP_200_OK)