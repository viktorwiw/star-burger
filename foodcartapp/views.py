import logging

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@api_view(['POST'])
def register_order(request):
    try:
        preorder = request.data
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON'})

    if 'products' not in preorder:
        return Response({'error': 'no products found'})
    elif isinstance(preorder.get('products'), str):
        return Response({'error': 'products key not presented or not list'})
    elif not preorder['products']:
        return Response({'error': 'no products found'})

    order = Order.objects.create(
        address=preorder.get('address'),
        name = preorder.get('firstname'),
        surname = preorder.get('lastname'),
        phone_number = preorder.get('phonenumber'),
    )

    for item in preorder.get('products'):
        product_id = item.get('product')
        amount = item.get('quantity')
        product = Product.objects.get(pk=product_id)

        OrderDetails.objects.create(
            order=order,
            product = product,
            amount = amount,
        )

    return Response({'message': 'Order created'})
