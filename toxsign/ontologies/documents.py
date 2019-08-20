from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from toxsign.ontologies.models import *

@registry.register_document
class BiologicalDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

    def get_queryset(self):
        return super(BiologicalDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Biological):
            return related_instance.as_grandson

@registry.register_document
class CellLineDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

@registry.register_document
class CellLineDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]


    def get_queryset(self):
        return super(CellLineDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, CellLine):
            return related_instance.as_grandson

@registry.register_document
class CellDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

         

    def get_queryset(self):
        return super(CellDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Cell):
            return related_instance.as_grandson

@registry.register_document
class ChemicalDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

         

    def get_queryset(self):
        return super(ChemicalDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Chemical):
            return related_instance.as_grandson

@registry.register_document
class DiseaseDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

         

    def get_queryset(self):
        return super(DiseaseDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Disease):
            return related_instance.as_grandson

@registry.register_document
class ExperimentDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

         

    def get_queryset(self):
        return super(ExperimentDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Experiment):
            return related_instance.as_grandson

@registry.register_document
class SpeciesDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

         

    def get_queryset(self):
        return super(SpeciesDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Species):
            return related_instance.as_grandson

@registry.register_document
class TissueDocument(Document):

    as_ancestor = fields.NestedField(properties={
        'name': fields.TextField(),
        'synonyms': fields.TextField()
    })

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
            'onto_id',
        ]

         

    def get_queryset(self):
        return super(TissueDocument, self).get_queryset().prefetch_related(
            'as_ancestor'
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Tissue):
            return related_instance.as_grandson
