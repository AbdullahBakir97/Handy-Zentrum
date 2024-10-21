from django import forms
from .models import Customer, CustomerInteraction, LoyaltyProgram, Address


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_loyalty_member",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        # Assuming format_phone_number is a utility function
        from .helpers.utils import format_phone_number

        return format_phone_number(phone_number)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "address_type",
            "address_line_1",
            "address_line_2",
            "city",
            "country",
            "postal_code",
        ]


class CustomerInteractionForm(forms.ModelForm):
    class Meta:
        model = CustomerInteraction
        fields = ["customer", "interaction_type", "notes"]


class LoyaltyProgramForm(forms.ModelForm):
    class Meta:
        model = LoyaltyProgram
        fields = ["customer", "points", "tier"]
