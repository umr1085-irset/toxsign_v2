from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.assays.models import Assay, Factor
class AssayAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': [
            'name', 
            'created_by', 
            'status', 
            'additional_info', 
            'experimental_design', 
            'dev_stage',
            'generation', 
            'sex_type', 
            'exp_type', 
            'study', 
            'organism', 
            'tissue', 
            'cell', 
            'cell_line'
        ]}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

class FactorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': [
            'name', 
            'created_by', 
            'chemical', 
            'chemical_slug', 
            'factor_type', 
            'route',
            'vehicule', 
            'dose_value', 
            'dose_unit', 
            'exposure_time', 
            'exposure_frequencie', 
            'additional_info',
            'assay' 
        ]}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

admin.site.register(Assay, AssayAdmin)
admin.site.register(Factor, FactorAdmin)
