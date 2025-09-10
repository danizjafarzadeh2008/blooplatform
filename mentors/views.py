from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .models import Mentor, MentorPage, Question
from .forms import QuestionForm
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

def mentor_list(request):
    mentors = Mentor.objects.filter(is_active=True)
    page_data = MentorPage.objects.first()
    
    query = request.GET.get('q')
    if query:
        mentors = mentors.filter(
            Q(name__icontains=query) |
            Q(university__icontains=query) |
            Q(department__icontains=query)
        )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        mentors_data = []
        for mentor in mentors:
            mentors_data.append({
                'id': mentor.id,
                'name': mentor.name,
                'university': mentor.university,
                'department': mentor.department,
                'initials': mentor.initials,
                'gradient': mentor.gradient,
                'slug': mentor.slug,
                'profile_photo_url': mentor.profile_photo.url if mentor.profile_photo else None,
            })
        return JsonResponse({'mentors': mentors_data})
    
    context = {
        'mentors': mentors,
        'page_data': page_data,
    }
    return render(request, 'mentors/mentor_list.html', context)

def ask_question(request, mentor_slug=None):
    mentor = None
    if mentor_slug:
        mentor = get_object_or_404(Mentor, slug=mentor_slug, is_active=True)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            if mentor:
                question.mentor = mentor
            question.save()
            
            try:
                send_mail(
                    f"New Question from {question.user_name}",
                    f"You have a new question from {question.user_name} ({question.user_email}):\n\n"
                    f"{question.question_text}\n\n"
                    f"Login to the admin panel to assign it to a mentor: {request.build_absolute_uri(reverse('admin:index'))}",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except:
                pass  # Don't fail if email doesn't send
            
            messages.success(request, "Your question has been submitted! We'll get back to you soon.")
            return redirect('question_submitted')
    else:
        form = QuestionForm()
    
    context = {
        'form': form,
        'mentor': mentor,
        'mentors': Mentor.objects.filter(is_active=True) if not mentor else None,
    }
    return render(request, 'mentors/ask_question.html', context)

def question_submitted(request):
    return render(request, 'mentors/question_submitted.html')