from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.ontologies.models import Biological, Cell, CellLine, Chemical, Disease, Experiment, Species, Tissue

class OntoAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'onto_id', 'synonyms', 'as_children']}),
    ]
    list_display = ['name', 'onto_id']
    search_fields = ['name', 'onto_id']

admin.site.register(Biological, OntoAdmin)
admin.site.register(Cell, OntoAdmin)
admin.site.register(CellLine, OntoAdmin)
admin.site.register(Chemical, OntoAdmin)
admin.site.register(Disease, OntoAdmin)
admin.site.register(Experiment, OntoAdmin)
admin.site.register(Species, OntoAdmin)
admin.site.register(Tissue, OntoAdmin)

