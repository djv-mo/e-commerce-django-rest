import stripe
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import serializers
from .models import Product, Category, ProductImage, Cart, CartItem, Order, OrderItem
from .signals import order_created


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'products_count']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.CharField(source="category.title", read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'category', 'images']

# This serializer for cart


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        selected_product = Product.objects.get(pk=product_id)
        if quantity > selected_product.inventory:
            raise serializers.ValidationError(
                "You have entered a quantity that is more than the product's availabe quantity")

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            if cart_item.quantity+quantity > selected_product.inventory:
                raise serializers.ValidationError(
                    "You have entered a quantity that is more than the product's availabe quantity")
            else:
                cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


# class CreateOrderSerializer(serializers.Serializer):
#     cart_id = serializers.UUIDField()

#     def validate_cart_id(self, cart_id):
#         if not Cart.objects.filter(pk=cart_id).exists():
#             raise serializers.ValidationError(
#                 'No cart with the given ID was found.')
#         if CartItem.objects.filter(cart_id=cart_id).count() == 0:
#             raise serializers.ValidationError('The cart is empty.')
#         return cart_id

#     def save(self, **kwargs):
#         with transaction.atomic():
#             cart_id = self.validated_data['cart_id']

#             customer = get_user_model().objects.get(
#                 id=self.context['id'])
#             if getattr(customer, 'address', None) is None:
#                 raise serializers.ValidationError(
#                     'Your address should not be empty')
#             if getattr(customer, 'phone', None) is None:
#                 raise serializers.ValidationError(
#                     'Your phone should not be empty')
#             order = Order.objects.create(customer=customer)

#             cart_items = CartItem.objects \
#                 .select_related('product') \
#                 .filter(cart_id=cart_id)
#             order_items = [
#                 OrderItem(
#                     order=order,
#                     product=item.product,
#                     unit_price=item.product.unit_price,
#                     quantity=item.quantity
#                 ) for item in cart_items
#             ]
#             OrderItem.objects.bulk_create(order_items)

#             Cart.objects.filter(pk=cart_id).delete()

#             order_created.send_robust(self.__class__, order=order)

#             return order

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    # Test card

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            # Get the customer and validate their address and phone
            customer = get_user_model().objects.get(
                id=self.context['id'])
            if getattr(customer, 'address', None) is None:
                raise serializers.ValidationError(
                    'Your address should not be empty')
            if getattr(customer, 'phone', None) is None:
                raise serializers.ValidationError(
                    'Your phone should not be empty')

            # Create the order
            order = Order.objects.create(customer=customer)

            # Get the cart items and create the order items
            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            # Calculate the total cost of the
            total_cost = int(sum(
                item.unit_price * item.quantity for item in order_items)*100)
        # Set the Stripe API key
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        payment_method_card = stripe.PaymentMethod.create(
            type='card',
            card={
                'number': '4242424242424242',
                'exp_month': 12,
                'exp_year': 2030,
                'cvc': 123,
            },
        )

        customer_stripe = stripe.Customer.create(
            description='Test customer',
            email='test@example.com',
            name='Test Customer',
            phone='+1234567890',
        )
        # Create the payment
        payment = stripe.PaymentIntent.create(
            amount=total_cost,
            currency='usd',
            payment_method=payment_method_card,
            confirm=True,
            customer=customer_stripe,
            error_on_requires_action=True,
            metadata={
                'order_id': order.id
            }
        )

        # Check if the payment was successful
        if payment.status == 'succeeded':
            order.payment_status = Order.COMPLETE
            order.save()
        else:
            order.payment_status = Order.FAILED
            order.save()

        # Delete the cart
        Cart.objects.filter(pk=cart_id).delete()

        # Send a signal that the order has been created
        order_created.send_robust(self.__class__, order=order)

        return order
