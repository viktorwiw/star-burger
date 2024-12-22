import logging

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from phonenumber_field.phonenumber import PhoneNumber

from .models import Product, Order, OrderDetails


logger = logging.getLogger(__name__)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate_field(data, field):
    if field not in data:
        return f"Ключ '{field}' отсутствует - это обязательное поле"
    elif data.get(field) is None:
        return f"Ключ '{field}' не может быть пустым(равен None)"
    elif not data.get(field):
        return f"Ключ '{field}' имеет пустое значение"


@api_view(['POST'])
def register_order(request):
    preorder = request.data

    string_fields = ['firstname', 'lastname', 'address', 'phonenumber']
    errors = {f'the key {field} value must not be a list' for field in string_fields if isinstance(preorder.get(field), list)}
    if errors:
        return Response({'error': errors}, status=400)

    required_fields = [
        'products',
        'firstname',
        'lastname',
        'phonenumber',
        'address'
    ]
    errors = {validate_field(preorder,field) for field in required_fields if validate_field(preorder, field)}
    if errors:
        return Response({'errors': errors}, status=400)

    if not isinstance(preorder.get('products'), list):
        return Response(
            {'error': 'the key products value was expected list with values'},
            status=400
        )

    phone = PhoneNumber.from_string(preorder.get('phonenumber'))
    if not PhoneNumber.is_valid(phone):
        return Response(
            {'error': 'the key phonenumber is invalid'},
            status=400
        )

    order = Order.objects.create(
        address=preorder.get('address'),
        name = preorder.get('firstname'),
        surname = preorder.get('lastname'),
        phone_number = preorder.get('phonenumber'),
    )

    for item in preorder.get('products'):
        amount = item.get('quantity')

        product_id = item.get('product')
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product does not exist'},
                status=400
            )

        OrderDetails.objects.create(
            order=order,
            product = product,
            amount = amount,
        )
    return Response({'message': 'Order created'})
