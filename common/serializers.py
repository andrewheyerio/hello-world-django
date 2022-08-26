from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User   # This is the model that we want to serialize
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'is_ambassador']  #The fields from the model we want to serialize
        extra_kwargs = { # We need to make a configuration for the password, we only want to store not
            'password' : {'write_only' : True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None) # We get the data and set a default value to none
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) # the set password is from django to hash to password
        instance.save()
        return instance