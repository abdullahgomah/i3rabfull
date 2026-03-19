from django import forms

class I3rabForm(forms.Form):
    sentence = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'أدخل الجملة العربية هنا...',
            'rows': 3,
            'class': 'form-control'
        }),
        label='الجملة المراد إعرابها',
        required=True
    )

    def clean_sentence(self):
        sentence = self.cleaned_data.get('sentence', '').strip()
        if not sentence:
            raise forms.ValidationError("الرجاء إدخال جملة صالحة.")
        if len(sentence) < 2:
            raise forms.ValidationError("الجملة قصيرة جداً، يرجى إدخال جملة كاملة.")
        return sentence
