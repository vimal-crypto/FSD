from django.shortcuts import render, redirect
from django.http import JsonResponse
from transformers import pipeline
from .models import Mail
import requests
from bs4 import BeautifulSoup
from collections import Counter
from string import punctuation
import json

# Pipeline for answering questions
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def index(request):
    if request.method == "POST":
        url = request.POST.get('url')
        if Mail.objects.filter(url=url).exists():
            query = Mail.objects.get(url=url)
            words = json.loads(query.words)
            full_text = query.full_text  # Retrieve full text from DB if already saved
            context = {'url': url, 'words': words, 'full_text': full_text, 'chat_history': []}
            return render(request, 'result.html', context)
        else:
            context = {'url': url, 'words': None, 'chat_history': [], 'full_text': ''}
            return render(request, 'result.html', context)
    return render(request, 'home.html')


from django.http import JsonResponse
from bs4 import BeautifulSoup
import requests


def perform_webscraping(request):
    if request.method == "POST":
        url = request.POST.get('url')

        # Check if the URL is not empty
        if not url:
            return JsonResponse({'error': 'No URL provided'}, status=400)

        try:
            # Fetch the webpage content
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)

            # Get HTML source code and parsed text
            soup = BeautifulSoup(response.content, 'html.parser')
            full_text = ' '.join(soup.stripped_strings)  # Scraped text from the page
            html_source = soup.prettify()  # Raw HTML source

            # Return the scraped data and HTML source in JSON format
            return JsonResponse({
                'scraped_data': full_text[:500] + '...',  # Limit to first 500 chars for preview
                'html_source': html_source[:2000] + '...',  # Limit HTML source for preview
            })

        except requests.RequestException as e:
            # Handle exceptions related to requests
            return JsonResponse({'error': f'Error fetching URL: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def ask_question(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        url = request.POST.get('url')

        # Retrieve full text for context
        mail = Mail.objects.get(url=url)
        context_text = mail.full_text  # Use full scraped text for descriptive answering

        if context_text:
            # Ask the question to the QA pipeline
            answer = qa_pipeline({
                'question': question,
                'context': context_text
            })

            # Check if an answer was found and if it's valid
            if not answer.get('answer') or len(answer['answer'].strip()) == 0:
                bot_response = "The particular information is not available on this site."
            else:
                bot_response = answer['answer']  # Return the answer as is

            # Update chat history
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'user': question, 'bot': bot_response})
            request.session['chat_history'] = chat_history

            return render(request, 'result.html', {
                'url': url,
                'chat_history': chat_history,
                'words': None,
                'full_text': context_text
            })
        else:
            # If no context is available, return an error message in the chat
            return render(request, 'result.html', {
                'url': url,
                'chat_history': [
                    {'user': question, 'bot': "No content available for answering. Try scraping a webpage first."}],
                'words': None,
                'full_text': ''
            })


def generate_wordcount(request):
    url = request.POST.get('url')

    try:
        # Fetch the corresponding Mail entry to get the full_text
        mail = Mail.objects.get(url=url)
        full_text = mail.full_text

        # Perform the word count on the full text
        word_counter = Counter(
            word.rstrip(punctuation).lower() for word in full_text.split()
        )
        words = word_counter.most_common()  # List of tuples with word counts

        # Return the word count data
        return JsonResponse({
            'words': words
        })

    except Mail.DoesNotExist:
        # If no scraped data is found for the URL
        return JsonResponse({'error': 'No data found for this URL'}, status=404)

