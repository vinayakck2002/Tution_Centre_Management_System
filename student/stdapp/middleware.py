from django.shortcuts import redirect
from django.urls import resolve, reverse
from .models import Teacher

class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            current_url = resolve(request.path_info).url_name
            exempt_urls = ['change_password', 'logout', 'admin:index', 'static']
            
            if current_url not in exempt_urls:
                try:
                    teacher = Teacher.objects.get(email=request.user.username)
                    if teacher.last_login is None:
                        return redirect('change_password')
                except Teacher.DoesNotExist:
                    pass
                
        response = self.get_response(request)
        return response
