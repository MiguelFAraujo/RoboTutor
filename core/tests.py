from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch, MagicMock
from core.models import Profile
import json

class BillingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.login(username='testuser', password='password')

    @patch('core.billing.stripe.checkout.Session.create')
    @patch.dict('os.environ', {'STRIPE_PRICE_ID': 'price_test', 'DOMAIN': 'http://testserver'})
    def test_create_checkout_session(self, mock_session_create):
        # Setup mock
        mock_session_create.return_value = MagicMock(url='https://checkout.stripe.com/test')

        response = self.client.get(reverse('subscribe'))
        
        # Verify redirect
        self.assertRedirects(response, 'https://checkout.stripe.com/test', status_code=302, target_status_code=404, fetch_redirect_response=False)
        mock_session_create.assert_called_once()

    @patch('core.billing.stripe.Webhook.construct_event')
    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'whsec_test'})
    def test_stripe_webhook_success(self, mock_construct_event):
        # Mock Stripe event
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': str(self.user.id),
                    'customer': 'cus_test123',
                    'subscription': 'sub_test123'
                }
            }
        }
        mock_construct_event.return_value = mock_event

        payload = json.dumps(mock_event)
        response = self.client.post(reverse('webhook'), data=payload, content_type='application/json', HTTP_STRIPE_SIGNATURE='test_sig')

        self.assertEqual(response.status_code, 200)
        
        # Verify user upgraded
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile.is_premium)
        self.assertEqual(self.user.profile.stripe_customer_id, 'cus_test123')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')


class AITutorTests(TestCase):
    @patch('core.ai_tutor.genai.Client')
    @patch.dict('os.environ', {'GOOGLE_API_KEY': 'fake_key'})
    def test_get_response_stream(self, mock_client_class):
        from core.ai_tutor import get_response_stream
        
        # Mock Client instance
        mock_client = mock_client_class.return_value
        
        # Mock response stream
        mock_chunk = MagicMock()
        mock_chunk.text = "Hello world"
        mock_client.models.generate_content_stream.return_value = [mock_chunk]

        # Call generator
        generator = get_response_stream("Hi")
        result = list(generator)

        self.assertEqual(result, ["Hello world"])
        mock_client.models.generate_content_stream.assert_called()
