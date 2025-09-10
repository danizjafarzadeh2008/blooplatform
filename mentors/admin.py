from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Mentor, MentorPage, Question

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'department', 'is_active', 'pending_questions_count')
    list_filter = ('is_active', 'university')
    search_fields = ('name', 'university', 'department')
    prepopulated_fields = {'slug': ('name',)}
    
    def pending_questions_count(self, obj):
        return obj.pending_questions_count()
    pending_questions_count.short_description = 'Pending Questions'

@admin.register(MentorPage)
class MentorPageAdmin(admin.ModelAdmin):
    list_display = ('title',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_email', 'mentor', 'status', 'created_at', 'admin_actions')
    list_filter = ('status', 'mentor', 'created_at')
    search_fields = ('user_name', 'user_email', 'question_text')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at', 'answered_at', 'approved_at', 'sent_at')
    actions = ['send_to_mentors', 'approve_answers', 'send_to_users']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user_name', 'user_email', 'question_text', 'status')
        }),
        ('Mentor Assignment', {
            'fields': ('mentor', 'assigned_at')
        }),
        ('Answer', {
            'fields': ('answer_text', 'answered_at')
        }),
        ('Approval', {
            'fields': ('approved_at',)
        }),
        ('Delivery', {
            'fields': ('sent_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def admin_actions(self, obj):
        """Display action buttons in the list view"""
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="{}" style="background-color: #4CAF50; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; display: inline-block;">Assign to Mentor</a>',
                f'{obj.id}/assign/'
            )
        elif obj.status == 'assigned':
            return format_html(
                '<span style="color: #2196F3; display: inline-block; padding: 5px 0;">Waiting for mentor response</span>'
            )
        elif obj.status == 'answered':
            return format_html(
                '<a class="button" href="{}" style="background-color: #FF9800; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; margin-right: 5px; display: inline-block;">Review Answer</a>',
                f'{obj.id}/change/'
            )
        elif obj.status == 'approved':
            return format_html(
                '<a class="button" href="{}" style="background-color: #4CAF50; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; display: inline-block;">Send to User</a>',
                f'{obj.id}/send-to-user/'
            )
        elif obj.status == 'sent' and obj.sent_at:
            return format_html(
                '<span style="color: #4CAF50; display: inline-block; padding: 5px 0;">Sent to user on {}</span>',
                obj.sent_at.strftime('%Y-%m-%d %H:%M')
            )
        elif obj.status == 'sent':
            return format_html(
                '<span style="color: #4CAF50; display: inline-block; padding: 5px 0;">Sent to user</span>'
            )
        return ''
    admin_actions.short_description = 'Actions'
    
    def send_to_mentors(self, request, queryset):
        """Action to send questions to mentors"""
        sent_count = 0
        for question in queryset.filter(status='pending'):
            if question.mentor:
                if question.send_to_mentor(request):
                    question.status = 'assigned'
                    question.assigned_at = timezone.now()
                    question.save()
                    sent_count += 1
                else:
                    self.message_user(request, f"Failed to send question to {question.mentor.name}", level='error')
            else:
                self.message_user(request, f"Question from {question.user_name} has no mentor assigned", level='warning')
        
        if sent_count > 0:
            self.message_user(request, f"Successfully sent {sent_count} questions to mentors.")
    send_to_mentors.short_description = "Send selected questions to mentors"
    
    def approve_answers(self, request, queryset):
        """Approve selected answers"""
        updated_count = queryset.update(status='approved', approved_at=timezone.now())
        self.message_user(request, f"Approved {updated_count} answers.")
    approve_answers.short_description = "Approve selected answers"
    
    def send_to_users(self, request, queryset):
        """Send approved answers to users"""
        sent_count = 0
        for question in queryset.filter(status='approved'):
            if question.send_to_user():
                sent_count += 1
            else:
                self.message_user(request, f"Failed to send answer to {question.user_name}", level='error')
        
        self.message_user(request, f"Successfully sent {sent_count} answers to users.")
    send_to_users.short_description = "Send approved answers to users"
    
    # Custom views for specific actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/assign/', self.admin_site.admin_view(self.assign_to_mentor), name='assign_to_mentor'),
            path('<path:object_id>/send-to-user/', self.admin_site.admin_view(self.send_to_user_view), name='send_to_user'),
        ]
        return custom_urls + urls
    
    def assign_to_mentor(self, request, object_id):
        """Custom view to assign question to mentor"""
        question = get_object_or_404(Question, id=object_id)
        
        if request.method == 'POST':
            mentor_id = request.POST.get('mentor')
            if mentor_id:
                mentor = get_object_or_404(Mentor, id=mentor_id)
                question.mentor = mentor
                
                # Send question to mentor
                if question.send_to_mentor(request):
                    question.status = 'assigned'
                    question.assigned_at = timezone.now()
                    question.save()
                    self.message_user(request, f"Question assigned to {mentor.name} and email sent successfully.")
                else:
                    self.message_user(request, f"Failed to send email to {mentor.name}", level='error')
                
                return HttpResponseRedirect(reverse('admin:mentors_question_changelist'))
        
        # Show mentor selection form
        from django.template.response import TemplateResponse
        context = {
            'question': question,
            'mentors': Mentor.objects.filter(is_active=True),
            'title': 'Assign Question to Mentor',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/assign_to_mentor.html', context)
    
    def send_to_user_view(self, request, object_id):
        """Custom view to send answer to user"""
        question = get_object_or_404(Question, id=object_id)
        
        if question.status == 'approved':
            if question.send_to_user():
                self.message_user(request, "Answer sent to user successfully.")
            else:
                self.message_user(request, "Failed to send answer to user.", level='error')
        else:
            self.message_user(request, "Only approved answers can be sent to users.", level='warning')
        
        return HttpResponseRedirect(reverse('admin:mentors_question_changelist'))