from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Represents a customer support conversation"""
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.id}: {self.title or 'Untitled'}"


class Message(models.Model):
    """Individual messages within a conversation"""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField()
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.text[:50]}"


class ConversationAnalysis(models.Model):
    """Post-conversation analysis results"""
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]
    
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    
    # Scoring metrics (0-100)
    clarity_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    accuracy_score = models.FloatField(default=0.0)
    completeness_score = models.FloatField(default=0.0)
    empathy_score = models.FloatField(default=0.0)
    
    # Additional metrics
    fallback_count = models.IntegerField(default=0)
    sentiment = models.CharField(
        max_length=10,
        choices=SENTIMENT_CHOICES,
        default='neutral'
    )
    resolution = models.BooleanField(default=False)
    escalation_needed = models.BooleanField(default=False)
    avg_response_time_seconds = models.FloatField(default=0.0)
    overall_score = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Conversation Analyses'
    
    def __str__(self):
        return f"Analysis for Conversation {self.conversation.id}"