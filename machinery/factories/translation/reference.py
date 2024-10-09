import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template
from django.utils.translation import gettext as _
from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin

import requests

from core.models import ChatSessionMessage
from machinery.bridges.ollama import OllamaPipeline
from lib.constants import RENDERER_HTML
from lib.constants import LANGUAGE_TO_LABEL, LANGUAGE_ENGLISH

logger = logging.getLogger("django")


class ReferenceTranslationPipeline(OllamaPipeline, LlmTitleGeneratorMixin):

    MODEL = None  # must be defined within factory
    LANGUAGE = None  # ditto

    @classmethod
    def get_language_label(cls):
        language_key = getattr(cls, 'LANGUAGE')
        return LANGUAGE_TO_LABEL.get(language_key, LANGUAGE_ENGLISH)

    @classmethod
    def get_default_label(cls):
        language_label = cls.get_language_label()
        label_tpl = _('%s Translation')
        return label_tpl % (language_label,)

    @classmethod
    def get_default_description(cls):
        language_label = cls.get_language_label()
        description_tpl = _('This pipeline will translate texts to %s')
        return description_tpl % (language_label,)

    @classmethod
    def get_title(cls, request_message: ChatSessionMessage, response_message: ChatSessionMessage) -> str:
        user_prompt = request_message.data.get('prompt', None)
        prompt_format = _("Define a title for this message, only give the title without comments or explanations : user message : {user_prompt}")
        title = cls.generate_title(prompt_format.format(user_prompt=user_prompt))
        language_label = cls.get_language_label()
        pretitle = _('%s translation') % (language_label,)
        return f'{pretitle}: {title}'

    def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
        language_label = self.get_language_label()
        self.send_log(_("Starting translation to %s") % (language_label,))
        data = request_message.data
        user_prompt = data.get('prompt')
        final_prompt_tpl = _("""Please translate this text to {language_label}. Do not add a title nor introduction nor explanations, only provide the translation. Here is the text to translate :
        {user_prompt}
        """)
        final_prompt = final_prompt_tpl.format(user_prompt=user_prompt, language_label=language_label)
        output = self.client.generate(self.MODEL, final_prompt, stream=True)
        self.send_log(_('Extracting results'))
        results = []
        for item in output:
            content = item['response']
            results.append(content)
            raw_content = ''.join(results)
            response_message.data['result'] = raw_content
            self.send_partial(response_message.as_dict())
        # NOTE : No need to set result at the end, the last loop does this
