from django.contrib.auth import get_user_model
from rest_framework import serializers

from finance.serializers import WalletSerializer


class AccountingSerializer(serializers.ModelSerializer):
    wallets = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'wallets')

    def get_wallets(self, user):
        return WalletSerializer(
            user.wallets.prefetch_related('transactions'),
            many=True,
            context=self.context,
        ).data
