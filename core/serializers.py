from rest_framework import serializers
from .models import Document


class DocumentUploadSerializer(serializers.ModelSerializer):
    """File upload ke liye serializer"""

    class Meta:
        model = Document
        fields = ['id', 'file', 'file_name', 'file_type',
                  'file_size', 'status', 'created_at']
        read_only_fields = ['id', 'file_name', 'file_type',
                            'file_size', 'status', 'created_at']


class DocumentListSerializer(serializers.ModelSerializer):
    """Document list ke liye — short info"""

    class Meta:
        model = Document
        fields = [
            'id', 'file_name', 'file_type',
            'file_size', 'status', 'title',
            'language', 'word_count', 'created_at'
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Single document ki full detail"""

    class Meta:
        model = Document
        fields = [
            'id', 'file_name', 'file_type', 'file_size',
            'status', 'error_message',
            'extracted_text', 'title', 'summary',
            'keywords', 'language', 'word_count',
            'created_at', 'updated_at'
        ]