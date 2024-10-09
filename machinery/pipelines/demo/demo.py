from __future__ import annotations
import logging

from django.utils.translation import gettext as _
from django.utils.functional import classproperty
from django.conf import settings


from machinery.pipelines.base import BasePipeline
from core import models as core_models
from lib.constants import KIND_TEXT, RENDERER_HTML

logger = logging.getLogger("django")

class EchoPipeline(BasePipeline):

    LABEL = _("Echo pipeline")
    DESCRIPTION = _("Returns the message sent by the user")
    GENERATE_MEDIA = False
    INPUT = KIND_TEXT
    OUTPUT = KIND_TEXT

    @classmethod
    def get_title(cls, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> str:
        title = _("Echo")
        return title

    def process(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        user_prompt = request_message.data['prompt']
        result = user_prompt
        response_message.data['result'] = result

