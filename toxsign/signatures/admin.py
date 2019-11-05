from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.signatures.models import Signature
class SignatureAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 
        'created_by',
        'signature_type',
        'phenotype_description',
        'experimental_design',
        'dev_stage',
        'generation',
        'sex_type',
        'exp_type',
        'factor',
        'organism',
        'tissue',
        'cell',
        'cell_line',
        'chemical',
        'chemical_slug',
        'disease',
        'technology',
        'technology_slug',
        'platform',
        'control_sample_number',
        'treated_sample_number',
        'pvalue',
        'cutoff',
        'statistical_processing',
        'up_gene_file_path',
        'up_gene_number',
        'down_gene_file_path',
        'down_gene_number',
        'interrogated_gene_file_path',
        'interrogated_gene_number',
        'additional_file_path',
        'gene_id',
        'expression_values',
        'expression_values_file',
    ]}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    autocomplete_fields = ['disease','organism','cell', 'tissue', 'cell', 'cell_line', 'technology', 'chemical']
    search_fields = ['name']

admin.site.register(Signature, SignatureAdmin)
