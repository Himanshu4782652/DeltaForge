from django.contrib import admin
from .models import StrategyConfig, TradeExecutionLog


@admin.register(StrategyConfig)
class StrategyConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_index', 'category', 'square_off_time', 'is_active', 'created_by')
    list_filter = ('target_index', 'category', 'is_active')
    search_fields = ('name', 'description')


@admin.register(TradeExecutionLog)
class TradeExecutionLogAdmin(admin.ModelAdmin):
    list_display = ('executed_at', 'broker_account', 'strategy', 'status', 'order_id')
    list_filter = ('status', 'broker_account__broker_name')
    search_fields = ('order_id', 'broker_account__client_id', 'strategy__name')
    readonly_fields = ('id', 'executed_at', 'response_payload')
