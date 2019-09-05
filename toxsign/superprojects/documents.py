from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from toxsign.superprojects.models import Superproject

@registry.register_document
class SuperprojectDocument(Document):

    tsx_id = fields.KeywordField()

    created_by = fields.ObjectField(properties={
        'username': fields.TextField()
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'superprojects'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Superproject # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'created_at',
            'description',
        ]

        ignore_signals = False
