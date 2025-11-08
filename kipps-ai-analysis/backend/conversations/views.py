from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, ConversationAnalysis
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    ConversationAnalysisSerializer,
    MessageSerializer
)
from .analysis import ConversationAnalyzer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    Endpoints:
    - GET /api/conversations/ - List all conversations
    - POST /api/conversations/ - Create a new conversation with messages
    - GET /api/conversations/{id}/ - Get conversation details
    - POST /api/conversations/{id}/analyze/ - Analyze specific conversation
    """
    queryset = Conversation.objects.all().prefetch_related('messages')
    serializer_class = ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a conversation with messages from JSON payload."""
        serializer = ConversationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the created conversation with messages
        output_serializer = ConversationSerializer(conversation)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Trigger analysis for a specific conversation.
        
        POST /api/conversations/{id}/analyze/
        """
        conversation = self.get_object()
        
        # Get all messages for this conversation
        messages = conversation.messages.all().order_by('timestamp')
        
        if not messages.exists():
            return Response(
                {'error': 'Cannot analyze conversation with no messages'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        
        serializer = ConversationAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing conversation analyses.
    
    Endpoints:
    - GET /api/analysis/ - List all analyses with filters
    - GET /api/analysis/{id}/ - Get specific analysis
    """
    queryset = ConversationAnalysis.objects.all().select_related('conversation')
    serializer_class = ConversationAnalysisSerializer
    
    def get_queryset(self):
        """Filter by sentiment, date, or score if provided."""
        queryset = super().get_queryset()
        
        # Filter by sentiment
        sentiment = self.request.query_params.get('sentiment', None)
        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Filter by minimum overall score
        min_score = self.request.query_params.get('min_score', None)
        if min_score:
            try:
                queryset = queryset.filter(overall_score__gte=float(min_score))
            except ValueError:
                pass
        
        return queryset