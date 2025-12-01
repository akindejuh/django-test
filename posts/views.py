import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Post


@require_http_methods(["GET"])
def get_all_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    data = [
        {
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'rating': post.rating,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
        }
        for post in posts
    ]
    return JsonResponse({'posts': data})


@require_http_methods(["GET"])
def get_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        data = {
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'rating': post.rating,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def create_post(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description')
        rating = data.get('rating')

        if not all([title, description, rating]):
            return JsonResponse({'error': 'title, description, and rating are required'}, status=400)

        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return JsonResponse({'error': 'rating must be an integer between 1 and 5'}, status=400)

        post = Post.objects.create(
            title=title,
            description=description,
            rating=rating
        )
        return JsonResponse({
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'rating': post.rating,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def edit_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
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
        return JsonResponse({
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'rating': post.rating,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
        })
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({'message': 'Post deleted successfully'})
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)
