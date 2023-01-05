from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views


router = routers.DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('products', views.ProductViewSet, basename='products')
router.register('carts', views.CartViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + carts_router.urls
