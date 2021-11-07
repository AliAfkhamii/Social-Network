from rest_framework import serializers

from .models import User, Profile


# class EmailTokenAuthentication(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField()


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

#
# class ProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializers(read_only=True)
#
#     class Meta:
#         model = Profile
#         fields = ...
