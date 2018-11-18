from sberbank.models import Payment, Status, Method
from sberbank.util import system_name
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    pan = serializers.SerializerMethodField()
    system = serializers.SerializerMethodField()
    method = serializers.SerializerMethodField()

    def get_method(self, obj):
        return Method(obj.method).name

    def get_status(self, obj):
        return Status(obj.status).name

    def get_pan(self, obj):
        return obj.details.get('pan')

    def get_system(self, obj):
        return system_name(self.get_pan(obj))

    class Meta:
        model = Payment
        fields = ['uid', 'amount', 'status', 'updated', 'pan', 'system']
