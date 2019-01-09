import phonenumbers
from phonenumbers import PhoneNumberFormat
from io import BytesIO
from django import forms
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.safestring import mark_safe
from PIL import Image

from .models import EmailActivation, GuestEmail
from .signals import user_logged_in
from marketplace.models import Store

User = get_user_model()


class ReactivateEmailForm(forms.Form):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ReactivateEmailForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        request = self.request
        email   = self.cleaned_data.get('email')
        qs      = EmailActivation.objects.email_exists(email)
        if not qs.exists():
            register_link = reverse("register")
            msg = """This email does not exists, would you 
            like to <a href="{link}">register</a>?  
             """.format(link=register_link)
            messages.success(request, mark_safe(msg))
        return email


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'mobile_number')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_mobile_number(self):

        """
        Ensure pattern matches "+234-7012345678"
        Verify mobile number.
        """

        mobile_number = self.cleaned_data.get("mobile_number", None)
        if User.objects.filter(mobile_number=mobile_number).count() > 0:
            raise forms.ValidationError('This mobile number is already in use.')
        try:
            mobile = phonenumbers.parse(mobile_number, None)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Enter number in the correct format '+2347012345678")
        if phonenumbers.is_possible_number(mobile) and phonenumbers.is_valid_number(mobile):
            return phonenumbers.format_number(mobile, PhoneNumberFormat.INTERNATIONAL)
        else:
            raise forms.ValidationError("Enter a valid number in the INTERNATIONAL format")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserDetailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile_number']

    def clean_mobile_number(self):

        """
        Ensure pattern matches "+234-7012345678"
        Verify mobile number.
        """

        mobile_number = self.cleaned_data.get("mobile_number", None)
        try:
            mobile = phonenumbers.parse(mobile_number, None)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Enter number in the correct format '+2347012345678")
        if phonenumbers.is_possible_number(mobile) and phonenumbers.is_valid_number(mobile):
            return phonenumbers.format_number(mobile, PhoneNumberFormat.INTERNATIONAL)
        else:
            raise forms.ValidationError("Enter a valid number in the INTERNATIONAL format")


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'mobile_number', 'first_name', 'last_name', 'password', 'is_active', 'admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def clean_mobile_number(self):

        """
        Ensure pattern matches "+234-7012345678"
        Verify mobile number.
        """

        mobile_number = self.cleaned_data.get("mobile_number", None)
        try:
            mobile = phonenumbers.parse(mobile_number, None)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Enter number in the correct format '+2347012345678")
        if phonenumbers.is_possible_number(mobile) and phonenumbers.is_valid_number(mobile):
            return phonenumbers.format_number(mobile, PhoneNumberFormat.INTERNATIONAL)
        else:
            raise forms.ValidationError("Enter a valid number in the INTERNATIONAL format")


class GuestForm(forms.ModelForm):
    class Meta:
        model = GuestEmail
        fields = [
            'email'
        ]

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GuestForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        # Save the provided password in hashed format
        obj = super(GuestForm, self).save(commit=False)

        if commit:
            obj.save()
            self.request.session['guest_email_id'] = obj.id
        return obj


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "example@email.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "enter password"}))

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        request = self.request
        data = self.cleaned_data
        email = data.get("email")
        password = data.get("password")

        # Check if email is registered
        qs = User.objects.filter(email=email)
        if qs.exists():
            # User email is registered, check active/email activation
            not_active = qs.filter(is_active=False)
            if not_active.exists():
                link = reverse('account:resend-activation')
                reconfirm_msg = """<a href="{resend_link}">resend</a>""".format(resend_link=link)
                msg1 = "Please check your email to confirm your account. " \
                       "Do you need us to " + reconfirm_msg + "?"
                msg2 = "Please go here to " + reconfirm_msg + " confirmation email."
                msg3 = "Email confirmation required"
                # Not active, check email activation
                confirm_email = EmailActivation.objects.filter(email=email)
                is_confirmable = confirm_email.confirmable().exists()
                if is_confirmable:
                    messages.success(request, mark_safe(msg1))
                    raise forms.ValidationError(msg3)
                email_confirm_exists = EmailActivation.objects.email_exists(email).exists()
                if email_confirm_exists:
                    messages.success(request, mark_safe(msg2))
                    raise forms.ValidationError(mark_safe(msg3))
                if not is_confirmable or not email_confirm_exists:
                    raise forms.ValidationError("This user is inactive.")
        user = authenticate(request, email=email, password=password)
        if user is None:
            raise forms.ValidationError("Invalid credentials.")
        login(request, user)
        self.user = user
        user_logged_in.send(user.__class__, instance=user, request=request)
        try:
            del request.session['guest_email_id']
        except:
            pass
        return data


class RegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'mobile_number')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'placeholder': " Email  **"})
        self.fields['mobile_number'].widget.attrs.update({'placeholder': " Phone '+123-7012345678'  **"})
        self.fields['first_name'].widget.attrs.update({'placeholder': " First name  **"})
        self.fields['last_name'].widget.attrs.update({'placeholder': " Last name  **"})
        self.fields['password1'].widget.attrs.update({'placeholder': " Password  **"})
        self.fields['password2'].widget.attrs.update({'placeholder': " Confirm password  **"})
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'sizefull s-text7 p-l-15 p-r-15'})

    def clean(self):
        print(self.data)
        print(self.errors)
        print(self.cleaned_data)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_mobile_number(self):

        """
        Ensure pattern matches "+234-7012345678"
        Verify mobile number.
        """

        mobile_number = self.cleaned_data.get("mobile_number", None)
        try:
            mobile = phonenumbers.parse(mobile_number, None)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Enter number in the correct format '+2347012345678")

        if phonenumbers.is_possible_number(mobile) and phonenumbers.is_valid_number(mobile):
            return phonenumbers.format_number(mobile, PhoneNumberFormat.INTERNATIONAL)

        else:
            raise forms.ValidationError("Enter a valid number in the INTERNATIONAL format")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False  # send confirmation email

        user_image = user.image

        data = self.cleaned_data
        # x = float(data.get('x'))
        # y = float(data.get('y'))
        # w = float(data.get('width'))
        # h = float(data.get('height'))

        # if user_image:
            # buffer = BytesIO()
            # ext = str(user_image).split('.', 1)[1]
            # ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            # image = Image.open(user_image)
            # cropped_image = image.crop((x, y, w + x, h + y))
            # resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
            # resized_image.save(buffer, ext, quality=100)
            # img_content = ContentFile(buffer.getvalue(), user_image.name)
            #
            # user.image.save(user_image.name, img_content, save=False)

        # obj = EmailActivation.objects.create(user=user)  # Sending Confirmation via signals
        # obj.send_activation_email()
        if commit:
            user.save()
        return user


class StoreRegisterForm(forms.ModelForm):

    class Meta:
        model = Store
        fields = (
            'title', 'seller_type', 'description',
            'instagram', 'twitter', 'whatsapp',
            # 'slider_image', 'header_image',
        )

    def __init__(self, *args, **kwargs):
        super(StoreRegisterForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'placeholder': " Store / Brand name  **"})
        self.fields['description'].widget.attrs.update({'placeholder': " Store / Brand slogan  **"})
        self.fields['instagram'].widget.attrs.update({'placeholder': " IG-@handle  **"})
        self.fields['twitter'].widget.attrs.update({'placeholder': " Twitter-@handle"})
        self.fields['whatsapp'].widget.attrs.update({'placeholder': " +234-whatsapp"})
        for field in iter(self.fields):
            if field is 'seller_type':
                self.fields[field].help_text = "  Store type  **"
                self.fields[field].widget.attrs.update({
                    'class': 'js-example-basic-single',
                    'style': "border: 1px solid #e6e6e6; border-radius: 10px; width: 90px; height: 30px;"
                })

            else:
                self.fields[field].widget.attrs.update({
                    'class': 'sizefull s-text7 p-l-15 p-r-15',
                })

    def clean(self):
        print(self.data)
        print(self.cleaned_data)

    def save(self, commit=False, *args, **kwargs):
        store = super(StoreRegisterForm, self).save(commit=False)
        if commit:
            store.save()
        return store


class StoreSliderUploadForm(forms.Form):
    x_1 = forms.FloatField(widget=forms.HiddenInput())
    y_1 = forms.FloatField(widget=forms.HiddenInput())
    width_1 = forms.FloatField(widget=forms.HiddenInput())
    height_1 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, *args, **kwargs):
        data = self.data
        store = kwargs.get('store')

        store_slider_image = store.background_image_a
        ext = str(store_slider_image).split('.', 1)[1]

        x = float(data.get('x_1'))
        y = float(data.get('y_1'))
        w = float(data.get('width_1'))
        h = float(data.get('height_1'))

        if store_slider_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(store_slider_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((1500, 500), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), store_slider_image.name)

            store.background_image_a.save(store_slider_image.name, img_content, save=False)


class StoreHeaderUploadForm(forms.Form):
    x_2 = forms.FloatField(widget=forms.HiddenInput())
    y_2 = forms.FloatField(widget=forms.HiddenInput())
    width_2 = forms.FloatField(widget=forms.HiddenInput())
    height_2 = forms.FloatField(widget=forms.HiddenInput())

    def save(self, *args, **kwargs):
        data = self.data
        store = kwargs.get('store')

        store_header_image = store.background_image_b
        ext = str(store_header_image).split('.', 1)[1]

        x = float(data.get('x_2'))
        y = float(data.get('y_2'))
        w = float(data.get('width_2'))
        h = float(data.get('height_2'))

        if store_header_image:
            buffer = BytesIO()
            ext = 'JPEG' if ext.lower() == 'jpg' else ext.upper()
            image = Image.open(store_header_image)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((1920, 570), Image.ANTIALIAS)
            resized_image.save(buffer, ext, quality=100)
            img_content = ContentFile(buffer.getvalue(), store_header_image.name)

            store.background_image_b.save(store_header_image.name, img_content, save=False)



