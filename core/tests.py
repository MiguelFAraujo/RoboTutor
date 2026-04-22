from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command
from unittest.mock import patch, MagicMock
from django.contrib.sites.models import Site
from pathlib import Path
from tempfile import TemporaryDirectory
import json

class BillingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.login(username='testuser', password='password')

    @patch('core.services.billing_service.stripe.checkout.Session.create')
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

    @patch('core.billing.stripe.Webhook.construct_event')
    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'whsec_test'})
    def test_stripe_webhook_subscription_deleted(self, mock_construct_event):
        self.user.profile.is_premium = True
        self.user.profile.stripe_subscription_id = 'sub_test123'
        self.user.profile.save()

        mock_event = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_test123'
                }
            }
        }
        mock_construct_event.return_value = mock_event

        response = self.client.post(reverse('webhook'), data='{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='test_sig')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile.is_premium)

    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'whsec_test'})
    def test_stripe_webhook_missing_signature(self):
        response = self.client.post(reverse('webhook'), data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/index.html')

    def test_chat_api_invalid_json(self):
        response = self.client.post(
            reverse('chat_api'),
            data='{"message": ',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_landing_and_academy_pages_render(self):
        self.assertEqual(self.client.get(reverse('landing')).status_code, 200)
        self.assertEqual(self.client.get(reverse('academy')).status_code, 200)
        self.assertEqual(self.client.get(reverse('academy_pack', kwargs={'slug': 'arduino-starter-lab'})).status_code, 200)


class AITutorTests(TestCase):
    @patch('core.services.ai_service.genai.Client')
    def test_key_rotation(self, mock_client_class):
        from core.ai_tutor import get_response_stream, load_api_keys
        
        # Setup Environment with 2 keys
        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'key1', 
            'GOOGLE_API_KEY_2': 'key2'
        }):
            # Reload keys to pick up mocks
            # Setup Mock Clients
            # Client 1 (Key 1) -> Raises 429
            mock_client_1 = MagicMock()
            mock_client_1.models.generate_content_stream.side_effect = Exception("429 RESOURCE_EXHAUSTED")
            
            # Client 2 (Key 2) -> Success
            mock_client_2 = MagicMock()
            mock_chunk = MagicMock()
            mock_chunk.text = "Success from Key 2"
            mock_client_2.models.generate_content_stream.return_value = [mock_chunk]
            
            # side_effect for constructor to return different clients based on api_key
            def client_side_effect(api_key):
                if api_key == 'key1': return mock_client_1
                if api_key == 'key2': return mock_client_2
                return MagicMock()
                
            mock_client_class.side_effect = client_side_effect

            # Execute
            generator = get_response_stream("Hi")
            result = list(generator)

            # Verify
            self.assertEqual(result, ["Success from Key 2"])
            
            # Verify both clients were created
            self.assertEqual(mock_client_class.call_count, 2)

    @patch('core.services.ai_service.genai.Client')
    def test_all_keys_exhausted(self, mock_client_class):
        from core.ai_tutor import get_response_stream
        
        # Ensure ONLY GOOGLE_API_KEY is present, NO GROQ KEY
        with patch.dict('os.environ', {'GOOGLE_API_KEY': 'key1'}, clear=True):
            mock_client = mock_client_class.return_value
            mock_client.models.generate_content_stream.side_effect = Exception("429 RESOURCE_EXHAUSTED")
            
            generator = get_response_stream("Hi")
            result = list(generator)
            
            self.assertTrue("Sistema Sobrecarregado" in result[0])

    @patch('core.services.ai_service.Groq')
    @patch('core.services.ai_service.genai.Client')
    def test_groq_fallback(self, mock_genai, mock_groq):
        from core.ai_tutor import get_response_stream
        
        # Setup: 1 Gemini Key (that fails) + 1 Groq Key
        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'key1',
            'GROQ_API_KEY': 'groq_key'
        }):
            # Gemini Fails with 429
            mock_genai_instance = mock_genai.return_value
            mock_genai_instance.models.generate_content_stream.side_effect = Exception("429 RESOURCE_EXHAUSTED")
            
            # Groq Succeeds
            mock_groq_instance = mock_groq.return_value
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock(delta=MagicMock(content="Saved by Groq"))]
            mock_groq_instance.chat.completions.create.return_value = [mock_chunk]
            
            # Execute
            generator = get_response_stream("Help")
            result = list(generator)
            
            # Verify
            self.assertEqual(result[0], "Saved by Groq")
            mock_groq.assert_called_with(api_key='groq_key')

    def test_load_api_keys_reads_numbered_env_vars(self):
        from core.ai_tutor import load_api_keys

        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'key1',
            'GOOGLE_API_KEY_2': 'key2',
            'GOOGLE_API_KEY_3': 'key3',
        }, clear=True):
            self.assertEqual(load_api_keys(), ['key1', 'key2', 'key3'])


class PdfGenerationTests(TestCase):
    def test_generate_single_pack_pdf(self):
        with TemporaryDirectory() as temp_dir:
            call_command('generate_product_pdfs', '--slug', 'arduino-starter-lab', '--output-dir', temp_dir)
            generated = Path(temp_dir) / 'arduino-starter-lab.pdf'
            self.assertTrue(generated.exists())
            self.assertGreater(generated.stat().st_size, 0)


class SocialAdapterTests(TestCase):
    def test_google_adapter_handles_duplicate_social_apps(self):
        from allauth.socialaccount.models import SocialApp
        from core.adapters import CustomSocialAccountAdapter

        site = Site.objects.get(id=1)
        app1 = SocialApp.objects.create(
            provider='google',
            name='Google A',
            client_id='client-a',
            secret='secret-a',
        )
        app1.sites.add(site)
        app2 = SocialApp.objects.create(
            provider='google',
            name='Google B',
            client_id='client-b',
            secret='secret-b',
        )
        app2.sites.add(site)

        request = self.client.get('/').wsgi_request
        app = CustomSocialAccountAdapter().get_app(request, 'google')

        self.assertEqual(app.id, app1.id)
