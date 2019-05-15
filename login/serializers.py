# api/serializers.py

from rest_framework import serializers
from .models import URL


class LoginSerializer(serializers.ModelSerializer):
    # serializer to map the model instance into JSON format

    class Meta:
        # meta class to map serializer's fields with the model fields.
        model = URL
        owner = serializers.ReadOnlyField(source='owner.username')
        fields = ('apiserver_url', 'login_api_url',
                  'access_level', 'methods', 'owner',
                  'ip_address_limiter', 'active', 'created', 'modified')
        read_only_fields = ('created', 'modified')

