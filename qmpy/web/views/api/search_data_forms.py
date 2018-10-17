from django import forms
from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, TabHolder, Tab, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, ButtonHolder

filter_choices = [
    ('id', 'id'),
    ('name', 'name'),
    ('natoms', 'natoms'),
    ('ntypes', 'ntypes'),
    ('energy_per_atom', 'energy_per_atom'),
    ('band_gap', 'band_gap'),
    ('formation_energy', 'formation_energy'),
    ('stability', 'stability'),
]

class DataFilterForm(forms.Form):
    composition = forms.CharField(required=False, max_length=30)
    calculated = forms.CharField(required=False, max_length=30)
    band_gap = forms.CharField(required=False, max_length=30)
    ntypes = forms.CharField(required=False, max_length=10)
    generic = forms.CharField(required=False, max_length=30)

    sorted_by = forms.TypedChoiceField(
                    required=False,
                    choices=filter_choices,
                    label='Sort results by:',
                    widget=forms.Select,
    )

    def __init__(self, *args, **kwargs):
        super(DataFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('search', 'Search', css_class='btn-primary'))

    #def clean(self):
    #    cleaned_data = super(DataFilterForm, self).clean()
    #    composition = cleaned_data.get('composition')
    #    calculated = cleaned_data.get('calcualted')
    #    band_gap = cleaned_data.get('band_gap')
    #    ntypes = cleaned_data.get('ntypes')
    #    generic = cleaned_data.get('generic')
