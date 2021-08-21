from django.contrib import admin

from finance.models import Wallet
from users.models import User


class WalletInline(admin.TabularInline):
    model = Wallet
    verbose_name = 'Кошелек'
    verbose_name_plural = 'Кошельки'
    extra = 0
    readonly_fields = ('balance',)
    classes = ('collapse',)
    can_delete = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name', 'is_superuser',
    )
    fields = ('username', 'first_name', 'last_name', 'email')
    readonly_fields = ('is_superuser',)
    search_fields = ('username', 'first_name', 'last_name', 'email',)
    inlines = (WalletInline,)
