from django.http import JsonResponse
from .jwt_utils import decode_token
from .models import User
from .redis_utils import is_token_blacklisted


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that don't require authentication (prefix match)
        public_prefixes = [
            '/auth/',
            '/admin/',
        ]

        # Exact match paths
        public_exact = ['/']

        # Check if path is public
        if request.path in public_exact or any(request.path.startswith(prefix) for prefix in public_prefixes):
            return self.get_response(request)

        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authorization header required'}, status=401)

        token = auth_header.split(' ')[1]

        # Check if token is blacklisted
        if is_token_blacklisted(token):
            return JsonResponse({'error': 'Token has been revoked'}, status=401)

        payload = decode_token(token)

        if not payload:
            return JsonResponse({'error': 'Invalid or expired token'}, status=401)

        try:
            user = User.objects.get(id=payload['user_id'])
            request.user = user
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)

        return self.get_response(request)
