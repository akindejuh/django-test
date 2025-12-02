import json
import stripe
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Wallet, Transaction

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_wallet(user):
    """Get or create wallet for a user."""
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


@require_http_methods(["GET"])
def get_balance(request):
    """Get user's wallet balance."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    wallet = get_or_create_wallet(request.user)
    return JsonResponse({
        'balance': str(wallet.balance),
        'currency': 'USD'
    })


@require_http_methods(["GET"])
def get_transactions(request):
    """Get user's transaction history."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    wallet = get_or_create_wallet(request.user)
    transactions = wallet.transactions.all()[:50]

    return JsonResponse({
        'transactions': [
            {
                'id': t.id,
                'amount': str(t.amount),
                'type': t.transaction_type,
                'description': t.description,
                'created_at': t.created_at.isoformat()
            }
            for t in transactions
        ]
    })


@csrf_exempt
@require_http_methods(["POST"])
def create_payment_intent(request):
    """Create a Stripe PaymentIntent for funding the wallet."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        amount = data.get('amount')

        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)

        amount = Decimal(str(amount))
        if amount < Decimal('1.00'):
            return JsonResponse({'error': 'Minimum deposit is $1.00'}, status=400)

        # Convert to cents for Stripe
        amount_cents = int(amount * 100)

        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'user_id': request.user.id,
                'user_email': request.user.email
            }
        )

        return JsonResponse({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except stripe.error.StripeError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        user_id = payment_intent['metadata'].get('user_id')

        if user_id:
            from accounts.models import User
            try:
                user = User.objects.get(id=user_id)
                wallet = get_or_create_wallet(user)
                amount = Decimal(payment_intent['amount']) / 100

                # Check if transaction already exists (idempotency)
                if not Transaction.objects.filter(
                    stripe_payment_intent_id=payment_intent['id']
                ).exists():
                    wallet.balance += amount
                    wallet.save()
                    Transaction.objects.create(
                        wallet=wallet,
                        amount=amount,
                        transaction_type='deposit',
                        description='Stripe deposit',
                        stripe_payment_intent_id=payment_intent['id']
                    )
            except User.DoesNotExist:
                pass

    return JsonResponse({'status': 'success'})
