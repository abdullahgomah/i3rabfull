from django.shortcuts import render
from .forms import I3rabForm
from .services.i3rab_service import analyze_sentence, normalize_arabic_word
from .models import GlobalIrabRecord

def i3rab_view(request):
    """
    Main view for Arabic i'rab analysis with Global Registry.
    """
    form = I3rabForm()
    result = None
    error = None

    if request.method == 'POST':
        form = I3rabForm(request.POST)
        if form.is_valid():
            sentence = form.cleaned_data['sentence']
            # Call the OpenAI service (returns a dict or error dict)
            analysis_result = analyze_sentence(sentence)
            
            if "error" in analysis_result:
                error = analysis_result["error"]
            else:
                result = analysis_result
                # Save each word to the Global Registry
                try:
                    words_data = analysis_result.get("words", [])
                    sentence_summary = analysis_result.get("sentence_irab_summary", "")
                    
                    for word_item in words_data:
                        GlobalIrabRecord.objects.create(
                            word=word_item.get("word", ""),
                            normalized_word=normalize_arabic_word(word_item.get("word", "")),
                            sentence=sentence,
                            word_order=word_item.get("word_order", 0),
                            grammatical_type=word_item.get("grammatical_type", ""),
                            irab=word_item.get("irab", ""),
                            reason=word_item.get("reason", ""),
                            sentence_irab_summary=sentence_summary,
                            notes=word_item.get("notes", "")
                        )
                except Exception as e:
                    # Log error but don't crash the user experience
                    print(f"Error saving records: {e}")
        else:
            error = "الرجاء التأكد من صحة الجملة المدخلة."

    return render(request, 'api/i3rab.html', {
        'form': form,
        'result': result,
        'error': error
    })
