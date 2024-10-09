from rest_framework import serializers
from .models import ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):
    channel_id = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = (
            'id',
            'user',
            'datetime',
            'title',
            'has_messages',
            'messages',
            'channel_id',
            'files'
        )

    def get_channel_id(self, obj):
        return obj.channel_id

    def get_messages(self, obj):
        return []
