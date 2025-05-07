from django.db import models

class ChatbotCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Chatbot Categories"

class ChatbotFAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    category = models.ForeignKey(ChatbotCategory, on_delete=models.CASCADE)
    keywords = models.TextField(help_text="Comma-separated keywords for improved matching")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.question[:50]
    
    class Meta:
        verbose_name = "Chatbot FAQ"
        verbose_name_plural = "Chatbot FAQs"

class ChatbotFeedback(models.Model):
    faq = models.ForeignKey(ChatbotFAQ, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    helpful = models.BooleanField(default=False)
    user_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback on: {self.question[:30]}"
