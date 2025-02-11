from rest_framework.serializers import ModelSerializer
from rest_framework.templatetags.rest_framework import items

from foodcartapp.models import Order, OrderDetails\


class OrderDetailsSerializer(ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderDetailsSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']


    def create(self, validated_data):
        products_fields = validated_data.pop('products')

        order = super().create(validated_data)

        order_details = [
            OrderDetails(
                order=order,
                **fields
            )
        for fields in products_fields
        ]

        OrderDetails.objects.bulk_create(order_details)
        return order
