import secrets

from django.conf import settings

ORDER_NUMBER_PREFIX = getattr(settings, 'ORDER_NUMBER_PREFIX', 'SC-')


def order_number():
    """Генерация уникального номера заказа для отправки в сбербанк.

    Размер номера заказа в байтах не должен превышать 32 байт.
    Функция вычисляет размер префикса заказа и генерирует строку
    в зависимости от размера префикса.
    """
    prefix_size = len(ORDER_NUMBER_PREFIX.encode('ascii'))
    if prefix_size > 16:
        raise ValueError('Размер префикса не может превышать 16 байт.')
    random_string = secrets.token_hex(8)
    return ORDER_NUMBER_PREFIX + random_string

generate_order_number = getattr(settings, 'generate_order_number', order_number)
