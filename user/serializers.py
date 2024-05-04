from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email", "is_staff")
        read_only_fields = ("is_staff",)
        extra_kwargs = {
            "password":
                {
                    "<PASSWORD>": True,
                    "write_only": True,
                    "min_length": 8,
                    "max_length": 16,
                }
        }
    
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        
        return user
