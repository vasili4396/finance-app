from django.db.models import Sum, Case, When, F, DecimalField
from rest_framework import serializers

from finance.models import Wallet, Transaction
from finance.helpers import get_month_boundaries


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(source='get_transaction_type_display')

    class Meta:
        model = Transaction
        fields = ('transaction_type', 'amount', 'created_at')


class WalletSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField()
    incomes = serializers.SerializerMethodField()
    outcomes = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ('balance', 'transactions', 'incomes', 'outcomes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.month_boundaries = None
        self.date = self.context['date']

        incomes_condition = {'transactions__transaction_type': Transaction.TransactionTypes.INCOME}
        outcomes_condition = {'transactions__transaction_type': Transaction.TransactionTypes.OUTCOME}
        if self.date:
            self.month_boundaries = get_month_boundaries(self.date)
            incomes_condition.update({'transactions__created_at__range': self.month_boundaries})
            outcomes_condition.update({'transactions__created_at__range': self.month_boundaries})

        self.wallet_summaries = list(self.instance.annotate(
            incomes=Sum(
                Case(
                    When(then=F('transactions__amount'), **incomes_condition),
                    output_field=DecimalField(),
                    default=0,
                )
            ),
            outcomes=Sum(
                Case(
                    When(then=F('transactions__amount'), **outcomes_condition),
                    output_field=DecimalField(),
                    default=0,
                )
            ),
        ).values('id', 'incomes', 'outcomes'))

    def get_incomes(self, wallet):
        for summary in self.wallet_summaries:
            if summary['id'] == wallet.id:
                return summary['incomes']
        return 0

    def get_outcomes(self, wallet):
        for summary in self.wallet_summaries:
            if summary['id'] == wallet.id:
                return summary['outcomes']
        return 0

    def get_transactions(self, wallet):
        if self.month_boundaries:
            transactions_qs = wallet.transactions.filter(created_at__range=self.month_boundaries)
        else:
            transactions_qs = wallet.transactions.all()
        return TransactionSerializer(transactions_qs, many=True).data
