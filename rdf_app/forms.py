from django import forms

from .models import User, UserProfile


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile

        fields = [
            "date_of_birth",
            "gender",
            "city",
            "state",
            "pincode",
            "alternate_phone",
            "bio",
        ]

        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),
            "gender": forms.Select(),
            "city": forms.TextInput(
                attrs={
                    "maxlength": "100"
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "maxlength": "100"
                }
            ),
            "pincode": forms.TextInput(
                attrs={
                    "maxlength": "10",
                    "inputmode": "numeric"
                }
            ),
            "alternate_phone": forms.TextInput(
                attrs={
                    "maxlength": "15",
                    "inputmode": "tel"
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "maxlength": "500",
                    "rows": 4
                }
            ),
        }

    def clean_city(self):
        city = self.cleaned_data.get("city", "").strip()

        if city:
            return city.title()

        return city

    def clean_state(self):
        state = self.cleaned_data.get("state", "").strip()

        if state:
            return state.title()

        return state

    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode", "").strip()

        if pincode and not pincode.isdigit():
            raise forms.ValidationError(
                "Pincode must contain only numbers."
            )

        return pincode

    def clean_alternate_phone(self):
        phone = self.cleaned_data.get(
            "alternate_phone",
            ""
        ).strip()

        if phone:
            phone = phone.replace(" ", "")

            if not phone.isdigit():
                raise forms.ValidationError(
                    "Enter a valid alternate phone number."
                )

        return phone