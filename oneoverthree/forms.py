from django import forms


class ContactForm(forms.Form):
    fullname = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}))
    subject = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control","placeholder": "Enter eMail"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter Comments"}))

    # def clean(self):
    #     return print(self.cleaned_data)
