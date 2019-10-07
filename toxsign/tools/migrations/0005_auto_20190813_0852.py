# Generated by Django 2.0.13 on 2019-08-13 08:52

from django.db import migrations
from django.core.files import File
from toxsign.tools.models import Category, Tag, Tool
from datetime import datetime

# Populate with default tools (ontologies..)

def populate_default_tools(apps, schema_editor):
    search_category = Category(name='Search tools', description='Tools used to search through entities on this website')
    search_category.save()

    search_tag = Tag(word='Search', slug='search', created_at=datetime.now())
    search_tag.save()

    onto_search_tool = Tool(
        name = 'Browse ontologies',
        type = "LOCAL",
        category = search_category,
        short_description = "Get information about ontologies (name, id, synonyms)",
        description = "TOXsIgN also includes a tool to browse the ontologies used in the resource to describe data. This feature is especially relevant for filling the excel template required when submitting a novel signature.",
        status = "DEVELOPPMENT",
        link = "ontologies:search",
    )
    onto_search_tool.icon.save("Ontology.svg", File(open("/app/loading_data/images/Ontology.svg", "rb")), save=True)
    onto_search_tool.visuel.save("Ontology.svg", File(open("/app/loading_data/images/Ontology.svg", "rb")), save=True)
    onto_search_tool.save()
    onto_search_tool.tags.add(search_tag)
    onto_search_tool.save()

    advanced_search_tool = Tool(
        name = 'Advanced search',
        type = "LOCAL",
        category = search_category,
        short_description = "Search entities using multiple fields such as names, descriptions, ontologies..",
        description = "The search engine supports complex fielded queries to retrieve signatures and associated data based on various information such as experimental parameters, observed toxicological effects and/or up/down-regulated gene lists. This module is especially powerfull for identifying comparable experiments (i.e. performed on similar models and/or with close environmental factors) and/or similar outcomes (i.e. close physiological, molecular and/or omics effects).",
        status = "DEVELOPPMENT",
        link = "advanced_search",
    )

    advanced_search_tool.icon.save("advanced_search.jpg", File(open("/app/loading_data/images/advanced_search.jpg", "rb")), save=True)
    advanced_search_tool.visuel.save("advanced_search.jpg", File(open("/app/loading_data/images/advanced_search.jpg", "rb")), save=True)
    advanced_search_tool.save()
    advanced_search_tool.tags.add(search_tag)
    advanced_search_tool.save()



class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0004_auto_20190812_1432'),
    ]

    operations = [
        migrations.RunPython(populate_default_tools),
    ]
