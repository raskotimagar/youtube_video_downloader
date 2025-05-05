from django import forms

class YouTubeForm(forms.Form):
    url = forms.URLField(label='YouTube Video URL', widget=forms.URLInput(attrs={
        'placeholder': 'Enter a YouTube URL',
        'class': 'form-control'
    }))
