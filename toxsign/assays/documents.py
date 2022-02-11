from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from toxsign.projects.models import Project
from toxsign.assays.models import Assay, Factor, ChemicalsubFactor
from toxsign.signatures.models import Signature

from elasticsearch_dsl import normalizer

lowercase = normalizer('my_analyzer',
    filter=['lowercase']
)

@registry.register_document
class AssayDocument(Document):

    project= fields.ObjectField(properties={
            'id': fields.TextField(),
            'status': fields.TextField()
    })

    created_by = fields.ObjectField(properties={
        'username': fields.TextField()
    })

    organism = fields.NestedField(properties={
        'name': fields.TextField()
    })

    tissue = fields.NestedField(properties={
        'name': fields.TextField()
    })

    cell = fields.NestedField(properties={
        'name': fields.TextField()
    })

    cell_line = fields.NestedField(properties={
        'name': fields.TextField()
    })

    cell_line_slug = fields.TextField()

    tsx_id = fields.KeywordField(normalizer=lowercase)

    class Index:
        # Name of the Elasticsearch index
        name = 'assays'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Assay # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'created_at',
            'sex_type',
            'dev_stage',
        ]
        related_models = [Project]
        ignore_signals = False

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(AssayDocument, self).get_queryset().select_related(
            'project',
            'created_by',
            'organism',
            'tissue',
            'cell',
            'cell_line',
        )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Project):
            return related_instance.assay_of.all()

@registry.register_document
class FactorDocument(Document):

    assay = fields.ObjectField(properties={
        'project': fields.ObjectField(properties={
            'id': fields.TextField(),
            'status': fields.TextField()
        })
    })

    created_by = fields.ObjectField(properties={
        'username': fields.TextField()
    })

    tsx_id = fields.KeywordField(normalizer=lowercase)

    class Index:
        # Name of the Elasticsearch index
        name = 'factors'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Factor # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'name',
            'created_at',
        ]
        related_models = [Assay]
        ignore_signals = False

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(FactorDocument, self).get_queryset().select_related(
            'assay__project',
            'created_by'
        )

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, Assay):
            return related_instance.factor_of.all()


@registry.register_document
class ChemicalsubFactorDocument(Document):

    factor = fields.ObjectField(properties={
        'id': fields.TextField()
    })

    chemical = fields.NestedField(properties={
        'id': fields.TextField(),
        'name': fields.TextField()
    })

    class Index:
        # Name of the Elasticsearch index
        name = 'biologicalsubfactors'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = ChemicalsubFactor # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'chemical_slug'
        ]

        related_models = [Factor]
        ignore_signals = False

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(ChemicalsubFactorDocument, self).get_queryset().select_related(
            'factor',
            'chemical'
        )
    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, ChemicalsubFactor):
            return related_instance.chemical_subfactor_of.all()
