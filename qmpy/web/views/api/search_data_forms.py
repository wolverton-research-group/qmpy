from django import forms
#from django.core.urlresolvers import reverse
from crispy_forms.bootstrap import Field, TabHolder, Tab, FormActions, InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, ButtonHolder, HTML, Row, Column

filter_choices = [
    #('id', 'id'),
    #('name', 'name'),
    #('natoms', 'natoms'),
    #('ntypes', 'ntypes'),
    (None, 'none'),
    #('energyperatom', 'energy_per_atom'),
    #('bandgap', 'band_gap'),
    #('formationenergy', 'formation_energy'),
    ('stability', 'stability'),
]

def popover_html(label, content):
    OUT = label + ' <a tabindex="0" role="button" data-toggle="popover" data-html="true"' +\
         'data-trigger="hover" data-placement="auto"' +\
         'data-content="' + content + '">' +\
         '<span class="glyphicon glyphicon-info-sign"></span></a>'
    return OUT



class DataFilterForm(forms.Form):
    composition = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'e.g. Al2O3, Fe-O, {3d}O'}, )
                                 )
    element_set = forms.CharField(required=False, label='Element Set',
                                  widget=forms.TextInput(attrs={'placeholder': 'e.g. S, (Mn,Fe)-O'},
                                                        ),
                                  help_text="""Use '-' as AND operator and ',' as OR operator. 
                                  Use '(' and ')' to change priority.""",
                                 )
    prototype = forms.CharField(required=False, 
                                widget=forms.TextInput(attrs={'placeholder': 'e.g. Cu, CsCl'}, )
                               )
    spacegroup = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'e.g. Fm-3m, P4/mmm'})
                                )
    generic = forms.CharField(required=False, 
                              widget=forms.TextInput(attrs={'placeholder': 'e.g. AB, AB2'})
                             )
    icsd = forms.CharField(required=False, label='ICSD tag',
                                widget=forms.TextInput(attrs={'placeholder': 'e.g. True, T, False, F'}),
                          )
    band_gap = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'e.g. 0, >0.3'}),
                              )
    delta_e = forms.CharField(required=False, label='Formation Energy',
                              widget=forms.TextInput(attrs={'placeholder': 'e.g. <-0.5'})
                             )
    stability = forms.CharField(required=False, 
                                widget=forms.TextInput(attrs={'placeholder': 'e.g. <-0.5'}),
                               )
    natoms = forms.CharField(required=False, label='# of atoms', 
                             widget=forms.TextInput(attrs={'placeholder': 'e.g. 2, >3'})
                            )
    ntypes = forms.CharField(required=False, label='# of element types',
                             widget=forms.TextInput(attrs={'placeholder': 'e.g. 2, >3'}),
                             )
    volume = forms.CharField(required=False)
    filters = forms.CharField(required=False)
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
                    initial='False',
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
                Tab('Filters',
                    HTML('<p style="margin-left: 10px; margin-bottom: 20px; font-size: 15px; font-weight:\
                         600">General properties</p>'),
                    Div(
                        Div('element_set', css_class="span4"),
                        css_class='row-fluid'
                    ),
                    Div(
                        Div('composition', css_class="span4"),
                        Div('icsd', css_class="span4"),
                        css_class='row-fluid'
                    ),
                    HTML('<br><p style="margin-left: 10px; margin-bottom: 20px; font-size: 15px; font-weight:\
                         600">Structural properties</p>'),
                    Div(
                        Div('ntypes', css_class="span4"),
                        Div('natoms', css_class="span4"),
                        css_class='row-fluid'
                    ),
                    Div(
                        Div('prototype', css_class="span4"),
                        Div('generic', css_class="span4"),
                        css_class='row-fluid'
                    ),
                    HTML('<br><p style="margin-left: 10px; margin-bottom: 20px; font-size: 15px; font-weight:\
                         600">DFT calculated properties</p>'),
                    Div(
                        Div('stability', css_class="span4"),
                        Div('band_gap', css_class="span4"),
                        css_class='row-fluid'
                    ),
                    Div(
                        Div('delta_e', css_class="span4"),
                        css_class='row-fluid'
                    ),
                   ),
                Tab('Manual Input Filters',
                    Div(
                        Field('filters', css_class="span8"),
                        css_class='row-fluid'
                    ),
                   ),
            ),
            TabHolder(
                Tab('Order of Results',
                    Field('sort_by', css_class="input-sm"),
                    Field('desc', css_class="input-sm"),
                   ),
                Tab('Limit',
                    Field('limit', css_class="input-sm"),
                    Field('sort_offset', css_class="input-sm"),
                   ),
            ),
        )
        self.helper.add_input(Submit('search', 'Search', css_class='btn-primary'))

