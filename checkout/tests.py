from django.test import TestCase
from tenacity import RetryError
from unittest.mock import patch, MagicMock
from django.db import OperationalError
from .models import Order
from .webhooks import handle_payment_event


class HandlePaymentEventRetryTests(TestCase):
    @patch('checkout.views.Order.objects.get')
    def test_retry_logic_on_operational_error(self, mock_get_order):
        mock_order = MagicMock()

        mock_order.stripe_pid = 'pi_12345'
        mock_order.status = 'pending'
        # First call raises OperationalError, second call returns mock_order
        mock_get_order.side_effect = [OperationalError, mock_order]

        payment_intent = MagicMock(id='pi_12345')

        try:
            handle_payment_event(payment_intent, 'payment_intent.succeeded')
        except OperationalError:
            self.fail("handle_payment_event raised OperationalError even after retries")

        self.assertEqual(mock_get_order.call_count, 2)

    @patch('checkout.views.Order.objects.get')
    def test_retry_logic_on_does_not_exist(self, mock_get_order):
        mock_get_order.side_effect = Order.DoesNotExist

        payment_intent = MagicMock(id='pi_12345')

        # Call the function and assert it raises Order.DoesNotExist
        with self.assertRaises(Order.DoesNotExist):
            handle_payment_event(payment_intent, 'payment_intent.succeeded')

        self.assertEqual(mock_get_order.call_count, 1)

    @patch('checkout.views.Order.objects.get')
    def test_retry_logic_on_generic_exception(self, mock_get_order):
        mock_get_order.side_effect = Exception('Generic error')

        payment_intent = MagicMock(id='pi_12345')

        # Call the function and assert it raises Exception
        with self.assertRaises(Exception):
            handle_payment_event(payment_intent, 'payment_intent.succeeded')

        self.assertEqual(mock_get_order.call_count, 1)

    @patch('checkout.views.Order.objects.get')
    def test_retry_logic_on_payment_failed(self, mock_get_order):
        mock_order = MagicMock()
        mock_order.stripe_pid = 'pi_12345'
        mock_order.status = 'pending'
        # First two calls raise OperationalError, third call returns mock_order
        mock_get_order.side_effect = [OperationalError, OperationalError, mock_order]

        payment_intent = MagicMock(id='pi_12345')

        try:
            handle_payment_event(payment_intent, 'payment_intent.payment_failed')
        except OperationalError:
            self.fail("handle_payment_event raised OperationalError even after retries")

        # Assert get was called three times (two failures and one success)
        self.assertEqual(mock_get_order.call_count, 3)

    @patch('checkout.views.Order.objects.get')
    def test_retry_exceeds_max_attempts(self, mock_get_order):
        # Mock order get to always raise OperationalError
        mock_get_order.side_effect = OperationalError

        payment_intent = MagicMock(id='pi_12345')

        # Call the function and assert it raises RetryError after max retries
        with self.assertRaises(RetryError):
            handle_payment_event(payment_intent, 'payment_intent.succeeded')

        # Assert get was called three times (max attempts)
        self.assertEqual(mock_get_order.call_count, 3)
