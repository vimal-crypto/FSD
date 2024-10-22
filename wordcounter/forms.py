from django import forms

class InputForm(forms.Form):
    url = forms.URLField(label='Website URL', widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter the URL'
    }))
