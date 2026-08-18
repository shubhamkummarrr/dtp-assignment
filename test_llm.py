import os
import sys
from dotenv import load_dotenv

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtp_assignment.settings')
import django
django.setup()

load_dotenv()

from groq import Groq
from core.utils.extractor import extract_text

# Real document se text nikalo
file_path = r"C:\Users\tally\Downloads\Assignment-AI.pdf"
extracted = extract_text(file_path, 'pdf')

print(f"EXTRACTED TEXT LENGTH: {len(extracted)}")
print(f"FIRST 300 CHARS: {extracted[:300]}")
print("---")

# Trim karo jaise llm.py karta hai
max_chars = 3000
if len(extracted) > max_chars:
    text = extracted[:max_chars] + "\n\n[Document truncated...]"
else:
    text = extracted

print(f"TRIMMED LENGTH: {len(text)}")
print("---")

# Prompt banao
prompt = f"""Analyze this document and return ONLY a JSON object with these fields:
- title: document title
- summary: 2-3 sentence summary
- keywords: list of 5 keywords
- language: document language
- word_count: integer word count

Document:
{text}

Return ONLY JSON, no markdown, no explanation."""

print(f"PROMPT LENGTH: {len(prompt)}")
print("---")

# LLM call karo
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": "You are a document analyzer. Return only valid JSON. No markdown. No explanation."
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    temperature=0.1,
    max_tokens=8000,
)

print("CONTENT:", repr(response.choices[0].message.content))
print("FINISH REASON:", response.choices[0].finish_reason)
print("USAGE:", response.usage)