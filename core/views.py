import os
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Document
from .serializers import (
    DocumentUploadSerializer,
    DocumentListSerializer,
    DocumentDetailSerializer
)
from .utils.extractor import get_file_type
from .tasks import process_document

logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    """
    POST /api/documents/upload/
    File upload karo aur background processing start karo
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # File check karo
        if 'file' not in request.FILES:
            return Response(
                {"error": "No file provided. Please upload a PDF, DOCX, or TXT file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES['file']

        # File type validate karo
        try:
            file_type = get_file_type(file.name)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # File size check karo (max 10MB)
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            return Response(
                {"error": "File too large. Maximum allowed size is 10MB."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Document create karo
            document = Document.objects.create(
                file=file,
                file_name=file.name,
                file_type=file_type,
                file_size=file.size,
                status='pending'
            )

            # Celery background task trigger karo
            process_document.delay(document.id)

            logger.info(f"Document uploaded: {file.name} (ID: {document.id})")

            return Response(
                {
                    "message": "File uploaded successfully. Processing started.",
                    "document_id": document.id,
                    "file_name": document.file_name,
                    "status": document.status
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return Response(
                {"error": f"Upload failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentListView(APIView):
    """
    GET /api/documents/
    Sabhi documents ki list return karo
    """

    def get(self, request):
        try:
            documents = Document.objects.all()

            # Optional filter by status
            status_filter = request.query_params.get('status', None)
            if status_filter:
                documents = documents.filter(status=status_filter)

            serializer = DocumentListSerializer(documents, many=True)

            return Response(
                {
                    "count": documents.count(),
                    "documents": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"List fetch failed: {str(e)}")
            return Response(
                {"error": f"Failed to fetch documents: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentDetailView(APIView):
    """
    GET /api/documents/<id>/
    Specific document ki full detail return karo
    """

    def get(self, request, pk):
        try:
            document = get_object_or_404(Document, pk=pk)
            serializer = DocumentDetailSerializer(document)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Detail fetch failed for ID {pk}: {str(e)}")
            return Response(
                {"error": f"Failed to fetch document: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentStatusView(APIView):
    """
    GET /api/documents/<id>/status/
    Document processing status check karo
    """

    def get(self, request, pk):
        try:
            document = get_object_or_404(Document, pk=pk)

            return Response(
                {
                    "document_id": document.id,
                    "file_name": document.file_name,
                    "status": document.status,
                    "error_message": document.error_message,
                    "updated_at": document.updated_at
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to fetch status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )