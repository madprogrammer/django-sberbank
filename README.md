[![PyPI version fury.io](https://badge.fury.io/py/django-sberbank.svg)](https://pypi.python.org/pypi/django-sberbank/)
[![PyPI license](https://img.shields.io/pypi/l/django-sberbank.svg)](https://pypi.python.org/pypi/django-sberbank/)

# Оплата через платежный API Сбербанка в Django
Это Django-приложение позволяет быстро приделать к сайту на Django прием оплаты с банковских карт с помощью платежного API Сбербанка. Приложение поддерживает:

* Оплату через веб-формы (пользователь вводит данные карты на сервере Сбербанка)
* Оплату с помощью Apple Pay и Google Pay
* Привязку банковских карт и получение списка привязанных карт
* Отслеживание истории транзакций и журналирование обмена с API Сбербанка в БД

## Установка
1. Добавить `sberbank` в список INSTALLED_APPS:
```python
INSTALLED_APPS = [
  ...
  'sberbank',
  ...
]
```
2. Добавить параметры мерчанта в `settings.py`:
```python
MERCHANTS = {
  %merchant_id%: {
    'username': '%merchant_username%',
    'password': '%merchant_password%',
    'success_url': 'http://ваш.домен/sberbank/payment/success',
    'fail_url': 'http://ваш.домен/sberbank/payment/fail',
    'app_success_url': 'http://ваш.домен/payment/success',
    'app_fail_url': 'http://ваш.домен/payment/fail',
  }
}
```
3. Добавить URL-ы приложения в ваш `urls.py`:
```python
urlpatterns = [
  ...
  url('/sberbank', include('sberbank.urls'))
]

```
4. Запустить `python manage.py migrate` чтобы создать модели.

## Установка окружения

Переменная окружения: `ENVIRONMENT`

Возможные значения:
* `development` - https://securepayments.sberbank.ru/payment
* `production` - https://3dsec.sberbank.ru/payment

По-умолчанию: `development`

## Параметры словаря `MERCHANTS`
* `success_url` - на данный URL Сбербанк будет перенаправлять браузер после успешного платежа
* `fail_url` - на данный URL Сбербанк будет перенаправлять браузер после неуспешного платежа
* `app_success_url` - это URL, с помощью которого ваше приложение может среагировать на успешный платеж после того, как отработает коллбэк `success_url`.
* `app_fail_url` - это URL, с помощью которого ваше приложение может среагировать на неуспешный платеж после того, как отработает коллбэк `fail_url`.

## Использование
### Платеж с помощью веб-формы

```python
from sberbank.service import BankService
from sberbank.models import Payment, Status

...
try:
    # Сумма в рублях
    amount = 10.0

    # Уникальный ID пользователя, используется для привязки карт
    # Если None, пользователь не сможет выбрать ранее привязанную карту
    # или привязать карту в процессе оплаты
    client_id = request.data.get("client_id")

    svc = BankService(%merchant_id%)

    # url - адрес, на который следует перенаправить пользователя для оплаты
    # payment - объект Payment из БД, содержит информацию о платеже
    # description - назначение платежа в веб-форме банка
    # params - произвольные параметры, которые можно привязать к платежу
    payment, url = svc.pay(amount, params={'foo': 'bar'}, client_id=client_id,
        description="Оплата заказа №1234")
    return HttpResponseRedirect(url)
except Exception as exc:
    # Что-то пошло не так
    raise
```
### Привязка карты со списанием и возвратом 1 рубля

```python
from sberbank.service import BankService
from sberbank.models import Payment, Status

...
try:
    # Уникальный ID пользователя, используется для привязки карт
    # параметр необходимо передавать при использовании функции привязки карт
    # через списание и возврат
    client_id = request.data.get("client_id")
    if client_id is None:
        return HttpResponseBadRequest()

    svc = BankService(%merchant_id%)

    # url - адрес, на который следует перенаправить пользователя для оплаты
    # payment - объект Payment из БД, содержит информацию о платеже
    payment, url = svc.bind_refund(client_id=client_id)
    return HttpResponseRedirect(url)
except Exception as exc:
    # Что-то пошло не так
    raise
```
### Оплата с помощью Apple/Google Pay

```python
from sberbank.service import BankService
from sberbank.models import Payment, Status

...
try:
    # Уникальный ID пользователя, используется для привязки карт
    # параметр необходимо передавать при использовании функции привязки карт
    # через списание и возврат
    client_id = request.data.get("client_id")

    # Сумма платежа в рублях
    amount = 10.0

    # Токен, переданный приложением для Apple/Android
    # библиотека сама определяет тип платежа по формату
    # переданного токена и вызывает соответствующее API Сбербанка
    token = request.data.get("token")

    # IP адрес клиента
    ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

    svc = BankService(%merchant_id%)

    payment, response = svc.mobile_pay(amount, token, ip, client_id=client_id,
      params={'foo': 'bar'}, description="Оплата заказа №1234")
    
    if response['success'] != True:
        return Response({"status": "error"})
    if payment.status == Status.SUCCEEDED:
        # Платеж успешен
    json_response = {"status": "success"}

    # Платежи с некоторых карт требуют особой обработки на клиенте
    # При наличии в ответе acsUrl клиенту нужно перенаправить пользователя
    # на адрес redirect_url, POST-запросом передав параметры в виде x-www-form-urlencoded
    if response['data'].get('acsUrl'):
        json_response.update({"redirect_url": response['data'].get('acsUrl', '')})
        json_response.update({"params": {
            'paReq': response['data'].get('paReq', ''),
            'termUrl': response['data'].get('termUrl', ''),
            'orderId': response['data'].get('orderId', '')}})
    return Response(json_response)
except Exception as exc:
    # Что-то пошло не так
    raise
```

### Периодическая проверка платежей по которым не известно состояние

```python
from datetime import timedelta
from celery.task import periodic_task
from sberbank.tasks import check_payments

@periodic_task(run_every=timedelta(minutes=20))
def task_check_payments():
    check_payments()
```


### Настройки
```python
ORDER_NUMBER_PREFIX - Префикс номера заказа. По умолчанию 'SC-'.
```