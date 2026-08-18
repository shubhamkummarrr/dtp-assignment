import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

SUMMARY_PROMPT_TEMPLATE = """You are an intelligent document analyzer. Analyze the following document text and return a structured JSON response.

Document Text:
{text}

Return ONLY a valid JSON object with exactly these fields:
{{
    "title": "A concise and descriptive title for the document",
    "summary": "A comprehensive summary of the document in 3-5 sentences",
    "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "language": "The language of the document",
    "word_count": 123
}}

Rules:
- Return ONLY the JSON object
- No extra text, no explanation
- keywords must be a list of 5 strings
- word_count must be an integer
- Do not wrap in markdown or code blocks"""


def get_client():
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)


def analyze_document(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("Empty text provided for analysis")

    # Token limit ke liye trim karo
    max_chars = 3000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[Document truncated...]"

    try:
        client = get_client()
        prompt = SUMMARY_PROMPT_TEMPLATE.replace("{text}", text)

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

        raw = response.choices[0].message.content
        print(f"RAW LLM RESPONSE: '{raw[:200]}'")

        if not raw or not raw.strip():
            raise ValueError("Empty response from LLM")

        return _parse_llm_response(raw)

    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"LLM analysis failed: {str(e)}")


def _parse_llm_response(response: str) -> dict:
    cleaned = response.strip()

    # Thinking tags remove karo
    if "<think>" in cleaned and "</think>" in cleaned:
        think_end = cleaned.find("</think>") + len("</think>")
        cleaned = cleaned[think_end:].strip()

    # Markdown code blocks remove karo
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # First aur last line hatao
        cleaned = "\n".join(lines[1:-1])

    cleaned = cleaned.strip()

    if not cleaned:
        raise ValueError("Empty response from LLM after cleaning")

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # JSON manually dhundo
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                data = json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                raise ValueError(f"Could not parse LLM response as JSON: {cleaned[:200]}")
        else:
            raise ValueError(f"No JSON found in response: {cleaned[:200]}")

    # Required fields ensure karo
    required_fields = ["title", "summary", "keywords", "language", "word_count"]
    for field in required_fields:
        if field not in data:
            data[field] = "" if field != "keywords" else []

    # Type safety
    if not isinstance(data["keywords"], list):
        data["keywords"] = [str(data["keywords"])]

    if not isinstance(data["word_count"], int):
        try:
            data["word_count"] = int(data["word_count"])
        except:
            data["word_count"] = 0

    return data