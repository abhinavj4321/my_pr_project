from django.contrib import admin
from .models import ChatbotCategory, ChatbotFAQ, ChatbotFeedback
from import_export.admin import ImportExportModelAdmin

class ChatbotFAQAdmin(ImportExportModelAdmin):
    list_display = ('question', 'category', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('question', 'answer', 'keywords')

class ChatbotFeedbackAdmin(admin.ModelAdmin):
    list_display = ('question', 'helpful', 'created_at')
    list_filter = ('helpful', 'created_at')
    search_fields = ('question',)

admin.site.register(ChatbotCategory)
admin.site.register(ChatbotFAQ, ChatbotFAQAdmin)
admin.site.register(ChatbotFeedback, ChatbotFeedbackAdmin)

# Register your models here.
