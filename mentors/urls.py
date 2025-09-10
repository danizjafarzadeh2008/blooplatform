from django.urls import path
from . import views

urlpatterns = [
    path('', views.mentor_list, name='mentor_list'),
    path('ask-question/', views.ask_question, name='ask_question'),
    path('ask-question/<slug:mentor_slug>/', views.ask_question, name='ask_mentor_question'),
    path('question-submitted/', views.question_submitted, name='question_submitted'),
]