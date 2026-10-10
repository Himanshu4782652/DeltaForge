"""
DeltaForge URL Configuration
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_app.apps.strategy_manager.urls')),
]

admin.site.site_header = "DeltaForge Quant Administration"
admin.site.site_title = "DeltaForge Portal"
admin.site.index_title = "Enterprise Options Trading & Broker Vault"
