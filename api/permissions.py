class PipelinePermission:

    @classmethod
    def _get_write_permission(cls, obj, user):
        group_can_write = obj.get('group') in user.groups.values_list('id', flat=True) and obj.get('group_rights').get('can_write')
        user_can_write = obj.get('user') == user.id and obj.get('user_rights').get('can_write')
        other_can_write = obj.get('other_rights').get('can_write')
        return group_can_write or user_can_write or other_can_write or user.is_superuser

    @classmethod
    def _get_read_permission(cls, obj, user):
        group_can_read = obj.get('group') in user.groups.values_list('id', flat=True) and obj.get('group_rights').get('can_read')
        user_can_read = obj.get('user') == user.id and obj.get('user_rights').get('can_read')
        other_can_read = obj.get('other_rights').get('can_read')
        return group_can_read or user_can_read or other_can_read or user.is_superuser

    @classmethod
    def _get_update_permission(cls, obj, user):
        group_can_update = obj.get('group') in user.groups.values_list('id', flat=True) and obj.get('group_rights').get('can_update')
        user_can_update = obj.get('user') == user.id and obj.get('user_rights').get('can_update')
        other_can_update = obj.get('other_rights').get('can_update')
        return group_can_update or user_can_update or other_can_update or user.is_superuser

    @classmethod
    def _get_delete_permission(cls, obj, user):
        group_can_delete = obj.get('group') in user.groups.values_list('id', flat=True) and obj.get('group_rights').get('can_delete')
        user_can_delete = obj.get('user') == user.id and obj.get('user_rights').get('can_delete')
        other_can_delete = obj.get('other_rights').get('can_delete')
        return group_can_delete or user_can_delete or other_can_delete or user.is_superuser
