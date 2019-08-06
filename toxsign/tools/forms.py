from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.signatures.models import Signature

class python_printForm(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of charaters', max_length=200)

class module_006_Form(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of charaters', max_length=200)

class module_007_Form(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of charaters', max_length=200)

class test_form(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of characters', max_length=200)
    signatures = forms.ModelMultipleChoiceField(
                    queryset=Signature.objects.all(),
                    required=False)

    def __init__(self, *args, **kwargs):

        self.projects = kwargs.pop('projects', None)
        self.arguments_order = kwargs.pop('arguments_order', None)
        super(test_form, self).__init__(*args, **kwargs)

        if self.projects:

            signatures = Signature.objects.filter(factor__assay__study__project__in=self.projects)
            self.fields['signatures'].queryset = signatures
            if not signatures.exists():
                self.fields['signatures'].widget.attrs['disabled'] = True

        if self.arguments_order:
            for argument in self.arguments_order.all():
                if argument.argument.user_filled:
                    self.fields[argument.argument.label] = forms.CharField(label="{} ({})".format(argument.argument.label, argument.argument.parameter), max_length=100)
                    if argument.argument.optional:
                        self.fields[argument.argument.label].required = False

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Submit job'))

