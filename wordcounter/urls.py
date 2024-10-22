from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),  # Home page for URL input
    path('ask-question/', views.ask_question, name='ask_question'),  # Endpoint for asking questions
    path('generate-wordcount/', views.generate_wordcount, name='generate_wordcount'),  # Generate word count
    path('perform-webscraping/', views.perform_webscraping, name='perform_webscraping'),  # Perform web scraping
]
