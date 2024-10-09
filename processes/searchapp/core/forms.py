from django import forms
from django.utils.translation import gettext as _


class DocumentForm(forms.Form):
    file = forms.FileField(required=False)
    namespace = forms.CharField(max_length=255)
    title = forms.CharField(max_length=255)
    text = forms.CharField(required=False)
    context = forms.JSONField(required=False)
    url = forms.CharField(max_length=2048, required=False)
    generate_summary = forms.BooleanField(initial=False, required=False)
    parts_size = forms.IntegerField(required=False)
    parts_overlap = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('file') and not cleaned_data.get('text'):
            raise forms.ValidationError(_("You must provide a file or text"))

        return cleaned_data
