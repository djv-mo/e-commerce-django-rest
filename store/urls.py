from django.urls import path
from django.urls.conf import include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('products', views.ProductViewSet, basename='products')


urlpatterns = router.urls
