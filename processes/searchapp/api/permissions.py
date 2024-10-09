class Permission:

    @classmethod
    def _get_write_permission(cls, obj, user):
        return user.is_superuser or \
        (obj.user_can_write and obj.user == user) or \
        (obj.group_can_write and obj.group in user.groups) or \
        obj.other_can_write

    @classmethod
    def _get_read_permission(cls, obj, user):
        return user.is_superuser or \
        (obj.user_can_read and obj.user == user) or \
        (obj.group_can_read and obj.group in user.groups) or \
        obj.other_can_read

    @classmethod
    def _get_update_permission(cls, obj, user):
        return user.is_superuser or \
        (obj.user_can_update and obj.user == user) or \
        (obj.group_can_update and obj.group in user.groups) or \
        obj.other_can_update

    @classmethod
    def _get_delete_permission(cls, obj, user):
        return user.is_superuser or \
        (obj.user_can_delete and obj.user == user) or \
        (obj.group_can_delete and obj.group in user.groups) or \
        obj.other_can_delete
