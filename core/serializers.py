from core.fields import PasswordField
from core.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, exceptions


class CreateUserSerializer(serializers.ModelSerializer):
    password = PasswordField()
    confirmed_password = PasswordField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'confirmed_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmed_password']:
            raise exceptions.ValidationError('Passwords must match')
        return attrs

    def create(self, validated_data):
        del validated_data['confirmed_password']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)