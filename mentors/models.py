from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import default_storage

class Mentor(models.Model):
    name = models.CharField(max_length=100)
    university = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    initials = models.CharField(max_length=2)
    gradient = models.CharField(max_length=50, default='from-purple-400 to-pink-400')
    slug = models.SlugField(unique=True)
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    profile_photo = models.ImageField(upload_to='mentors/profile_photos/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def pending_questions_count(self):
        return self.question_set.filter(status='assigned').count()
    
    @property
    def profile_photo_url(self):
        if self.profile_photo and default_storage.exists(self.profile_photo.name):
            return self.profile_photo.url
        return None
    
    class Meta:
        ordering = ['name']

class MentorPage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    def __str__(self):
        return self.title

class Question(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned to Mentor'),
        ('answered', 'Answered by Mentor'),
        ('approved', 'Approved by Admin'),
        ('rejected', 'Rejected by Admin'),
        ('sent', 'Sent to User'),
    )
    
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    question_text = models.TextField()
    mentor = models.ForeignKey(Mentor, on_delete=models.SET_NULL, null=True, blank=True)
    answer_text = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Question from {self.user_name} - {self.status}"
    
    def send_to_mentor(self, request=None):
        """Send question to mentor via email"""
        if self.mentor and self.mentor.email:
            try:
                subject = f"New Question from {self.user_name}"
                message = (
                    f"Hello {self.mentor.name},\n\n"
                    f"You have received a new question from {self.user_name}:\n\n"
                    f"QUESTION:\n{self.question_text}\n\n"
                    f"Please reply to this email with your answer.\n\n"
                    f"Best regards,\nThe Bloo Team"
                )
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.mentor.email],
                    fail_silently=False,
                )
                return True
            except Exception as e:
                print(f"Failed to send email to mentor: {e}")
                return False
        return False
    
    def send_to_user(self):
        """Send approved answer to user"""
        try:
            mentor_name = self.mentor.name if self.mentor else "our mentor"
            subject = f"Answer to your question from {mentor_name}"
            message = (
                f"Dear {self.user_name},\n\n"
                f"Thank you for your question. Here is the answer from our expert:\n\n"
                f"QUESTION:\n{self.question_text}\n\n"
                f"ANSWER:\n{self.answer_text}\n\n"
                f"If you have any follow-up questions, please don't hesitate to ask.\n\n"
                f"Best regards,\nThe Bloo Team"
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.user_email],
                fail_silently=False,
            )
            self.status = 'sent'
            self.sent_at = timezone.now()
            self.save()
            return True
        except Exception as e:
            print(f"Failed to send email to user: {e}")
            return False
    
    class Meta:
        ordering = ['-created_at']