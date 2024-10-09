from rest_framework import serializers
from core.models import Document


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = [
            'id',
            'created_on',
            'content',
            'content_lang',
            'title',
            'summary',
            'summary_lang',
            'url',
            'image',
            'embedding',
            'namespace',
            'file',
            'folder',
            'context',
            'other_rights',
            'user_rights',
            'group_rights',
            'state'
        ]
