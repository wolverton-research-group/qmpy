from django import forms

class DataFilterForm(forms.Form):
    composition = forms.CharField(
                    required=False,
                    max_length=30,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'composition',
                            'style': 'width: 300px; height: 30px; font-size: large',


                        }
                    )
    )
    calculated = forms.CharField(
                    required=False,
                    max_length=30,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'calculated',
                            'style': 'width: 300px; height: 30px; font-size: large',


                        }
                    )
    )
    band_gap = forms.CharField(
                    required=False,
                    max_length=30,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'band gap',
                            'style': 'width: 300px; height: 30px; font-size: large',


                        }
                    )
    )
    ntypes = forms.CharField(
                    required=False,
                    max_length=30,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'ntypes',
                            'style': 'width: 300px; height: 30px; font-size: large',


                        }
                    )
    )
    generic = forms.CharField(
                    required=False,
                    max_length=30,
                    widget=forms.TextInput(
                        attrs={
                            'style': 'border-color: blue',
                            'placeholder': 'generic',
                            'style': 'width: 300px; height: 30px; font-size: large',


                        }
                    )
    )

    def clean(self):
        cleaned_data = super(DataFilterForm, self).clean()
        composition = cleaned_data.get('composition')
        calculated = cleaned_data.get('composition_include')
        band_gap = cleaned_data.get('band_gap')
        ntypes = cleaned_data.get('ntypes')
        generic = cleaned_data.get('generic')
