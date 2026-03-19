from django.contrib import admin
from .models import GrammarNote, GlobalIrabRecord

@admin.register(GrammarNote)
class GrammarNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')

@admin.register(GlobalIrabRecord)
class GlobalIrabRecordAdmin(admin.ModelAdmin):
    list_display = ('word', 'grammatical_type', 'sentence', 'created_at')
    list_filter = ('grammatical_type', 'created_at')
    search_fields = ('word', 'normalized_word', 'sentence', 'irab', 'reason')
    readonly_fields = ('created_at',)
