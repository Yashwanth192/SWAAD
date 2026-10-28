from django import forms
from django.contrib.auth.models import User
from accounts.models import UserDetails, Vendor, Menu, Address, Review
from django_recaptcha.fields import ReCaptchaField


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        # fields = '__all__'
        fields = ['username', 'email', 'password']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = [
            'phone',
            'age',
            'house_no',
            'street',
            'landmark',
            'city',
            'state',
            'zipcode',
            'userpic'
        ]

    captcha = ReCaptchaField()


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = [
            'phone',
            'age',
            'house_no',
            'street',
            'landmark',
            'city',
            'state',
            'zipcode',
            'userpic'
        ]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['label', 'house_no', 'street', 'city', 'state', 'zipcode']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(5, '5 Stars'), (4, '4 Stars'), (3, '3 Stars'), (2, '2 Stars'), (1, '1 Star')],
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


# =====================================================
# VENDOR FORM - ADDED
# =====================================================

class VendorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['accept'] = 'image/*'

    class Meta:
        model = Vendor

        fields = [
            'vendor_name',
            'restaurant_name',
            'phone_num',
            'address1',
            'address2',
            'city',
            'state',
            'zipcode',
            'gst_no',
            'licence_img',
            'restaurant_img'
        ]


# =====================================================
# MENU FORM - ADDED
# =====================================================

class MenuForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs['accept'] = 'image/*'
                field.widget.initial_text = 'Current image'
                field.widget.input_text = 'Choose a new image'
                field.widget.clear_checkbox_label = 'Remove image'

            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 5

    class Meta:
        model = Menu

        fields = [
            'food_name',
            'price',
            'category',
            'description',
            'food_image',
            'is_available'
        ]