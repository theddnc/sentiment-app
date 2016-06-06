from django import forms


class KeywordAdd(forms.Form):
    keyword = forms.CharField(label='', max_length=50)
