import bson
from users import get_owner
from toxsign.projects.models import Project

def process_projects(path, user_dict):
    # Load project file

    with open(path,'rb') as f:
        data = bson.decode_all(f.read())

    treated_number = 1
    fake_projects = 0
    project_list = []
    for project in data:
        id = int(project['id'].split("TSP")[-1])
        while not id == treated_number:
            project_list.append(_create_empty_project("TSP" + str(treated_number), user_dict))
            fake_projects += 1
            treated_number +=1

        project_list.append(_create_project(project, user_dict))
        treated_number +=1

    if not (treated_number -1) == (len(data) + fake_projects):
        print(fake_projects)
        print(treated_number)
        print(len(data))
        raise Exception("Missing!")

    # Bulk create
    Project.objects.bulk_create(project_list)
    _cleanup()

def get_project_dict():
    dict = {}
    for project in Project.objects.all():
        dict[project.tsx_id] = project
    return dict

def _cleanup():
    Project.objects.filter(name='temp_project_delete_me').delete()

def _create_empty_project(project_id, user_dict):
    return Project(**{'tsx_id': project_id, 'created_by': user_dict['admin'],'name': 'temp_project_delete_me', 'status': 'PRIVATE'})

def _create_project(project_data, user_dict):

    owner = get_owner(project_data['owner'], user_dict)

    project_dict = {
        'name': project_data['title'],
        'tsx_id':  project_data['id'],
        'created_by': owner,
        'description': project_data['description'],
        'pubmed_id': project_data['pubmed'],
        'cross_link': project_data['cross_link'],
        'project_type': 'INTERVENTIONAL',
    }

    project = Project(**project_dict)

    return project
