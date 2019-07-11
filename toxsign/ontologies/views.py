from dal import autocomplete
from django.db.models import Q
from toxsign.ontologies.models import Disease

class DiseaseAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):

        if not self.request.user.is_authenticated():
                    return Disease.objects.none()

        qs = Disease.objects.all()
        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q))

        return qs
