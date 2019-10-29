from sberbank.models import Payment, Status, Method
from sberbank.util import system_name
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    pan = serializers.SerializerMethodField()
    system = serializers.SerializerMethodField()
    method = serializers.SerializerMethodField()

    @staticmethod
    def get_method(obj):
        return Method(obj.method).name

    @staticmethod
    def get_status(obj):
        return Status(obj.status).name

    @staticmethod
    def get_pan(obj):
        return obj.details.get('pan')

    def get_system(self, obj):
        return system_name(self.get_pan(obj))

    class Meta:
        model = Payment
        fields = ['uid', 'amount', 'status', 'updated', 'pan', 'system', 'method']
