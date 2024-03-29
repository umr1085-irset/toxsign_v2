# Generated by Django 2.0.13 on 2019-09-13 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontologies', '0005_auto_20190529_1039'),
    ]


    operations = []
    for ontology in ['biological', 'cellline', 'cell', 'chemical', 'disease', 'experiment', 'species', 'tissue']:
        operations += [
            migrations.RemoveField(
                model_name=ontology,
                name='as_ancestor',
            ),
            migrations.AddField(
                model_name=ontology,
                name='as_children',
                field=models.TextField(blank=True, default='', verbose_name='Children'),
            ),
            migrations.RemoveField(
                model_name=ontology,
                name='name',
            ),
            migrations.AddField(
                model_name=ontology,
                name='name',
                field=models.TextField(verbose_name='Ontology name'),
            ),
            migrations.RemoveField(
                model_name=ontology,
                name='as_parent',
            )
        ]

