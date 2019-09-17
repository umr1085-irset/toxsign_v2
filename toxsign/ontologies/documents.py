from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from toxsign.ontologies.models import *

@registry.register_document
class BiologicalDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'biologicals'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Biological # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]


@registry.register_document
class CellLineDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'celllines'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = CellLine # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]


@registry.register_document
class CellDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'cells'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Cell # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]


@registry.register_document
class ChemicalDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'chemicals'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Chemical # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]


@registry.register_document
class DiseaseDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'diseases'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Disease # The model associated with this Document
        related_models = [Disease]
        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]

@registry.register_document
class ExperimentDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'experiments'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Experiment # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]

@registry.register_document
class SpeciesDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'species'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Species # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]


@registry.register_document
class TissueDocument(Document):

    onto_id = fields.KeywordField()

    class Index:
        # Name of the Elasticsearch index
        name = 'tissues'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Tissue # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'synonyms',
            'as_children',
        ]
