from django.urls import path
from . import views

urlpatterns = [
    path('balance/', views.get_balance, name='wallet_balance'),
    path('transactions/', views.get_transactions, name='wallet_transactions'),
    path('fund/', views.create_payment_intent, name='wallet_fund'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
