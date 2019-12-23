import bson
from toxsign.users.models import User

def process_users(path, admin_mail, admin_password):

    user_dict = {}

    with open(path,'rb') as f:
        data = bson.decode_all(f.read())
    for user in data:
        new_user = _create_user(user)
        user_dict[user['id']] = new_user

    new_admin =_create_super_user(admin_mail, admin_password)
    user_dict['admin'] = new_admin.id

    return user_dict

def get_user_dict():
    dict = {}
    users = User.objects.all()
    for user in users:
        dict[user.username] = user
    return dict

def get_owner(current_owner, user_dict):
    if current_owner not in user_dict:
        return user_dict['admin']
    else:
        return user_dict[current_owner]

def _create_user(data):
    user_dict = {
        'username': data['id'],
        'email': data['id'],
    }
    if 'first_name' in data:
        user_dict['name'] = data['first_name']
    if 'last_name' in data:
        user_dict['last_name'] = data['last_name']
    if 'laboratory' in data:
        user_dict['institut'] = data['laboratory']

    user = User.objects.create_user(**user_dict)
    return user


def _create_super_user(admin_mail, admin_password):
    user = User.objects.create_superuser(username='admin', email=admin_mail, password=admin_password)
    return user
