import os
import json
import re
from openai import OpenAI
from django.conf import settings
from ..models import GrammarNote

def get_openai_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalize_arabic_word(word):
    """
    Simple Arabic word normalization.
    """
    if not word:
        return ""
    word = word.strip()
    # Normalize Alef variants
    word = re.sub(r'[أإآ]', 'ا', word)
    # Normalize Teh Marbuta to Heh (optional, depends on preference)
    # word = re.sub(r'ة', 'ه', word)
    # Remove Diacritics (Tashkeel)
    tashkeel_pattern = re.compile(r'[\u064B-\u0652]')
    word = re.sub(tashkeel_pattern, '', word)
    return word

def build_system_instructions():
    """
    Build the system instructions for the OpenAI Assistant.
    """
    active_notes = GrammarNote.objects.filter(is_active=True)
    local_notes_text = ""
    if active_notes.exists():
        local_notes_text = "\n\nملاحظات نحوية إضافية من قاعدة البيانات المحلية:\n"
        for note in active_notes:
            local_notes_text += f"- {note.title}: {note.content}\n"

    instructions = (
        "أنت خبير في النحو العربي والإعراب. "
        "مهمتك هي تحليل الجمل العربية وإعرابها بدقة وتفصيل. "
        "يجب عليك استخدام أداة البحث في الملفات (file_search) للرجوع إلى قواعد النحو المتاحة. "
        "إذا وجدت تعارضاً، أعطِ الأولوية للمعلومات المستخرجة من المتجر الموجه، ثم الملاحظات المحلية الواردة أدناه. "
        "في حال وجود أكثر من وجه إعرابي، اذكر الوجه الأقوى والأرجح أولاً. "
        "لا تذكر أي تفاصيل تقنية حول كيفية عمل النظام أو أسماء الملفات أو الاستشهادات أو المراجع. "
        f"{local_notes_text}"
        "\n\nيجب أن يكون الرد بصيغة JSON حصراً، وبالهيكل التالي:\n"
        "{\n"
        '  "sentence": "الجملة الأصلية",\n'
        '  "sentence_irab_summary": "ملخص شامل لإعراب الجملة",\n'
        '  "words": [\n'
        '    {\n'
        '      "word": "الكلمة",\n'
        '      "word_order": 1,\n'
        '      "grammatical_type": "النوع النحوي",\n'
        '      "irab": "الإعراب التفصيلي للكلمة",\n'
        '      "reason": "سبب هذا الإعراب",\n'
        '      "notes": "أي ملاحظات إضافية عن الكلمة"\n'
        '    }\n'
        '  ],\n'
        '  "additional_notes": "ملاحظات عامة إضافية إن وجدت"\n'
        "}"
    )
    return instructions

def analyze_sentence(sentence):
    """
    Analyze the given sentence using OpenAI Assistants API with file_search and JSON output.
    """
    client = get_openai_client()
    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    try:
        # Create an Assistant with file_search enabled
        # Note: We specify JSON response format if supported, or rely on instructions
        assistant = client.beta.assistants.create(
            name="Arabic I3rab Expert Structured",
            instructions=build_system_instructions(),
            model=model,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
            response_format={"type": "json_object"}
        )

        # Create a thread
        thread = client.beta.threads.create()

        # Add a message to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"قم بإعراب هذه الجملة بنظام JSON: {sentence}"
        )

        # Run the assistant
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == 'assistant':
                    raw_content = msg.content[0].text.value
                    # Clean potential markdown JSON blocks
                    clean_content = re.sub(r'```json\n|\n```', '', raw_content).strip()
                    try:
                        return json.loads(clean_content)
                    except json.JSONDecodeError:
                        return {"error": "فشل في تحليل الرد المنظم من الذكاء الاصطناعي."}
            return {"error": "لم يتم العثور على رد من الخبير."}
        else:
            return {"error": f"فشل التحليل. الحالة: {run.status}"}

    except Exception as e:
        print(f"OpenAI Error: {e}")
        return {"error": "عذراً، حدث خطأ أثناء الاتصال بخدمة التحليل."}
