from celery import shared_task
from django.utils import timezone
from .models import Document
from .utils.extractor import extract_text
from .utils.llm import analyze_document
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, document_id: int):
    """
    Celery background task — document process karo
    1. Text extract karo
    2. LLM se analyze karo
    3. Database update karo
    """
    try:
        # Document fetch karo
        document = Document.objects.get(id=document_id)

        # Status — processing
        document.status = 'processing'
        document.save(update_fields=['status', 'updated_at'])

        logger.info(f"Processing document {document_id}: {document.file_name}")

        # Step 1 — Text extract karo
        file_path = document.file.path
        extracted_text = extract_text(file_path, document.file_type)
        document.extracted_text = extracted_text
        document.save(update_fields=['extracted_text', 'updated_at'])

        logger.info(f"Text extracted for document {document_id}")

        # Step 2 — LLM se analyze karo
        llm_result = analyze_document(extracted_text)

        # Step 3 — Results save karo
        document.title = llm_result.get('title', '')
        document.summary = llm_result.get('summary', '')
        document.keywords = llm_result.get('keywords', [])
        document.language = llm_result.get('language', '')
        document.word_count = llm_result.get('word_count', 0)
        document.status = 'completed'
        document.error_message = None
        document.save()

        logger.info(f"Document {document_id} processed successfully")
        return {"status": "success", "document_id": document_id}

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Error processing document {document_id}: {str(exc)}")

        # Document status failed karo
        try:
            document = Document.objects.get(id=document_id)
            document.status = 'failed'
            document.error_message = str(exc)
            document.save(update_fields=['status', 'error_message', 'updated_at'])
        except Exception:
            pass

        # Retry logic — 3 baar try karega
        raise self.retry(exc=exc, countdown=60)