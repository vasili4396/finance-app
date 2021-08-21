import random
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from finance.models import Transaction

ISO_8601 = '%Y-%m-%d'


class AccoutingApiTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='big_boss', email='boss@test.com')
        self.client = APIClient()

        user_wallet = self.user.wallets.first()

        self.now = timezone.now()
        self.two_months_ago = self.now - relativedelta(months=2)

        # this month transactions
        for i in range(8):
            Transaction.objects.create(
                wallet=user_wallet,
                transaction_type=i % 2 + 1,
                amount=Decimal(random.randint(0, 1_000_000_000) / 1000),
                created_at=self.now,
            )

        Transaction.objects.create(
            wallet=user_wallet,
            transaction_type=Transaction.TransactionTypes.INCOME,
            amount=Decimal(203203),
            created_at=self.two_months_ago,
        )
        Transaction.objects.create(
            wallet=user_wallet,
            transaction_type=Transaction.TransactionTypes.OUTCOME,
            amount=Decimal(10101),
            created_at=self.two_months_ago,
        )

    @property
    def api_url(self):
        return reverse('users:accounting-detail', kwargs={'pk': self.user.id})

    @staticmethod
    def dttm_to_dt(_datetime):
        return _datetime.date().strftime(ISO_8601)

    def test_api_status(self):
        res = self.client.get(self.api_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(self.api_url, data={'date': self.dttm_to_dt(self.now)})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        invalid_url = reverse('users:accounting-detail', kwargs={'pk': 1010})
        res = self.client.get(invalid_url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        invalid_params = {'date': 'qwe'}
        res = self.client.get(self.api_url, data=invalid_params)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('Invalid date' in str(res.data))

    def test_api_response(self):
        res = self.client.get(self.api_url)
        self.assertEqual(res.data.get('username'), self.user.username)

        user_wallet = res.data.get('wallets')[0]
        self.assertEqual(
            len(user_wallet.get('transactions')),
            Transaction.objects.count(),
        )

        res = self.client.get(self.api_url, data={'date': self.dttm_to_dt(self.now)})
        user_wallet = res.data.get('wallets')[0]
        this_month_transactions = Transaction.objects.filter(created_at=self.now)
        incomes = 0
        outcomes = 0
        self.assertEqual(
            len(user_wallet.get('transactions')),
            this_month_transactions.count(),
        )
        for transaction in this_month_transactions:
            if transaction.transaction_type == Transaction.TransactionTypes.OUTCOME:
                outcomes += transaction.amount
            elif transaction.transaction_type == Transaction.TransactionTypes.INCOME:
                incomes += transaction.amount

        self.assertEqual(user_wallet.get('incomes'), incomes)
        self.assertEqual(user_wallet.get('outcomes'), outcomes)

        res = self.client.get(self.api_url, data={'date': self.dttm_to_dt(self.two_months_ago)})
        user_wallet = res.data.get('wallets')[0]
        self.assertEqual(
            len(user_wallet.get('transactions')),
            Transaction.objects.filter(created_at=self.two_months_ago).count(),
        )
