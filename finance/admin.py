from django.contrib import admin

from finance.models import Wallet, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('amount', 'transaction_type')
    classes = ('collapse',)
    can_delete = False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance',)
    list_select_related = ('user',)
    raw_id_fields = ('user',)
    fields = ('user', 'balance')
    readonly_fields = ('balance',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name',)
    inlines = (TransactionInline,)
