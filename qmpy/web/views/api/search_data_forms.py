from django import forms
#from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, TabHolder, Tab, FormActions, InlineField
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
    composition = forms.CharField(required=False)
    calculated = forms.CharField(required=False)
    band_gap = forms.CharField(required=False)
    ntypes = forms.CharField(required=False)
    generic = forms.CharField(required=False)
    limit = forms.IntegerField(required=False, label='limit', initial=50)
    sort_offset = forms.IntegerField(required=False, label='offset', initial=0)

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
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout = Layout(
            TabHolder(
                Tab('Materials properties',
                    Field('composition', css_class="input-sm"),
                    Field('band_gap', css_class="input-sm"),
                    Field('ntypes', css_class="input-sm"),
                    Field('generic', css_class="input-sm"),
                    Field('calculated', css_class="input-sm"),
                   ),
                Tab('Limit',
                    Field('limit', css_class="input-sm"),
                    Field('sort_offset', css_class="input-sm"),
                   ),
                Tab('Sort',
                    Field('sort_by', css_class="input-sm"),
                    Field('desc', css_class="input-sm"),
                   ),
            ),
        )
        self.helper.add_input(Submit('search', 'Search', css_class='btn-primary'))

