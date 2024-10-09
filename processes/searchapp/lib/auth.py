from django.http import HttpRequest
from django.middleware.csrf import get_token


ROOT_USER_ID = 0
ROOT_GROUP_ID = 0


def get_root_user():
    from core.models import ExternalUser
    root_user = ExternalUser.objects.get(uid=ROOT_USER_ID)
    return root_user


def get_root_group():
    from core.models import ExternalGroup
    root_group = ExternalGroup.objects.get(gid=ROOT_GROUP_ID)
    return root_group


def get_user(user_id):
    from core.models import ExternalUser
    user = ExternalUser.objects.get(uid=user_id)
    return user


def login_and_get_token(request: HttpRequest, namespace: str, user: dict, group_mapping: dict):
    # Note : searchapp is a companion process of matcha
    # it is aimed to be used for its api, there's no frontend that allow user to log in
    # (and furthermore ExternalUser is not classical django User, it's just a practical local representation of an other-proces user)
    # so this method's name is a bit abusive...
    from core.models import ExternalUser, ExternalGroup, GroupUser  # avoid circular imports

    gid_to_group = {}

    # Syncing external users
    external_user, _ = ExternalUser.objects.get_or_create(uid=user['id'], namespace=namespace)
    if external_user.username != user['username']:
        external_user.username = user['username']
        external_user.is_superuser = user['is_superuser']
        external_user.is_staff = user['is_staff']
        external_user.save()

    # Syncing external groups and user's groups
    current_user_group_ids = set([group_user.group.gid for group_user in GroupUser.objects.filter(user=external_user)])
    wanted_user_group_ids = []
    for group_id, group_name in group_mapping.items():
        wanted_user_group_ids.append(group_id)
        external_group, _ = ExternalGroup.objects.get_or_create(gid=group_id, namespace=namespace)
        gid_to_group[group_id] = external_group
        if external_group.groupname != group_name:
            external_group.groupname = group_name
            external_group.save()
    wanted_user_group_ids = set(wanted_user_group_ids)

    # Comparing current and wanted to update GroupUser entries :
    to_add_ids = wanted_user_group_ids - current_user_group_ids
    to_remove_ids = current_user_group_ids - wanted_user_group_ids
    if to_add_ids:
        to_add_group_users = []
        for group_id in to_add_ids:
            group = gid_to_group[group_id]
            group_user = GroupUser(user=external_user, group=group)
            to_add_group_users.append(group_user)
        GroupUser.objects.bulk_create(to_add_group_users)
    if to_remove_ids:
        GroupUser.objects.filter(user=external_user, group__id__in=to_remove_ids).delete()

    # Finally, create a csrf token and returns it :
    return get_token(request)
