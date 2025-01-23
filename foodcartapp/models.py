from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=250,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def total_price(self):
        return self.annotate(
            total_price=Sum(F('details__quantity') * F('details__price'))
        ).order_by('id')



class Order(models.Model):
    PROCESSING_STATUS_CHOICES = (
        ('raw', 'Необработанный'),
        ('assembled', 'Cборка'),
        ('delivery', 'Доставка'),
        ('ready', 'Готов'),
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default='raw',
        db_index=True,
    )
    PAYMENT_STATUS_CHOICES = (
        ('cash', 'Наличностью'),
        ('electronic', 'Электронно'),
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='cash',
        db_index=True
    )
    address = models.CharField('Адрес', max_length=150, db_index=True)
    firstname = models.CharField('Имя', max_length=50, db_index=True)
    lastname = models.CharField('Фамилия', max_length=50, db_index=True)
    phonenumber = PhoneNumberField('Мобильный номер', db_index=True)
    comment = models.TextField('Комментарий', blank=True)
    registrated_at = models.DateTimeField(
        'Время регистрации',
        default=timezone.now,
        db_index=True
    )
    called_at = models.DateTimeField(
        'Время звонка',
        db_index=True,
        blank=True,
        null=True
    )
    delivered_at = models.DateTimeField(
        'Время доставки',
        db_index=True,
        blank=True,
        null=True
    )
    objects = OrderQuerySet.as_manager()

    @property
    def full_name(self):
        return f"{self.firstname} {self.lastname}"

    def __str__(self):
        return f'Заказ № {self.id} - {self.firstname} {self.lastname}, {self.address}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['id']


class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='details',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='products',)
    quantity = models.PositiveIntegerField(
        'Количество',
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    price = models.DecimalField(
        'Цена продукта',
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f'{self.product} {self.order.firstname} {self.order.lastname} {self.order.address}'

    class Meta:
        verbose_name = 'Элементы заказа'
        verbose_name_plural = 'Элементы заказа'
