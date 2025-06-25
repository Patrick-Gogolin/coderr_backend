from rest_framework import serializers
from user_auth_app.models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(allow_blank=True, default='')
    last_name = serializers.CharField(allow_blank=True, default='')

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'type', 'created_at']
    
    def validate_email(self, value):
        user = self.instance.user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This Email is already in use!")
        return value
    
    def update(self, instance, validated_data):
        user = instance.user
        email = validated_data.pop('email', None)
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)

        user_changed = False

        if email is not None:
            user.email = email
            user_changed = True
        if first_name is not None:
            user.first_name = first_name
            user_changed = True
        if last_name is not None:
            user.last_name = last_name
            user_changed = True
        
        if user_changed:
            user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['email'] = instance.user.email
        data['first_name'] = instance.user.first_name
        data['last_name'] = instance.user.last_name
        return data

class CustomerProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type'
        ]

class BusinessProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, default='')
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, default='')

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description',
            'working_hours', 'type',
        ]