from django import forms
#from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, TabHolder, Tab, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, ButtonHolder

filter_choices = [
    #('id', 'id'),
    #('name', 'name'),
    #('natoms', 'natoms'),
    #('ntypes', 'ntypes'),
    (None, 'None'),
    ('energyperatom', 'energy_per_atom'),
    ('bandgap', 'band_gap'),
    ('formationenergy', 'formation_energy'),
    #('stability', 'stability'),
]

class DataFilterForm(forms.Form):
    composition = forms.CharField(required=False, max_length=30)
    calculated = forms.CharField(required=False, max_length=30)
    band_gap = forms.CharField(required=False, max_length=30)
    ntypes = forms.CharField(required=False, max_length=10)
    generic = forms.CharField(required=False, max_length=30)
    limit = forms.IntegerField(required=False, label='limit')
    sort_offset = forms.IntegerField(required=False, label='offset')

    sort_by = forms.TypedChoiceField(
                    required=False,
                    choices=filter_choices,
                    label='Sort results by:',
                    widget=forms.Select,
    )
    desc = forms.TypedChoiceField(
                    required=False,
                    choices=[('False', 'Ascending'), ('True', 'Descending')],
                    label='Order:',
                    widget=forms.RadioSelect,
    )

    def __init__(self, *args, **kwargs):
        super(DataFilterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('search', 'Search', css_class='btn-primary'))
