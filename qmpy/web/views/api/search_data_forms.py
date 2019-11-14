from django import forms
from crispy_forms.bootstrap import Field, TabHolder, Tab, FormActions, InlineField, InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, ButtonHolder, HTML, Row, Column, Reset

filter_choices = [
    (None, 'None'),
    ('delta_e', 'Formation Energy'),
    ('stability', 'Stability'),
]

def popover_html(label, content):
    OUT = label + ' <a tabindex="0" role="button" data-toggle="popover" data-html="true"' +\
         'data-trigger="hover" data-placement="auto"' +\
         'data-content="' + content + '">' +\
         '<span class="glyphicon glyphicon-info-sign"></span></a>'
    return OUT



class DataFilterForm(forms.Form):
    composition = forms.CharField(required=False,
                                  widget=forms.TextInput(
                                      attrs={'placeholder': 'e.g. Al2O3, Fe-O, {3d}2O3'} 
                                  ),
                                  help_text="<html><a href='/materials/element_groups'\
                                  target='_blank'>Available element groups</a>"
                                 )
    element_set = forms.CharField(required=False, label='Element Set',
                                  widget=forms.TextInput(attrs={'placeholder': 'e.g. S, (Mn-Fe),O'},
     ),
                                  help_text="<html>Use <code>,</code> as <b>AND</b> and\
                                  <code>-</code> as <b>OR</b> <br>\
                                  Use <code>(</code> and <code>)</code> to change priority</html>",
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
    icsd = forms.TypedChoiceField(
                    required=False,
                    choices=[(None, 'All'), ('True', 'Include'), ('False', 'Exclude')],
                    label='ICSD Tag',
                    widget=forms.Select,
                    initial='None',
    )
    noduplicate = forms.TypedChoiceField(
                    required=False,
                    choices=[('True', 'Yes'), ('False', 'No')],
                    label='Exclude Duplicate',
                    widget=forms.Select,
                    initial='False',
    )
    band_gap = forms.CharField(required=False, label='Band Gap',
                               widget=forms.TextInput(attrs={'placeholder': 'e.g. 0, !=0, >0.3'}),
                              )
    delta_e = forms.CharField(required=False, label='Formation Energy',
                              widget=forms.TextInput(attrs={'placeholder': 'e.g. <=-0.5'})
                             )
    stability = forms.CharField(required=False, 
                                widget=forms.TextInput(attrs={'placeholder': 'e.g. 0, <=0.05'}),
                               )
    natoms = forms.CharField(required=False, label='# of Atoms', 
                             widget=forms.TextInput(attrs={'placeholder': 'e.g. 2, >3'})
                            )
    ntypes = forms.CharField(required=False, label='# of Element Types',
                             widget=forms.TextInput(attrs={'placeholder': 'e.g. 2, >3, !=1'}),
                             )
    volume = forms.CharField(required=False)
    filter = forms.CharField(required=False, label='Filter', help_text="<html>Available Filters:\
                             <i>element_set</i>, <i>element</i>, <i>spacegroup</i>, <i>prototype</i>,\
                             <i>generic</i>, <i>volume</i>, <i>natoms</i>, <i>ntypes</i>,\
                             <i>stability</i>, <i>delta_e</i>, <i>band_gap</i><br>\
                             Logical Operators: <code>AND</code>, <code>OR</code>, <code>NOT</code>\
                             </html>",
                             widget=forms.TextInput(attrs={'placeholder': 'e.g. (NOT element=O) AND (ntypes=2 OR spacegroup="Fm-3m") AND stability<0.01'}),
                            )
    limit = forms.IntegerField(required=False, label='Limit', initial=50)
    sort_offset = forms.IntegerField(required=False, label='Offset', initial=0)

    sort_by = forms.TypedChoiceField(
                    required=False,
                    choices=filter_choices,
                    label='Sort By',
                    widget=forms.Select,
    )
    desc = forms.TypedChoiceField(
                    required=False,
                    choices=[('False', 'Asc'), ('True', 'Desc')],
                    label='Order',
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
        self.helper.form_action = '#apisearchresult'

        self.helper.layout = Layout(
            HTML('<p style="margin-left: 10px; margin-bottom: 20px; font-size: 17px; font-weight:\
                 600">General Properties</p>'),
            Div(
                Div('element_set', css_class="span4"),
                Div('composition', css_class="span4"),
                css_class='row-fluid'
            ),
            Div(
                Div(
                    InlineRadios('noduplicate'),
                    css_class="span4"
                ),
                Div('icsd', css_class="span4"),
                css_class='row-fluid'
            ),
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
            HTML('<br><p style="margin-left: 10px; margin-bottom: 20px; font-size: 17px; font-weight:\
                 600">DFT Calculated Properties</p>'),
            Div(
                Div('stability', css_class="span4"),
                Div('band_gap', css_class="span4"),
                css_class='row-fluid'
            ),
            Div(
                Div('delta_e', css_class="span4"),
                css_class='row-fluid'
            ),
            HTML('<br><p style="margin-left: 10px; margin-bottom: 20px; font-size: 17px; font-weight:\
                 600">Sorting and Pagination</p>'),
            Div(
                Div('sort_by', css_class="span4"),
                Div(InlineRadios('desc'), css_class="span4"),
                css_class='row-fluid'
            ),
            Div(
                Div('limit', css_class="span4"),
                Div('sort_offset', css_class="span4"),
                css_class='row-fluid'
            ),
            HTML('<br><p style="margin-left: 10px; margin-bottom: 20px; font-size: 17px; font-weight:\
                 600">Manual Input Filters</p>'),
            Div(
                Field('filter', css_class="span8"),
                css_class='row-fluid'
            ),
        )
        self.helper.add_input(Submit('search', 'Search', css_class='btn-primary'))
        self.helper.add_input(Submit('clear', 'Reset', css_class='btn-success clear'))
        self.helper.disable_csrf = False
