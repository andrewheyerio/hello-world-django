from rest_framework import serializers

from core.models import Product, Link

# This serailizer is identical to the one administrator is using. Because they are the same perhaps we can move it
# into the common folder
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'
