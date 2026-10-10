from django.urls import path
from . import views

app_name = 'strategy_manager'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('strategy/<uuid:strategy_id>/legs/', views.strategy_legs_partial, name='strategy_legs'),
    path('trade/execute-all/', views.execute_trade_all_view, name='execute_trade_all'),
]
