import logging

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _

from pydantic import ValidationError

from lib.auth import login_and_get_token
from .schema import LoginPayload

logger = logging.getLogger("django")


@csrf_exempt  # NOSONAR
def login(request):  # NOSONAR
    token = None
    if request.method == 'POST':
        try:
            payload = request.body
            data = LoginPayload.model_validate_json(payload)
            namespace = data.namespace
            user = {
                "id": data.user_id,
                "username": data.user_name,
                "is_superuser": data.is_superuser,
                "is_staff": data.is_staff,
            }
            group_mapping = data.group_mapping
            token = login_and_get_token(request, namespace, user, group_mapping)

        except ValidationError as e:
            logger.info(str(e))

    return JsonResponse({'csrftoken': token})
