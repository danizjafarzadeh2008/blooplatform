from django.shortcuts import render
from mentors.models import Mentor
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

def home(request):
    mentors = Mentor.objects.all()[:12]
    return render(request, 'core/home.html', {'mentors': mentors})

def contact(request):
    return render(request, 'core/contact.html')

def coming_soon(request):
    return render(request, 'core/coming-soon.html')

def handler404(request):
    return render(request, '404.html', status=404)