from decimal import Decimal
from django.db import models, transaction
from django.conf import settings


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s wallet - ${self.balance}"

    def deposit(self, amount):
        """Add funds to wallet."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        with transaction.atomic():
            self.balance += Decimal(str(amount))
            self.save()
            Transaction.objects.create(
                wallet=self,
                amount=Decimal(str(amount)),
                transaction_type='deposit',
                description='Stripe deposit'
            )
        return self.balance

    def withdraw(self, amount, description='Post creation fee'):
        """Withdraw funds from wallet."""
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        with transaction.atomic():
            if self.balance < amount:
                raise ValueError("Insufficient funds")
            self.balance -= amount
            self.save()
            Transaction.objects.create(
                wallet=self,
                amount=amount,
                transaction_type='withdrawal',
                description=description
            )
        return self.balance

    def has_sufficient_funds(self, amount):
        """Check if wallet has enough funds."""
        return self.balance >= Decimal(str(amount))


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - ${self.amount} - {self.created_at}"
