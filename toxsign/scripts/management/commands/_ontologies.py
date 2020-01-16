import toxsign.ontologies.models as onto

def get_ontology(model_name, value_dict, field_name, onto_dict):

    exceptions = {
        "Tissue": {
            "T lymphocyte": None,
            "Hippocampus": "layer of hippocampus",
            "Whole body": "body proper",
            "HEPARG": None,
            "PURIFIED SPLENIC CD8 T CELLS": None,
            "PRIMARY_HEPATOCYTE": None
        },
        "CellLine": {
            "Hepatocytes": None,
            "T-lymphocyte": "T cell",
            "MCF-7 cell": "MCF7 cell"
        },
        "Cell": {
            "Hepatocytes": "Hepatocyte",
        }
    }

    if not model_name in onto_dict:
        onto_dict[model_name] = {}
    val = None
    onto_name = value_dict.get(field_name)

    if onto_name and model_name in exceptions and onto_name in exceptions[model_name]:
        # Manage exceptions
        onto_name = exceptions[model_name][onto_name]
    if onto_name:
        model = getattr(onto, model_name)
        if onto_name in onto_dict[model_name]:
            val = onto_dict[model_name][onto_name]
        else:
            res = model.objects.filter(name__iexact=onto_name)
            if res.count():
                val = res[0]
                onto_dict[model_name][onto_name] = val
            else:
                onto_dict[model_name][onto_name] = None
                print(onto_name + " ontology not found in model " + model_name)
    return val, onto_dict

def get_ontology_slug(model_name, value_dict, field_name, slug_name, onto_dict, filter=None):

    exceptions = {
        "CellLine": {
            "Hepatocytes": None,
            "T-lymphocyte": "T cell",
            "MCF-7 cell": "MCF7 cell"
        },
        "Cell": {
            "Hepatocytes": "Hepatocyte",
        },
        "Experiment":   {
            "Microarray": "array",
            "microarray platform": "array"
        },
        "Chemical": {
            "wy-14643 CAS:NA": "pirinixic acid CAS:NA",
            "Vomitoxin CAS:51481-10-8": "deoxynivalenol CAS:51481-10-8"
        }
    }

    if not model_name in onto_dict:
        onto_dict[model_name] = {}

    val = None

    onto_name = value_dict.get(field_name)
    slug = value_dict.get(slug_name, "")

    if onto_name and model_name in exceptions and onto_name in exceptions[model_name]:
        # Manage exceptions
        onto_name = exceptions[model_name][onto_name]

    if onto_name:
        slug = onto_name
        if filter:
            onto_name = onto_name.split(filter)[0].rstrip()
        if onto_name in onto_dict[model_name]:
            val = onto_dict[model_name][onto_name]
        else:
            model = getattr(onto, model_name)
            res = model.objects.filter(name__iexact=onto_name)
            if res.count():
                onto_dict[model_name][onto_name] = res[0]
                val = res[0]
            else:
                print(onto_name + " ontology not found in model " + model_name)
                onto_dict[model_name][onto_name] = None
                val = None

    return val, slug, onto_dict
