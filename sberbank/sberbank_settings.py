import uuid

from django.conf import settings

ORDER_NUMBER_PREFIX = getattr(settings, 'ORDER_NUMBER_PREFIX', 'SC')


def order_number():
    """Генерация уникального номера заказа для отправки в сбербанк."""
    uid = uuid.uuid4()
    return f'{ORDER_NUMBER_PREFIX}-{uid}'


generate_order_number = getattr(settings, 'generate_order_number', order_number)
