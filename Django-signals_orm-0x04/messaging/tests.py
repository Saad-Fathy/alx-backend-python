# Add to existing tests
from django.core.cache import cache

def test_view_cache(self):
    message = Message.objects.create(sender=self.sender, receiver=self.receiver, content="Test message")
    response = self.client.get(f'/threaded_conversation/{message.id}/')
    cached_response = self.client.get(f'/threaded_conversation/{message.id}/')
    self.assertEqual(response.content, cached_response.content)  # Should hit cache
    cache.clear()  # Clean up cache after test