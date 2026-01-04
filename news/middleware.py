from .models_activity import ActivityLog

class ActivityLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before view (optional)
        
        response = self.get_response(request)
        
        # Process response (Log activity if user is logged in)
        if request.user.is_authenticated and request.path != '/favicon.ico':
            # Avoid logging static files or admin polling if desired, but for now log everything
            # We filter out common noisy paths if needed.
            
            # Simple logic: Log "Method Path"
            action = f"{request.method} {request.path}"
            
            # Use specific details for POST requests (data modification)
            details = ""
            if request.method == 'POST':
                details = "Submitted Form / Data"
            
            # Avoid duplicate logging if I already logged explicitly in views (optional optimization)
            # But simplistic approach is robust:
            
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                details=details,
                ip_address=request.META.get('REMOTE_ADDR')
            )

        return response
