from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.assays.models import Assay, Factor, ChemicalsubFactor

class AssayAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': [
            'name',
            'created_by',
            'additional_info',
            'experimental_design',
            'dev_stage',
            'generation', 
            'sex_type',
            'exp_type',
            'project',
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
            'assay'
        ]}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

class  ChemicalsubFactorAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': [
            'created_by',
            'factor',
            'chemical',
            'chemical_slug',
            'route',
            'vehicule',
            'dose_value',
            'dose_unit',
            'exposure_time',
            'exposure_frequencie',
            'additional_info',
        ]}),
    ]
    list_display = ['created_at', 'updated_at']

admin.site.register(Assay, AssayAdmin)
admin.site.register(Factor, FactorAdmin)
admin.site.register(ChemicalsubFactor, ChemicalsubFactorAdmin)

