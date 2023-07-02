from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class PasswordField(serializers.CharField):
    ...

    def __init__(self, **kwargs):
        kwargs.setdefault('write_only', True)
        kwargs.setdefault('required', True)
        super().__init__(**kwargs)
        self.validators.append(validate_password)
