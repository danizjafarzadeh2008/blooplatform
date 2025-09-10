from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['user_name', 'user_email', 'question_text']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
                'placeholder': 'Your Name'
            }),
            'user_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
                'placeholder': 'Your Email'
            }),
            'question_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent',
                'placeholder': 'Your question for our mentors...',
                'rows': 4
            }),
        }