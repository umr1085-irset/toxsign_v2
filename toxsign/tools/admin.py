from django.contrib import admin
from django import forms
from .models import Tool, Tag, ArgumentType
import toxsign.tools.forms as tool_forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps



class AdminForm(forms.ModelForm):

    class Meta:
        model = Tool
        fields = ['name', 'form_name', 'html_name', 'created_by', 'short_description', 'description', 'path', 'script_name', 'command_line', 'status', 'visuel', 'tags']

    def is_valid(self):
        valid = super(AdminForm, self).is_valid()
        if not valid:
            return valid
        form_function = getattr(tool_forms, self.cleaned_data['form_name'], False)
        if not form_function:
            self.add_error("form_name", ValidationError(_('No form called {} was found. Check if it is present in tools/forms.py'.format(self.cleaned_data['form_name']))))
            return False
        return True

class ArgumentTypeAdminForm(forms.ModelForm):

    TYPE_CHOICES = (('Text', 'Text'), ('Signature', 'Signature'),)

    type = forms.ChoiceField(choices = TYPE_CHOICES, label="Argument type", initial='Text', widget=forms.Select(), required=True)

    class Meta:
        model = ArgumentType
        fields = ['type']

    def __init__(self, *args, **kwargs):
        super(ArgumentTypeAdminForm, self).__init__(*args, **kwargs)
        choices = self.fields['type'].choices
        app_models = apps.get_app_config('ontologies').get_models()
        for model in app_models:
            choices += ((model.__name__, model.__name__),)

        self.fields['type'].choices = choices

class ArgumentTypeAdmin(admin.ModelAdmin):
    model = ArgumentType
    form = ArgumentTypeAdminForm

class ArgumentsAdmin(admin.TabularInline):
    model = Tool.argument_types.through

# Register your models here.
class ToolsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name']
    inlines = [ArgumentsAdmin,]
    form = AdminForm

admin.site.register(Tool, ToolsAdmin)
admin.site.register(Tag)
admin.site.register(ArgumentType, ArgumentTypeAdmin)



