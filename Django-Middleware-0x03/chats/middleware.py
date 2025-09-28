import logging
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, HttpResponse

# Configure logger to write to requests.log
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('requests.log'),
    ]
)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log each user's requests to requests.log.
    Logs format: {datetime.now()} - User: {user} - Path: {request.path}
    """
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Log the request with timestamp, user, and path.
        """
        user = request.user if request.user.is_authenticated else 'Anonymous'
        logger.info(f"{datetime.now()} - User: {user} - Path: {request.path}")
        response = self.get_response(request)
        return response

class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access to the messaging app outside 9:00 AM to 6:00 PM.
    Returns 403 Forbidden if the current time is outside these hours.
    """
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Check the current server time and deny access outside 9:00 AM to 6:00 PM.
        """
        current_hour = datetime.now().hour
        if not (9 <= current_hour < 18):
            return HttpResponseForbidden("Access denied: The messaging app is only available between 9:00 AM and 6:00 PM.")
        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware to limit the number of chat messages (POST requests to /api/messages/) 
    to 5 per minute per IP address. Returns 429 Too Many Requests if exceeded.
    """
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable and request tracking."""
        self.get_response = get_response
        self.request_counts = defaultdict(list)  # Store timestamps of POST requests per IP

    def __call__(self, request):
        """
        Check if the request is a POST to /api/messages/ and enforce rate limit.
        """
        if request.method == 'POST' and request.path == '/api/messages/':
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            current_time = datetime.now()
            time_window = current_time - timedelta(minutes=1)

            # Remove requests older than 1 minute
            self.request_counts[ip_address] = [
                timestamp for timestamp in self.request_counts[ip_address]
                if timestamp > time_window
            ]

            # Check if limit (5 messages per minute) is exceeded
            if len(self.request_counts[ip_address]) >= 5:
                return HttpResponse(
                    "Rate limit exceeded: Maximum 5 messages per minute allowed.",
                    status=429
                )

            # Record the current request
            self.request_counts[ip_address].append(current_time)

        response = self.get_response(request)
        return response

class RolePermissionMiddleware(MiddlewareMixin):
    """
    Middleware to restrict access to /api/conversations/ and /api/messages/ to users
    with admin (is_staff) or moderator (in 'Moderator' group) roles.
    Returns 403 Forbidden if the user lacks these roles.
    """
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable."""
        self.get_response = get_response

    def __call__(self, request):
        """
        Check if the user has admin or moderator role for /api/conversations/ or /api/messages/.
        """
        if request.path.startswith(('/api/conversations/', '/api/messages/')):
            if not request.user.is_authenticated:
                # AuthenticationMiddleware will handle unauthenticated users (401)
                return self.get_response(request)
            if not (request.user.is_staff or request.user.groups.filter(name='Moderator').exists()):
                return HttpResponseForbidden(
                    "Access denied: Only admins or moderators can access this endpoint."
                )
        response = self.get_response(request)
        return response