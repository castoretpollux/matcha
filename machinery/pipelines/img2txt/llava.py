from __future__ import annotations
import logging

from django.utils.translation import gettext as _
from django.utils.functional import classproperty


from machinery.bridges.ollama import OllamaPipeline
from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin
from core import models as core_models
from lib.constants import KIND_IMAGE, KIND_TEXT
from lib.constants import MESSAGE_KIND_REQUEST, MESSAGE_KIND_RESPONSE

logger = logging.getLogger("django")


class LlavaPipeline(OllamaPipeline, LlmTitleGeneratorMixin):

    MODEL = "llava:7b"
    LABEL = _("Ask questions on images")
    DESCRIPTION = _("After uploading and checking some images, you can run text prompts on them, such as asking a description of those images")
    GENERATE_MEDIA = False
    INPUT = KIND_IMAGE
    OUTPUT = KIND_TEXT

    @classmethod
    def get_title(cls, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> str:
        user_prompt = request_message.data.get('prompt', None)
        prompt_format = _("Define a title for our chat, only give the title without comments or explanations : user message : {user_prompt}")
        title = cls.generate_title(prompt_format.format(user_prompt=user_prompt))
        result = _("Image description")
        return f'{result}: {title}'

    def process(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        user_prompt = request_message.data['prompt']
        session_files = core_models.ChatSessionFile.objects.filter(session=self.session, favorite=True)
        images = [session_file.file.path for session_file in session_files]
        payload = {
            'model': self.MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': user_prompt,
                    'images': images
                }
            ]
        }
        output = self.client.chat(**payload)
        response_message.data['result'] = output['message']['content']

