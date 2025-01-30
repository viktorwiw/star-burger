from collections import defaultdict
import logging

from django import forms
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance
import requests

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderDetails


logger = logging.getLogger(__name__)


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    geo_apikey = settings.GEO_API_KEY

    orders = Order.objects.total_price().exclude(status='ready').prefetch_related(
        Prefetch('details', queryset=OrderDetails.objects.select_related('product'))
    ).order_by('-status')
    restaurant_items = RestaurantMenuItem.objects.select_related('restaurant', 'product').filter(availability=True)

    products_in_restaurant = defaultdict(set)
    for item in restaurant_items:
        products_in_restaurant[item.product].add(item.restaurant)

    order_items = []
    for order in orders:
        order_products = [detail.product for detail in order.details.all()]

        if not order_products:
            available_restaurants = []
        else:
            restaurants_for_products = [
                products_in_restaurant[product] for product in order_products
            ]

            available_restaurants = set.intersection(*restaurants_for_products)

        client_address = order.address
        order_coords = fetch_coordinates(geo_apikey, client_address)

        restaurant_with_distance = []
        for restaurant in available_restaurants:
            restaurant_coords = fetch_coordinates(geo_apikey, restaurant.address)

            if restaurant_coords and order_coords:
                restaurant_with_distance.append({
                    'restaurant_name': restaurant.name,
                    'distance': round(distance.distance(order_coords, restaurant_coords).km, 2)
                })
        sorted_restaurants = sorted(restaurant_with_distance, key=lambda restaurant: restaurant['distance'])
        order_items.append({
            'order': order,
            'restaurants': sorted_restaurants,
        })
        logger.info(f'Ордер {order_items}')
    return render(request, 'order_items.html', {
        'order_items': order_items,
    })


def fetch_coordinates(geo_apikey, address):
    try:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": geo_apikey,
            "format": "json",
            },
            timeout=5
        )
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return lon, lat

    except requests.exceptions.RequestException as e:
        logger.error(e)
        return None
