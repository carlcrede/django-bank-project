from rest_framework import serializers
from .models import ExternalTransfer

class ExternalTransferSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('idempotency_key', 'status', 'created_at')