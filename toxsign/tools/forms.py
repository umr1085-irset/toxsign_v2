from django import forms
from dal import autocomplete
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.signatures.models import Signature
import toxsign.ontologies.models as models

class default_form(forms.Form):

    job_name = forms.CharField(label='Job_name', max_length=100)

    def __init__(self, *args, **kwargs):

        self.projects = kwargs.pop('projects', None)
        self.arguments_order = kwargs.pop('arguments_order', None)
        super(my_tool_form, self).__init__(*args, **kwargs)

        if self.projects:
            self.signatures = Signature.objects.filter(factor__assay__study__project__in=self.projects)
        else:
            self.signatures = Signature.objects.all()

        if self.arguments_order:
            for argument in self.arguments_order.all():
                if argument.argument.user_filled:
                    if argument.argument.type == "TEXT":
                        self.fields[argument.argument.label] = forms.CharField(label="{} ({})".format(argument.argument.label, argument.argument.parameter), max_length=100)
                    elif argument.argument.type == "SIGNATURE":
                        if argument.argument.multiple:
                            self.fields[argument.argument.label] = forms.ModelMultipleChoiceField(queryset=self.signatures, label="{} ({})".format(argument.argument.label, argument.argument.parameter))
                        else:
                            self.fields[argument.argument.label] = forms.ModelChoiceField(queryset=self.signatures, label="{} ({})".format(argument.argument.label, argument.argument.parameter))
                    else:
                    # Ontologies
                        model = getattr(models, argument.argument.type)
                        autocomplete_url = "/ontologies/" + argument.argument.type.lower() + "-autocomplete"
                        if argument.argument.multiple:
                            self.fields[argument.argument.label] = forms.ModelMultipleChoiceField(
                                                                    queryset=model.objects.all(),
                                                                    widget=autocomplete.ModelSelect2(url=autocomplete_url),
                                                                    label="{} ({})".format(argument.argument.label, argument.argument.parameter)
                            )
                        else:
                            self.fields[argument.argument.label] = forms.ModelChoiceField(
                                                                    queryset=model.objects.all(),
                                                                    widget=autocomplete.ModelSelect2(url=autocomplete_url),
                                                                    label="{} ({})".format(argument.argument.label, argument.argument.parameter)
                            )
                    if argument.argument.optional:
                        self.fields[argument.argument.label].required = False

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Submit job'))
