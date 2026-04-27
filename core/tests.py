from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch
import json

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.models import AuditEvent, CatalogOrder


class BillingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.login(username='testuser', password='password')

    @patch('core.services.billing_service.stripe.checkout.Session.create')
    @patch.dict('os.environ', {'STRIPE_PRICE_ID': 'price_test', 'DOMAIN': 'http://testserver'})
    def test_create_checkout_session(self, mock_session_create):
        mock_session_create.return_value = MagicMock(url='https://checkout.stripe.com/test')

        response = self.client.get(reverse('subscribe'))

        self.assertRedirects(response, 'https://checkout.stripe.com/test', status_code=302, target_status_code=404, fetch_redirect_response=False)
        mock_session_create.assert_called_once()

    @patch('core.views.create_checkout_for_order')
    def test_catalog_purchase_creates_order_and_redirects(self, mock_create_checkout):
        mock_create_checkout.return_value = MagicMock(id='cs_pack_123', url='https://checkout.stripe.com/pack')

        response = self.client.post(reverse('academy_pack_purchase', kwargs={'slug': 'arduino-starter-lab'}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://checkout.stripe.com/pack')
        order = CatalogOrder.objects.get(user=self.user, pack_slug='arduino-starter-lab')
        self.assertEqual(order.status, CatalogOrder.STATUS_PENDING)
        self.assertEqual(order.stripe_session_id, 'cs_pack_123')
        self.assertTrue(AuditEvent.objects.filter(order=order, event_type='checkout_started').exists())

    def test_pdf_download_requires_purchase(self):
        response = self.client.get(reverse('academy_pdf_download', kwargs={'slug': 'arduino-starter-lab'}))
        self.assertEqual(response.status_code, 403)

    @patch('core.billing.stripe.Webhook.construct_event')
    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'whsec_test'})
    def test_stripe_webhook_success(self, mock_construct_event):
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'client_reference_id': str(self.user.id),
                    'customer': 'cus_test123',
                    'subscription': 'sub_test123',
                    'mode': 'subscription',
                }
            }
        }
        mock_construct_event.return_value = mock_event

        payload = json.dumps(mock_event)
        response = self.client.post(reverse('webhook'), data=payload, content_type='application/json', HTTP_STRIPE_SIGNATURE='test_sig')

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile.is_premium)
        self.assertEqual(self.user.profile.stripe_customer_id, 'cus_test123')

    @patch('core.billing.stripe.Webhook.construct_event')
    @patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'whsec_test'})
    def test_stripe_webhook_marks_catalog_order_paid(self, mock_construct_event):
        order = CatalogOrder.objects.create(
            user=self.user,
            pack_slug='arduino-starter-lab',
            pack_title='Laboratório Inicial de Arduino',
            amount_cents=499,
            customer_email=self.user.email,
        )
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_pack_done',
                    'payment_intent': 'pi_pack_done',
                    'mode': 'payment',
                    'metadata': {'catalog_order_id': str(order.id)},
                }
            }
        }
        mock_construct_event.return_value = mock_event

        response = self.client.post(reverse('webhook'), data='{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='test_sig')

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, CatalogOrder.STATUS_PAID)
        self.assertEqual(order.stripe_session_id, 'cs_pack_done')
        self.assertFalse(self.user.profile.is_premium)

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

    @patch('core.services.commerce_service.fetch_open_resource')
    @override_settings(DELIVERY_BUNDLE_DIR=Path.cwd() / 'test_generated_bundles')
    def test_paid_catalog_order_can_download_bundle(self, mock_fetch_resource):
        def fake_fetch(resource, base_dir):
            target = Path(base_dir) / resource['target_path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('codigo aberto', encoding='utf-8')
            return target

        mock_fetch_resource.side_effect = fake_fetch
        order = CatalogOrder.objects.create(
            user=self.user,
            pack_slug='arduino-starter-lab',
            pack_title='Laboratório Inicial de Arduino',
            amount_cents=499,
            customer_email=self.user.email,
            status=CatalogOrder.STATUS_PAID,
            source_snapshot={
                'open_resources': [
                    {
                        'target_path': 'codigo-aberto/arduino/blink/Blink.ino',
                        'url': 'https://raw.githubusercontent.com/arduino/arduino-examples/main/examples/01.Basics/Blink/Blink.ino',
                    }
                ]
            },
        )

        response = self.client.get(reverse('academy_bundle_download', kwargs={'order_id': order.id}))

        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, CatalogOrder.STATUS_FULFILLED)
        self.assertTrue(Path(order.delivery_bundle_path).exists())
        self.assertTrue(AuditEvent.objects.filter(order=order, event_type='bundle_downloaded').exists())
        response.close()

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

    def test_login_accepts_email(self):
        self.client.logout()
        response = self.client.post(
            reverse('login'),
            {'username': 'test@example.com', 'password': 'password'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class AITutorTests(TestCase):
    @patch('core.services.ai_service.genai.Client')
    def test_key_rotation(self, mock_client_class):
        from core.ai_tutor import get_response_stream

        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'key1',
            'GOOGLE_API_KEY_2': 'key2'
        }):
            mock_client_1 = MagicMock()
            mock_client_1.models.generate_content_stream.side_effect = Exception("429 RESOURCE_EXHAUSTED")

            mock_client_2 = MagicMock()
            mock_chunk = MagicMock()
            mock_chunk.text = "Success from Key 2"
            mock_client_2.models.generate_content_stream.return_value = [mock_chunk]

            def client_side_effect(api_key):
                if api_key == 'key1':
                    return mock_client_1
                if api_key == 'key2':
                    return mock_client_2
                return MagicMock()

            mock_client_class.side_effect = client_side_effect

            generator = get_response_stream("Hi")
            result = list(generator)

            self.assertEqual(result, ["Success from Key 2"])
            self.assertEqual(mock_client_class.call_count, 2)

    @patch('core.services.ai_service.genai.Client')
    def test_all_keys_exhausted(self, mock_client_class):
        from core.ai_tutor import get_response_stream

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

        with patch.dict('os.environ', {
            'GOOGLE_API_KEY': 'key1',
            'GROQ_API_KEY': 'groq_key'
        }):
            mock_genai_instance = mock_genai.return_value
            mock_genai_instance.models.generate_content_stream.side_effect = Exception("429 RESOURCE_EXHAUSTED")

            mock_groq_instance = mock_groq.return_value
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock(delta=MagicMock(content="Saved by Groq"))]
            mock_groq_instance.chat.completions.create.return_value = [mock_chunk]

            generator = get_response_stream("Help")
            result = list(generator)

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
