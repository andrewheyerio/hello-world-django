from rest_framework import serializers

from core.models import Product, Link, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # This is the model that we want to serialize
        fields = ['id', 'first_name', 'last_name', 'email', 'password',
                  'is_ambassador']  # The fields from the model we want to serialize
        extra_kwargs = {  # We need to make a configuration for the password, we only want to store not
            'password': {'write_only': True}
        }


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = Link
        fields = '__all__'
