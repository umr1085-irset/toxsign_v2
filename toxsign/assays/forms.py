from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.assays.models import Assay, Factor



class AssayCreateForm(forms.ModelForm):

    class Meta:
        model = Assay
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", "study", )

    def __init__(self, *args, **kwargs):
        super(AssayCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class FactorCreateForm(forms.ModelForm):

    class Meta:
        model = Factor
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", "assay", )

    def __init__(self, *args, **kwargs):
        super(FactorCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
