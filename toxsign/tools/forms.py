from django import forms
from dal import autocomplete
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.signatures.models import Signature
from toxsign.tools.models import PredictionModel
import toxsign.ontologies.models as models

from crispy_forms.layout import Submit, Layout, HTML, Div

class SignatureChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "{} - {}".format(obj.tsx_id, obj.name)

class default_form(forms.Form):

    job_name = forms.CharField(label='Job_name', max_length=100)

    def __init__(self, *args, **kwargs):

        self.projects = kwargs.pop('projects', None)
        self.arguments = kwargs.pop('arguments', None)
        super(default_form, self).__init__(*args, **kwargs)

        if self.projects:
            self.signatures = Signature.objects.filter(factor__assay__project__in=self.projects)
        else:
            self.signatures = Signature.objects.all()

        if self.arguments:
            for argument in self.arguments.all():
                if argument.user_filled:
                    if argument.argument_type.type == "Text":
                        self.fields[argument.label] = forms.CharField(label="{} ({})".format(argument.label, argument.parameter), max_length=100)
                    if argument.argument_type.type == "Job_id":
                        # We skip this, it will be added later
                        pass
                    elif argument.argument_type.type == "Signature":
                        if argument.multiple:
                            self.fields[argument.label] = forms.ModelMultipleChoiceField(queryset=self.signatures, label="{} ({})".format(argument.label, argument.parameter))
                        else:
                            self.fields[argument.label] = forms.ModelChoiceField(queryset=self.signatures, label="{} ({})".format(argument.label, argument.parameter))
                    else:
                    # Ontologies
                        model = getattr(models, argument.argument_type.type)
                        autocomplete_url = "/ontologies/" + argument.argument_type.type.lower() + "-autocomplete"
                        if argument.multiple:
                            self.fields[argument.label] = forms.ModelMultipleChoiceField(
                                                                    queryset=model.objects.all(),
                                                                    widget=autocomplete.ModelSelect2Multiple(url=autocomplete_url, attrs={'data-minimum-input-length': 3}),
                                                                    label="{} ({})".format(argument.label, argument.parameter)
                            )
                        else:
                            self.fields[argument.label] = forms.ModelChoiceField(
                                                                    queryset=model.objects.all(),
                                                                    widget=autocomplete.ModelSelect2(url=autocomplete_url, attrs={'data-minimum-input-length': 3}),
                                                                    label="{} ({})".format(argument.label, argument.parameter)
                            )
                    if argument.optional:
                        self.fields[argument.label].required = False

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Submit job'))

class signature_compute_form(forms.Form):

    job_name = forms.CharField(label='Job_name', max_length=100)

    def __init__(self, *args, **kwargs):

        self.signatures = kwargs.pop('signatures')
        self.selected_signature = kwargs.pop('selected_signature', None)
        super(signature_compute_form, self).__init__(*args, **kwargs)

        self.fields["signature"] = SignatureChoiceField(
            queryset=self.signatures,
            label="Signature",
            widget=autocomplete.ModelSelect2(url='/signatures/signature-autocomplete', attrs={'data-minimum-input-length': 3})
        )

        if self.selected_signature:
            self.fields["signature"].initial = self.selected_signature

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Submit job'))

class signature_cluster_compute_form(forms.Form):

    CHOICES = (("euclidean","Euclidean distance"),("correlation","Correlation distance"))

    job_name = forms.CharField(label='Job_name', max_length=100, required=True)
    cluster_type = forms.ChoiceField(choices = CHOICES, label="Cluster distance type", widget=forms.Select(), required=True, help_text='The distance calculation method used to define the ChemPSy clusters')

    def __init__(self, *args, **kwargs):

        self.signatures = kwargs.pop('signatures')
        self.selected_signature = kwargs.pop('selected_signature', None)
        super(signature_cluster_compute_form, self).__init__(*args, **kwargs)

        self.fields["signature"] = SignatureChoiceField(
            queryset=self.signatures,
            label="Signature",
            widget=autocomplete.ModelSelect2(url='/signatures/signature-autocomplete', attrs={'data-minimum-input-length': 3})
        )

        if self.selected_signature:
            self.fields["signature"].initial = self.selected_signature

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Submit job'))

class prediction_compute_form(forms.Form):

    job_name = forms.CharField(label='Job_name', max_length=100)

    def __init__(self, *args, **kwargs):

        self.signatures = kwargs.pop('signatures')
        self.selected_signature = kwargs.pop('selected_signature', None)
        super(prediction_compute_form, self).__init__(*args, **kwargs)

        self.fields["model"] = forms.ModelChoiceField(
            queryset=PredictionModel.objects.all(),
            label="Prediction model",
        )

        self.fields["signature"] = SignatureChoiceField(
            queryset=self.signatures,
            label="Signature",
            widget=autocomplete.ModelSelect2(url='/signatures/signature-autocomplete', attrs={'data-minimum-input-length': 3})
        )

        if self.selected_signature:
            self.fields["signature"].initial = self.selected_signature

        self.helper = FormHelper(self)
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_method = 'POST'

        self.helper.layout = Layout(
            Div('job_name'),
            Div('model'),
        )
        
        modal_button = '<p><button type="button" class="btn btn-primary btn-sm" data-toggle="modal" data-target="#modal-models">More info</button></p>'

        for model in PredictionModel.objects.all():
            stats = "<p>This model has a precision of {:.3f}, a recall of {:.3f} and a specificity of {:.3f} {}</p>".format(model.parameters['model_data']['precision'], model.parameters['model_data']['recall'], model.parameters['model_data']['specificity'], modal_button)
            self.helper.layout.append(Div(HTML('<div class="card bg-light"><div class="card-body"><p>{}</p>{}</div></div><br>'.format(model.description, stats)), style="display:none", css_class="model_description", id="model_" + str(model.id)))

        self.helper.layout.append(Div('signature'))
        self.helper.add_input(Submit('save', 'Submit job'))
