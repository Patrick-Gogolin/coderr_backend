from rest_framework import serializers
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.Serializer):

       """
       Serializer for user registration.

       Fields:
        - username: Required, unique username for the user.
        - email: Required, unique email address.
        - password: Required, write-only password field.
        - repeated_password: Required, write-only field to confirm the password.
        - type: User type choice between 'customer' and 'business'. Default is 'customer'.

       Validations:
        - Password and repeated_password must match.
        - Username must be unique.
        - Email must be unique.

       Methods:
        - create: Creates a new User instance with the validated data.
       """
       
       USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]
       username = serializers.CharField()
       email = serializers.EmailField()
       password = serializers.CharField(write_only=True)
       repeated_password = serializers.CharField(write_only=True)
       type = serializers.ChoiceField(choices=USER_TYPE_CHOICES, default='customer')

       def validate(self, data):
              """
              Check that passwords match and that username/email are unique.
              """
              if data['password'] != data['repeated_password']:
                     raise serializers.ValidationError("Passwords do not match.")
              if User.objects.filter(username=data['username']).exists():
                     raise serializers.ValidationError("Username already exists")
              if User.objects.filter(email=data['email']).exists():
                     raise serializers.ValidationError("Email already exists")
              return data
       
       def create(self, validated_data):
              """
              Create and return a new User instance.
              """
              user = User.objects.create_user(
                     username = validated_data['username'],
                     email=validated_data['email'],
                     password=validated_data['password']
              )
              return user

class LoginSerializer(serializers.Serializer):
       """
       Serializer for user login.

       Fields:
        - username: Required username.
        - password: Required, write-only password.

       Validations:
        - Checks if the username exists.
        - Authenticates user credentials.

       Returns:
        - Adds the authenticated user to the validated data.
       """
       username = serializers.CharField()
       password = serializers.CharField(write_only=True)

       def validate(self, data):
            username = data.get('username')
            password = data.get('password')

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                  raise serializers.ValidationError("User with this username does not exist.")
            
            user = authenticate(username=username, password=password)

            if not user:
                  raise serializers.ValidationError("Invalid credentials.")
            
            data['user'] = user
            
            return data