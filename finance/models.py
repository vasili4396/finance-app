from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь, за которым закреплен кошелек',
        on_delete=models.CASCADE,
    )
    balance = models.DecimalField(verbose_name='Баланс', max_digits=12, decimal_places=3, default=0)

    class Meta:
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return f'{self.user.username} ({self.balance})'


def magic_get_wallet(user):
    # Assume user always has at least 1 wallet. Use this in order to avoid explicit wallet creation
    user_wallets = Wallet.objects.filter(user=user)
    if not user_wallets.exists():
        Wallet.objects.create(user=user)
        return Wallet.objects.filter(user=user)

    return user_wallets


get_user_model().wallets = property(magic_get_wallet)


class Transaction(models.Model):
    class TransactionTypes(models.IntegerChoices):
        OUTCOME = 1, 'Списание'
        INCOME = 2, 'Начисление'

    wallet = models.ForeignKey(
        'Wallet',
        related_name='transactions',
        verbose_name='Кошелек, на котором прошла транзакция',
        null=False, on_delete=models.CASCADE,
    )
    transaction_type = models.SmallIntegerField(
        verbose_name='Тип транзакции', choices=TransactionTypes.choices,
    )
    amount = models.DecimalField(
        verbose_name='Сумма транзакции', max_digits=12, decimal_places=3, default=0,
    )
    created_at = models.DateTimeField(verbose_name='Дата создания', default=timezone.now)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        if self.transaction_type == self.TransactionTypes.OUTCOME:
            return f'{self.wallet.id} -> {self.amount}'
        return f'{self.wallet.id} <- {self.amount}'
