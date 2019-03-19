from django import forms

class APIKeyForm(forms.Form):
    username = forms.CharField(
                    max_length=30,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'Choose a username',
                            'style': 'width: 300px; height: 30px; font-size: large',


                        }
                    )
    )
    email = forms.EmailField(
                    max_length=254,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'Enter a valid email address',
                            'style': 'width: 300px; height: 30px; font-size: large',
                        }
                    )
    )

    def clean(self):
        cleaned_data = super(APIKeyForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if not username and not email:
            raise forms.ValidationError('You have to input your info')
