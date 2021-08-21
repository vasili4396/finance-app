import os
import random
from decimal import Decimal
from faker import Faker
from faker.providers import profile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from finance.models import Wallet, Transaction

BATCH_CREATE_SIZE = 1000


class ConsoleColor:
    OK = '\033[92m'
    END = '\033[0m'

    @staticmethod
    def console_ok():
        return f'{ConsoleColor.OK}OK{ConsoleColor.END}'


class Command(BaseCommand):
    help = "Fills database with fake records"

    def handle(self, *args, **options):
        User = get_user_model()

        # delete all existing records
        User.objects.exclude(username=os.environ['DJANGO_SUPERUSER_USERNAME']).delete()
        Transaction.objects.all().delete()
        Wallet.objects.all().delete()

        fake = Faker('ru_RU')
        fake.add_provider(profile)

        total_users_created = 0
        batched_users = []

        print('Creating user records...', end=' ', flush=True)

        for batch_idx in range(20000):
            profile_dict = fake.simple_profile(('birthdate', 'sex'),)
            generated_user = User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                birthday=profile_dict['birthdate'],
                sex=User.SexTypes.MALE if profile_dict['sex'] == 'M' else User.SexTypes.FEMALE,
            )
            batched_users.append(generated_user)

            if len(batched_users) == BATCH_CREATE_SIZE:
                total_users_created += len(User.objects.bulk_create(batched_users))
                batched_users = []

        # досоздать остатки из списка, если не прошли порог в BATCH_CREATE_SIZE
        if batched_users:
            total_users_created += len(User.objects.bulk_create(batched_users))

        print(f'{total_users_created} records: {ConsoleColor.console_ok()}')

        wallets = []
        for uid in User.objects.values_list('id', flat=True):
            wallets.append(
                Wallet(user_id=uid),
            )
        Wallet.objects.bulk_create(wallets)

        wallet_transactions = []
        total_transactions_created = 0

        print('Creating user transactions...', end=' ', flush=True)

        wallets = Wallet.objects.all()
        for wallet in wallets:
            transactions_per_wallet = 0
            wallet_transactions_summary = Decimal(0)

            while transactions_per_wallet < 5:
                # если с рандомом не повезло, дополняем как минимум до 5 транзакций
                for transaction_idx in range(random.randint(5, 10)):
                    transaction_type = random.choice(Transaction.TransactionTypes.values)
                    transaction_amount = Decimal(random.randint(0, 1_000_000_000) / 1000)

                    if transaction_type == Transaction.TransactionTypes.INCOME:
                        wallet_transactions_summary += transaction_amount
                    elif wallet_transactions_summary < transaction_amount:
                        # не даем уйти в минус
                        continue
                    else:
                        wallet_transactions_summary -= transaction_amount

                    wallet_transactions.append(
                        Transaction(
                            wallet_id=wallet.id,
                            transaction_type=transaction_type,
                            amount=transaction_amount,
                            created_at=fake.date_time_between(
                                start_date='-1y',
                                end_date='now',
                                tzinfo=timezone.get_current_timezone(),
                            ),
                        )
                    )
                    transactions_per_wallet += 1

            if len(wallet_transactions) > BATCH_CREATE_SIZE:
                total_transactions_created += len(Transaction.objects.bulk_create(wallet_transactions))
                wallet_transactions = []

            wallet.balance = wallet_transactions_summary

        if wallet_transactions:
            total_transactions_created += len(Transaction.objects.bulk_create(wallet_transactions))

        Wallet.objects.bulk_update(wallets, ['balance'])

        print(f'{total_transactions_created} records: {ConsoleColor.console_ok()}')
