from django.contrib import admin
from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps

class GeneAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['gene_id','tax_id','symbol','synonyms','description','homolog_id','ensemble_id'
                                        ]
                             }
        ),
    ]
    search_fields = ['symbol']
    list_display = ['symbol', 'gene_id']


admin.site.register(Gene, GeneAdmin)



