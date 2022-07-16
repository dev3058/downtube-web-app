from django import forms
class SearchForm(forms.Form):
    search_data = forms.CharField(widget = forms.TextInput(attrs={
        'placeholder' : 'Search...',
        'class' : 'datalist-input',
        'list' : 'lst-autocomplete',

    }))
class linkSearchForm(forms.Form):
    link_search_data = forms.URLField(widget = forms.URLInput(attrs={
        'placeholder' : '⬇️ Supported Shared link....',
    }), help_text='Provide Valid YouTube Link')

class FeedbackForm(forms.Form):
    full_name = forms.CharField(widget = forms.TextInput(attrs={
        'placeholder' : 'Full Name',
    }))
    email = forms.EmailField(widget = forms.EmailInput(attrs={
        'placeholder' : 'Email',
    }))
    subject = forms.CharField(widget = forms.TextInput(attrs={
        'placeholder' : 'Subject',
    }))
    comment_area = forms.CharField(widget = forms.Textarea(attrs={
        'placeholder' : 'Your Comment',
        'cols' : "30",
        'rows' : "10",
    }))
    

