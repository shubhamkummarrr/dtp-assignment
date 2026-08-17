from django.db import models


class Document(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'DOCX'),
        ('txt', 'TXT'),
    ]

    # File info
    file = models.FileField(upload_to='documents/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    file_size = models.IntegerField(default=0)  # bytes mein

    # Extracted content
    extracted_text = models.TextField(blank=True, null=True)

    # LLM Response
    title = models.CharField(max_length=500, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    keywords = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    word_count = models.IntegerField(default=0)

    # Status & Timestamps
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} ({self.status})"