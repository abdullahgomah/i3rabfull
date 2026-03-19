from django.db import models

class GrammarNote(models.Model):
    title = models.CharField(max_length=255, verbose_name="العنوان")
    content = models.TextField(verbose_name="المحتوى")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "ملاحظة نحوية"
        verbose_name_plural = "ملاحظات نحوية"
        ordering = ['-created_at']

class GlobalIrabRecord(models.Model):
    word = models.CharField(max_length=100, verbose_name="الكلمة")
    normalized_word = models.CharField(max_length=100, db_index=True, verbose_name="الكلمة المعيارية")
    sentence = models.TextField(verbose_name="الجملة")
    word_order = models.PositiveIntegerField(verbose_name="الترتيب")
    grammatical_type = models.CharField(max_length=100, verbose_name="النوع النحوي")
    irab = models.TextField(verbose_name="الإعراب")
    reason = models.TextField(verbose_name="السبب")
    sentence_irab_summary = models.TextField(verbose_name="ملخص إعراب الجملة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "سجل إعراب عالمي"
        verbose_name_plural = "سجل الإعراب العالمي"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.word} ({self.grammatical_type})"
