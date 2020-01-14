import random
import string

from django.conf import settings

ORDER_NUMBER_PREFIX = getattr(settings, 'ORDER_NUMBER_PREFIX', 'SC')
ORDER_NUMBER_PREFIX_SEPARATOR = getattr(settings, 'ORDER_NUMBER_PREFIX_SEPARATOR', '-')

def generate_random_string(size):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))

def order_number():
    """Генерация уникального номера заказа для отправки в сбербанк.

    Размер номера заказа в байтах не должен превышать 32 байт.
    Функция вычисляет размер префикса заказа и генерирует строку
    в зависимости от размера префикса.
    """
    full_prefix = ORDER_NUMBER_PREFIX + ORDER_NUMBER_PREFIX_SEPARATOR
    full_prefix_size = len(full_prefix.encode('ascii'))
    string_size = 32 - full_prefix_size
    random_string = generate_random_string(string_size)
    return full_prefix + random_string

generate_order_number = getattr(settings, 'generate_order_number', order_number)
