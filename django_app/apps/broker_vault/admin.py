from django.contrib import admin
from .models import BrokerAccount


@admin.register(BrokerAccount)
class BrokerAccountAdmin(admin.ModelAdmin):
    list_display = ('account_alias', 'broker_name', 'client_id', 'user', 'is_active', 'token_expiry', 'is_token_valid')
    list_filter = ('broker_name', 'is_active')
    search_fields = ('account_alias', 'client_id', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def is_token_valid(self, obj):
        return obj.is_token_valid()
    is_token_valid.boolean = True
    is_token_valid.short_description = "Session Active"
