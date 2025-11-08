"""
Conversation Analysis Module

This module implements rule-based heuristics and ML-lite approaches
for analyzing customer support conversations. The implementation is modular
to allow easy replacement with more sophisticated ML models.
"""

import re
from datetime import datetime
from typing import List, Dict, Tuple
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class ConversationAnalyzer:
    """
    Main analyzer class that computes various metrics for conversation quality.
    
    Metrics computed:
    - Clarity Score: How clear and understandable the messages are
    - Relevance Score: How relevant responses are to user queries
    - Accuracy Score: Confidence in provided information
    - Completeness Score: Whether all user concerns were addressed
    - Empathy Score: Level of empathetic language used
    - Fallback Count: Number of times agent couldn't help
    - Sentiment: Overall conversation sentiment
    - Resolution: Whether issue was resolved
    - Escalation Needed: Whether conversation should be escalated
    - Avg Response Time: Average agent response time in seconds
    """
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Fallback phrases indicating agent couldn't help
        self.fallback_phrases = [
            r"i don't know",
            r"can't help",
            r"unable to assist",
            r"sorry.*don't have",
            r"not sure",
            r"cannot provide",
            r"don't have that information",
            r"beyond my capabilities",
        ]
        
        # Resolution indicators
        self.resolution_phrases = [
            r"resolved",
            r"fixed",
            r"solved",
            r"shipped",
            r"completed",
            r"done",
            r"thank you.*help",
            r"problem.*solved",
            r"issue.*resolved",
            r"that works",
            r"perfect.*thanks",
        ]
        
        # Escalation keywords
        self.escalation_keywords = [
            r"speak.*human",
            r"talk.*agent",
            r"supervisor",
            r"manager",
            r"escalate",
            r"real person",
            r"human agent",
        ]
        
        # Empathy phrases
        self.empathy_phrases = [
            r"i understand",
            r"i apologize",
            r"i'm sorry",
            r"that must be",
            r"i can imagine",
            r"appreciate.*patience",
            r"thank you for",
            r"i hear you",
            r"understand.*frustration",
        ]
        
        # Question indicators
        self.question_pattern = r'\?'
        
        # Technical jargon that might hurt clarity
        self.jargon_terms = [
            r'API', r'SDK', r'latency', r'throughput', r'deprecated',
            r'refactor', r'endpoint', r'payload', r'middleware'
        ]
    
    def analyze(self, messages: List[Dict]) -> Dict:
        """
        Main analysis method that computes all metrics.
        
        Args:
            messages: List of message dicts with 'sender', 'text', 'timestamp'
        
        Returns:
            Dictionary with all computed metrics
        """
        agent_messages = [m for m in messages if m['sender'] == 'agent']
        user_messages = [m for m in messages if m['sender'] == 'user']
        
        if not agent_messages or not user_messages:
            return self._default_scores()
        
        # Compute individual metrics
        clarity_score = self._compute_clarity_score(agent_messages)
        relevance_score = self._compute_relevance_score(user_messages, agent_messages)
        accuracy_score = self._compute_accuracy_score(agent_messages)
        completeness_score = self._compute_completeness_score(user_messages, agent_messages)
        empathy_score = self._compute_empathy_score(agent_messages)
        fallback_count = self._count_fallbacks(agent_messages)
        sentiment = self._analyze_sentiment(messages)
        resolution = self._detect_resolution(messages)
        escalation_needed = self._detect_escalation_need(
            messages, sentiment, fallback_count
        )
        avg_response_time = self._compute_avg_response_time(messages)
        
        # Compute overall score (weighted average)
        overall_score = self._compute_overall_score(
            clarity_score, relevance_score, accuracy_score,
            completeness_score, empathy_score, resolution
        )
        
        return {
            'clarity_score': round(clarity_score, 2),
            'relevance_score': round(relevance_score, 2),
            'accuracy_score': round(accuracy_score, 2),
            'completeness_score': round(completeness_score, 2),
            'empathy_score': round(empathy_score, 2),
            'fallback_count': fallback_count,
            'sentiment': sentiment,
            'resolution': resolution,
            'escalation_needed': escalation_needed,
            'avg_response_time_seconds': round(avg_response_time, 2),
            'overall_score': round(overall_score, 2),
        }
    
    def _compute_clarity_score(self, agent_messages: List[Dict]) -> float:
        """
        Compute clarity score based on:
        - Average sentence length (shorter is clearer)
        - Use of jargon (less is clearer)
        - Readability (using TextBlob)
        """
        if not agent_messages:
            return 0.0
        
        total_words = 0
        total_sentences = 0
        jargon_count = 0
        
        for msg in agent_messages:
            text = msg['text']
            blob = TextBlob(text)
            
            # Count sentences and words
            sentences = blob.sentences
            total_sentences += len(sentences)
            total_words += len(blob.words)
            
            # Count jargon
            for term in self.jargon_terms:
                jargon_count += len(re.findall(term, text, re.IGNORECASE))
        
        # Average words per sentence (ideal: 15-20 words)
        avg_words_per_sentence = total_words / max(total_sentences, 1)
        sentence_score = 100 - abs(avg_words_per_sentence - 17.5) * 2
        sentence_score = max(0, min(100, sentence_score))
        
        # Jargon penalty (each jargon term reduces score)
        jargon_score = max(0, 100 - (jargon_count * 10))
        
        # Combined clarity score
        clarity_score = (sentence_score * 0.7) + (jargon_score * 0.3)
        
        return clarity_score
    
    def _compute_relevance_score(self, user_messages: List[Dict],
                                  agent_messages: List[Dict]) -> float:
        """
        Compute relevance by checking if agent responses address user questions
        and maintain topic continuity.
        """
        if not user_messages or not agent_messages:
            return 0.0
        
        relevance_scores = []
        
        for i, user_msg in enumerate(user_messages):
            # Find the next agent message
            agent_response = None
            for agent_msg in agent_messages:
                if agent_msg['timestamp'] > user_msg['timestamp']:
                    agent_response = agent_msg
                    break
            
            if not agent_response:
                continue
            
            # Simple keyword overlap as relevance proxy
            user_words = set(user_msg['text'].lower().split())
            agent_words = set(agent_response['text'].lower().split())
            
            # Remove common stop words
            stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'i', 'you', 'to', 'for'}
            user_words -= stop_words
            agent_words -= stop_words
            
            if user_words:
                overlap = len(user_words & agent_words) / len(user_words)
                relevance_scores.append(overlap * 100)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 50.0
    
    def _compute_accuracy_score(self, agent_messages: List[Dict]) -> float:
        """
        Compute accuracy score based on:
        - Presence of uncertain language
        - Confidence indicators
        - Hedge words
        """
        if not agent_messages:
            return 0.0
        
        uncertain_phrases = [
            r'maybe', r'perhaps', r'might be', r'could be', r'possibly',
            r'not sure', r'i think', r'probably'
        ]
        
        confident_phrases = [
            r'definitely', r'certainly', r'absolutely', r'confirmed',
            r'verified', r'guaranteed'
        ]
        
        uncertain_count = 0
        confident_count = 0
        
        for msg in agent_messages:
            text = msg['text'].lower()
            
            for phrase in uncertain_phrases:
                uncertain_count += len(re.findall(phrase, text))
            
            for phrase in confident_phrases:
                confident_count += len(re.findall(phrase, text))
        
        # Start with base score and adjust
        base_score = 75.0
        accuracy_score = base_score + (confident_count * 5) - (uncertain_count * 10)
        
        return max(0, min(100, accuracy_score))
    
    def _compute_completeness_score(self, user_messages: List[Dict],
                                     agent_messages: List[Dict]) -> float:
        """
        Compute completeness by checking if all user questions were addressed.
        """
        if not user_messages:
            return 100.0
        
        user_questions = sum(1 for msg in user_messages 
                           if re.search(self.question_pattern, msg['text']))
        
        if user_questions == 0:
            return 80.0  # No questions, assume mostly complete
        
        # Check if agent provided multiple responses (likely addressing questions)
        response_ratio = len(agent_messages) / max(user_questions, 1)
        
        # Score based on response ratio
        if response_ratio >= 1.0:
            completeness_score = min(100, 70 + (response_ratio * 10))
        else:
            completeness_score = response_ratio * 70
        
        return completeness_score
    
    def _compute_empathy_score(self, agent_messages: List[Dict]) -> float:
        """
        Compute empathy score based on presence of empathetic language.
        """
        if not agent_messages:
            return 0.0
        
        empathy_count = 0
        
        for msg in agent_messages:
            text = msg['text'].lower()
            
            for phrase in self.empathy_phrases:
                empathy_count += len(re.findall(phrase, text))
        
        # Score based on empathy phrases per message
        empathy_per_message = empathy_count / len(agent_messages)
        empathy_score = min(100, empathy_per_message * 50 + 30)
        
        return empathy_score
    
    def _count_fallbacks(self, agent_messages: List[Dict]) -> int:
        """Count the number of fallback responses."""
        fallback_count = 0
        
        for msg in agent_messages:
            text = msg['text'].lower()
            
            for phrase in self.fallback_phrases:
                if re.search(phrase, text):
                    fallback_count += 1
                    break  # Count each message only once
        
        return fallback_count
    
    def _analyze_sentiment(self, messages: List[Dict]) -> str:
        """
        Analyze overall conversation sentiment using VADER.
        """
        if not messages:
            return 'neutral'
        
        # Combine all messages
        full_text = ' '.join(msg['text'] for msg in messages)
        
        # Use VADER for sentiment analysis
        scores = self.vader_analyzer.polarity_scores(full_text)
        compound = scores['compound']
        
        if compound >= 0.05:
            return 'positive'
        elif compound <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_resolution(self, messages: List[Dict]) -> bool:
        """
        Detect if the conversation was resolved based on resolution phrases.
        """
        # Check last few messages for resolution indicators
        recent_messages = messages[-3:] if len(messages) >= 3 else messages
        
        for msg in recent_messages:
            text = msg['text'].lower()
            
            for phrase in self.resolution_phrases:
                if re.search(phrase, text):
                    return True
        
        return False
    
    def _detect_escalation_need(self, messages: List[Dict],
                                sentiment: str, fallback_count: int) -> bool:
        """
        Detect if conversation needs escalation based on:
        - Negative sentiment + fallbacks
        - User explicitly asking for human agent
        """
        # Check for explicit escalation requests
        for msg in messages:
            if msg['sender'] == 'user':
                text = msg['text'].lower()
                
                for keyword in self.escalation_keywords:
                    if re.search(keyword, text):
                        return True
        
        # Check for negative sentiment with fallbacks
        if sentiment == 'negative' and fallback_count > 0:
            return True
        
        # Check for excessive fallbacks
        if fallback_count >= 3:
            return True
        
        return False
    
    def _compute_avg_response_time(self, messages: List[Dict]) -> float:
        """
        Compute average agent response time in seconds.
        """
        response_times = []
        
        for i in range(len(messages) - 1):
            if messages[i]['sender'] == 'user' and messages[i + 1]['sender'] == 'agent':
                try:
                    user_time = self._parse_timestamp(messages[i]['timestamp'])
                    agent_time = self._parse_timestamp(messages[i + 1]['timestamp'])
                    
                    if user_time and agent_time:
                        response_time = (agent_time - user_time).total_seconds()
                        if response_time > 0:  # Ignore negative times (data issues)
                            response_times.append(response_time)
                except:
                    continue
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse timestamp string or datetime object."""
        if isinstance(timestamp, datetime):
            return timestamp
        
        # Try different formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except:
                continue
        
        return None
    
    def _compute_overall_score(self, clarity: float, relevance: float,
                               accuracy: float, completeness: float,
                               empathy: float, resolution: bool) -> float:
        """
        Compute weighted overall score.
        
        Weights:
        - Clarity: 20%
        - Relevance: 25%
        - Accuracy: 20%
        - Completeness: 20%
        - Empathy: 10%
        - Resolution: 5% (bonus)
        """
        base_score = (
            clarity * 0.20 +
            relevance * 0.25 +
            accuracy * 0.20 +
            completeness * 0.20 +
            empathy * 0.10
        )
        
        # Add resolution bonus
        if resolution:
            base_score += 5.0
        
        return min(100, base_score)
    
    def _default_scores(self) -> Dict:
        """Return default scores when analysis cannot be performed."""
        return {
            'clarity_score': 0.0,
            'relevance_score': 0.0,
            'accuracy_score': 0.0,
            'completeness_score': 0.0,
            'empathy_score': 0.0,
            'fallback_count': 0,
            'sentiment': 'neutral',
            'resolution': False,
            'escalation_needed': False,
            'avg_response_time_seconds': 0.0,
            'overall_score': 0.0,
        }