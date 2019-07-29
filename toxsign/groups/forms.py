from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from django.contrib.auth.models import Group
from toxsign.users.models import Notification

class GroupCreateForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super(GroupCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class GroupInvitationForm(forms.ModelForm):

    class Meta:
        model = Notification
        fields = ["user"]

    def __init__(self, *args, **kwargs):
        users = kwargs.pop('users', None)
        super(GroupInvitationForm, self).__init__( *args, **kwargs)
        if users:
            self.fields['user'].queryset = users
