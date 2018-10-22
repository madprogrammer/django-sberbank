from requests import RequestException


class NetworkException(RequestException):
    def __init__(self, payment_id):
        self.payment_id = payment_id
        super().__init__('Network error. Payment ID {}'.format(payment_id))


class ProcessingException(RequestException):
    def __init__(self, payment_id, error_text=None, error_code=None):
        self.payment_id = payment_id
        self.error_text = error_text
        self.error_code = int(error_code) if error_code else None
        super().__init__('Bank error. Payment ID {}. Info: {} {}'.format(
            payment_id, error_text, error_code))


class PaymentNotFoundException(Exception):
    def __init__(self):
        super().__init__('Payment_id not found in DB')
