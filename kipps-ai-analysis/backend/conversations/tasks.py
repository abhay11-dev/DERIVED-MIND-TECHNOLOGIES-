from celery import shared_task
from django.db.models import Q
from .models import Conversation, ConversationAnalysis
from .analysis import ConversationAnalyzer


@shared_task
def analyze_conversation_task(conversation_id):
    """
    Celery task to analyze a single conversation.
    
    Args:
        conversation_id: ID of the conversation to analyze
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.messages.all().order_by('timestamp')
        
        if not messages.exists():
            return f"Conversation {conversation_id} has no messages"
        
        # Prepare messages for analyzer
        messages_data = [
            {
                'sender': msg.sender,
                'text': msg.text,
                'timestamp': msg.timestamp
            }
            for msg in messages
        ]
        
        # Run analysis
        analyzer = ConversationAnalyzer()
        analysis_results = analyzer.analyze(messages_data)
        
        # Create or update analysis record
        analysis, created = ConversationAnalysis.objects.update_or_create(
            conversation=conversation,
            defaults=analysis_results
        )
        
        action = "created" if created else "updated"
        return f"Analysis {action} for conversation {conversation_id}"
    
    except Conversation.DoesNotExist:
        return f"Conversation {conversation_id} not found"
    except Exception as e:
        return f"Error analyzing conversation {conversation_id}: {str(e)}"


@shared_task
def analyze_unanalyzed_conversations():
    """
    Celery Beat task to analyze all conversations without analysis.
    Runs once daily.
    """
    # Find conversations without analysis
    unanalyzed = Conversation.objects.filter(
        Q(analysis__isnull=True)
    ).values_list('id', flat=True)
    
    count = 0
    for conversation_id in unanalyzed:
        analyze_conversation_task.delay(conversation_id)
        count += 1
    
    return f"Queued {count} conversations for analysis"