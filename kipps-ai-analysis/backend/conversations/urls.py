from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, AnalysisViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'analysis', AnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
]