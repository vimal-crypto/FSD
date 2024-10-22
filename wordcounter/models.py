from django.db import models

class Mail(models.Model):
    url = models.URLField(unique=True)  # Store unique URLs to avoid duplicates
    words = models.TextField(null=True, blank=True)  # Store word counts (JSON serialized)
    full_text = models.TextField(null=True, blank=True)  # Store full HTML content or text content of the page

    def __str__(self):
        return self.url
