import json
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Post
from wallet.models import Wallet


def get_author_data(user):
    """Helper to format author data for responses."""
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }


def post_to_dict(post):
    """Helper to convert post to dictionary."""
    return {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'rating': post.rating,
        'author': get_author_data(post.author),
        'created_at': post.created_at.isoformat(),
        'updated_at': post.updated_at.isoformat(),
    }


@require_http_methods(["GET"])
def get_all_posts(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    posts = Post.objects.select_related('author').order_by('-created_at')
    data = [post_to_dict(post) for post in posts]
    return JsonResponse({'posts': data})


@require_http_methods(["GET"])
def get_post(request, post_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    try:
        post = Post.objects.select_related('author').get(id=post_id)
        return JsonResponse(post_to_dict(post))
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def create_post(request):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        rating = data.get('rating')

        if not all([title, description, rating]):
            return JsonResponse({'error': 'title, description, and rating are required'}, status=400)

        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return JsonResponse({'error': 'rating must be an integer between 1 and 5'}, status=400)

        # Check wallet balance and deduct post creation fee
        post_cost = Decimal(settings.POST_CREATION_COST)
        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        if not wallet.has_sufficient_funds(post_cost):
            return JsonResponse({
                'error': 'Insufficient funds',
                'required': str(post_cost),
                'balance': str(wallet.balance)
            }, status=402)

        # Deduct the fee
        wallet.withdraw(post_cost, description='Post creation fee')

        post = Post.objects.create(
            title=title,
            description=description,
            rating=rating,
            author=request.user
        )
        return JsonResponse(post_to_dict(post), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def edit_post(request, post_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        post = Post.objects.select_related('author').get(id=post_id)

        # Check if user is the author
        if post.author_id != request.user.id:
            return JsonResponse({'error': 'You can only edit your own posts'}, status=403)

        data = json.loads(request.body)

        if 'title' in data:
            post.title = data['title']
        if 'description' in data:
            post.description = data['description']
        if 'rating' in data:
            rating = data['rating']
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return JsonResponse({'error': 'rating must be an integer between 1 and 5'}, status=400)
            post.rating = rating

        post.save()
        return JsonResponse(post_to_dict(post))
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_post(request, post_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        post = Post.objects.get(id=post_id)

        # Check if user is the author
        if post.author_id != request.user.id:
            return JsonResponse({'error': 'You can only delete your own posts'}, status=403)

        post.delete()
        return JsonResponse({'message': 'Post deleted successfully'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
