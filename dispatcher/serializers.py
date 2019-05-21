# api/serializers.py

from rest_framework import serializers
from .models import URL


class URLSerializer(serializers.ModelSerializer):
    # serializer to map the model instance into JSON format

    class Meta:
        # meta class to map serializer's fields with the model fields.
        model = URL
        owner = serializers.ReadOnlyField(source='owner.username')
        fields = ('apiserver_url', 'api_rules',
                  'access_level', 'methods', 'owner',
                  'ip_address_limiter', 'active', 'created', 'modified')
        read_only_fields = ('created', 'modified')

