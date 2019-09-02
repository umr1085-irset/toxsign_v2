from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from toxsign.assays.models import Factor
from toxsign.signatures.models import Signature
from toxsign.ontologies.models import *

@registry.register_document
class SignatureDocument(Document):

    factor = fields.ObjectField(properties={
        'assay': fields.ObjectField(properties={
            'study': fields.ObjectField(properties={
                'project': fields.ObjectField(properties={
                    'id': fields.TextField()
                })
            })
        })
    })

    created_by = fields.ObjectField(properties={
        'username': fields.TextField()
    })

    disease = fields.NestedField(properties={
        'id': fields.TextField(),
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'signatures'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Signature # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'created_at',
            'tsx_id',
        ]
        related_models = [Factor, Disease]
        ignore_signals = False

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(SignatureDocument, self).get_queryset().select_related(
            'factor'
        )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Factor):
            return related_instance.signature_of_of.all()
