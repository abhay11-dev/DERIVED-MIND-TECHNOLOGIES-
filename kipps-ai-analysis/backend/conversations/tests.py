import pytest
from datetime import datetime, timedelta
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Conversation, Message, ConversationAnalysis
from .analysis import ConversationAnalyzer


class ConversationAnalyzerTest(TestCase):
    """Unit tests for the ConversationAnalyzer class"""
    
    def setUp(self):
        self.analyzer = ConversationAnalyzer()
    
    def test_clarity_score_calculation(self):
        """Test clarity score computation"""
        messages = [
            {
                'sender': 'agent',
                'text': 'Hello! How can I help you today?',
                'timestamp': datetime.now()
            }
        ]
        
        result = self.analyzer.analyze(messages + [{
            'sender': 'user',
            'text': 'I need help',
            'timestamp': datetime.now()
        }])
        
        self.assertGreater(result['clarity_score'], 0)
        self.assertLessEqual(result['clarity_score'], 100)
    
    def test_fallback_detection(self):
        """Test fallback phrase detection"""
        messages = [
            {
                'sender': 'agent',
                'text': "I'm sorry, I don't know the answer to that.",
                'timestamp': datetime.now()
            },
            {
                'sender': 'agent',
                'text': "I can't help with that request.",
                'timestamp': datetime.now()
            },
            {
                'sender': 'user',
                'text': "Please help me",
                'timestamp': datetime.now()
            }
        ]
        
        result = self.analyzer.analyze(messages)
        self.assertEqual(result['fallback_count'], 2)
    
    def test_sentiment_analysis(self):
        """Test sentiment detection"""
        positive_messages = [
            {
                'sender': 'user',
                'text': 'Thank you so much! This is great!',
                'timestamp': datetime.now()
            },
            {
                'sender': 'agent',
                'text': 'Happy to help!',
                'timestamp': datetime.now()
            }
        ]
        
        result = self.analyzer.analyze(positive_messages)
        self.assertEqual(result['sentiment'], 'positive')
    
    def test_resolution_detection(self):
        """Test resolution detection"""
        resolved_messages = [
            {
                'sender': 'user',
                'text': 'I have an issue',
                'timestamp': datetime.now()
            },
            {
                'sender': 'agent',
                'text': 'Issue resolved successfully!',
                'timestamp': datetime.now()
            }
        ]
        
        result = self.analyzer.analyze(resolved_messages)
        self.assertTrue(result['resolution'])
    
    def test_escalation_detection(self):
        """Test escalation need detection"""
        escalation_messages = [
            {
                'sender': 'user',
                'text': 'I want to speak to a human agent',
                'timestamp': datetime.now()
            },
            {
                'sender': 'agent',
                'text': 'Let me help you',
                'timestamp': datetime.now()
            }
        ]
        
        result = self.analyzer.analyze(escalation_messages)
        self.assertTrue(result['escalation_needed'])
    
    def test_empathy_score(self):
        """Test empathy score calculation"""
        empathetic_messages = [
            {
                'sender': 'agent',
                'text': 'I understand your frustration. I apologize for the inconvenience.',
                'timestamp': datetime.now()
            },
            {
                'sender': 'user',
                'text': 'Thanks',
                'timestamp': datetime.now()
            }
        ]
        
        result = self.analyzer.analyze(empathetic_messages)
        self.assertGreater(result['empathy_score'], 50)


class ConversationAPITest(APITestCase):
    """Integration tests for the Conversation API"""
    
    def test_create_conversation(self):
        """Test creating a conversation via API"""
        payload = {
            'title': 'Test Conversation',
            'messages': [
                {
                    'sender': 'user',
                    'text': 'Hello',
                    'timestamp': '2024-01-01T10:00:00Z'
                },
                {
                    'sender': 'agent',
                    'text': 'Hi! How can I help?',
                    'timestamp': '2024-01-01T10:00:05Z'
                }
            ]
        }
        
        response = self.client.post('/api/conversations/', payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 1)
        self.assertEqual(Message.objects.count(), 2)
    
    def test_list_conversations(self):
        """Test listing conversations"""
        # Create test conversation
        conversation = Conversation.objects.create(title='Test')
        Message.objects.create(
            conversation=conversation,
            sender='user',
            text='Hello',
            timestamp=datetime.now()
        )
        
        response = self.client.get('/api/conversations/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_analyze_conversation(self):
        """Test analyzing a conversation via API"""
        # Create test conversation
        conversation = Conversation.objects.create(title='Test')
        Message.objects.create(
            conversation=conversation,
            sender='user',
            text='I need help',
            timestamp=datetime.now()
        )
        Message.objects.create(
            conversation=conversation,
            sender='agent',
            text='I understand. Let me help you.',
            timestamp=datetime.now() + timedelta(seconds=5)
        )
        
        response = self.client.post(f'/api/conversations/{conversation.id}/analyze/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('overall_score', response.data)
        self.assertTrue(ConversationAnalysis.objects.filter(conversation=conversation).exists())
    
    def test_list_analyses(self):
        """Test listing analyses with filters"""
        # Create test data
        conversation = Conversation.objects.create(title='Test')
        Message.objects.create(
            conversation=conversation,
            sender='user',
            text='Help',
            timestamp=datetime.now()
        )
        Message.objects.create(
            conversation=conversation,
            sender='agent',
            text='Sure',
            timestamp=datetime.now()
        )
        
        ConversationAnalysis.objects.create(
            conversation=conversation,
            sentiment='positive',
            overall_score=85.0
        )
        
        response = self.client.get('/api/analysis/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test filtering by sentiment
        response = self.client.get('/api/analysis/?sentiment=positive')
        self.assertEqual(len(response.data['results']), 1)