from __future__ import annotations
import logging

from django.utils.translation import gettext as _
from django.utils.functional import classproperty
from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template

import requests

from core import models as core_models
from machinery.pipelines.base import BasePipeline
from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin
from lib.constants import KIND_AUDIO, KIND_TEXT
from lib.constants import RENDERER_HTML

logger = logging.getLogger("django")


class WhisperPipeline(BasePipeline, LlmTitleGeneratorMixin):

    INPUT = KIND_AUDIO
    OUTPUT = KIND_TEXT
    TEMPLATE = 'whisperresult.html'
    TEMPLATE_STRING = None
    LABEL = _("Speech to text transcription")

    @classmethod
    def get_title(cls, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> str:
        # contrary to most Pipelines, the text is contained in the result instead of request
        # so let's use the result text
        result = response_message.data['result']
        if len(result):
            text = result[0]['text']
            prompt_format = _("The following is a text transcription of an audio file, generate a title for this transcription : {text}")
            title = cls.generate_title(prompt_format.format(text=text))
        else:
            title = _("Audio to text transcription")
        return title

    @classmethod
    def format_request(cls, request_message: core_models.ChatSessionMessage) -> str:
        return _('<Audio file text transcription>')

    @classmethod
    def format_response(cls, response_message: core_models.ChatSessionMessage) -> str:
        # preparing context :
        context = {
            'site_root': settings.SITE_ROOT
        }
        items = []
        result = response_message.data['result']
        for item in result:
            file_id = item['file_id']
            file: core_models.ChatSessionFile = core_models.ChatSessionFile.objects.filter(id=file_id).first()
            if file is not None:
                text = item['text']
                items.append({
                    'url': file.file.url,
                    'transcript': text
                })
        context['items'] = items
        # rendering the context :
        if cls.TEMPLATE_STRING is not None:
            template = Template(cls.TEMPLATE_STRING)
            content = template.render(context)
        else:
            template = cls.TEMPLATE
            content = render_to_string(template, context)
        return content

    def preprocess(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage):
        response_message.data = {'result': []}
        response_message.renderer = RENDERER_HTML

    def process(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        session_files = core_models.ChatSessionFile.objects.filter(session=self.session, favorite=True)
        outputs = []
        for session_file in session_files:
            payload = {
                "audio": session_file.file.path,
            }
            output = requests.post(settings.WHISPER_BACKEND_URL + "/transcript", json=payload)
            json_output = output.json()
            outputs.append({
                'file_id': str(session_file.id),
                'text': json_output['text']
            })
        response_message.data['result'] = outputs
