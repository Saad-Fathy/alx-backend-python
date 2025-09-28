import logging
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin

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