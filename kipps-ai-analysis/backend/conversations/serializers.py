from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp']
        read_only_fields = ['id']


class ConversationAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for ConversationAnalysis model"""
    
    class Meta:
        model = ConversationAnalysis
        fields = [
            'id', 'conversation', 'clarity_score', 'relevance_score',
            'accuracy_score', 'completeness_score', 'empathy_score',
            'fallback_count', 'sentiment', 'resolution', 'escalation_needed',
            'avg_response_time_seconds', 'overall_score', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    messages = MessageSerializer(many=True, read_only=True)
    analysis = ConversationAnalysisSerializer(read_only=True)
    has_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'messages', 'analysis', 'has_analysis']
        read_only_fields = ['id', 'created_at']
    
    def get_has_analysis(self, obj):
        """Check if conversation has been analyzed"""
        return hasattr(obj, 'analysis')


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer for creating conversations with messages from JSON"""
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    messages = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_messages(self, value):
        """Validate message structure"""
        for msg in value:
            if 'sender' not in msg or 'text' not in msg or 'timestamp' not in msg:
                raise serializers.ValidationError(
                    "Each message must have 'sender', 'text', and 'timestamp' fields"
                )
            if msg['sender'] not in ['user', 'agent']:
                raise serializers.ValidationError(
                    "Sender must be either 'user' or 'agent'"
                )
        return value
    
    def create(self, validated_data):
        """Create conversation and its messages"""
        messages_data = validated_data.pop('messages')
        title = validated_data.get('title', '')
        
        # Create conversation
        conversation = Conversation.objects.create(title=title)
        
        # Create messages
        for msg_data in messages_data:
            Message.objects.create(
                conversation=conversation,
                sender=msg_data['sender'],
                text=msg_data['text'],
                timestamp=msg_data['timestamp']
            )
        
        return conversation