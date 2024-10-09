import logging
import requests

from django.conf import settings
from django.template.loader import render_to_string
from django.template import Template
from django.utils.translation import gettext as _

from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin
from machinery.pipelines.base import BasePipeline

from core.models import ChatSessionMessage
from lib.app_requests import SearchRequest
from lib.constants import RENDERER_HTML

logger = logging.getLogger("django")


class ReferenceSearchPipeline(BasePipeline, LlmTitleGeneratorMixin):

    MODEL = None  # must be defined within factory
    NAMESPACE = None  # ditto
    TEMPLATE = 'searchresult.html'
    TEMPLATE_STRING = None

    @classmethod
    def get_default_label(cls):
        class_label = getattr(cls, 'LABEL')
        if class_label:
            return class_label
        label_tpl = _('Search %s')
        return label_tpl % (cls.NAMESPACE,)

    @classmethod
    def get_default_description(cls):
        description_tpl = _('This pipeline will search documents or texts from %s namespace')
        return description_tpl % (cls.NAMESPACE,)

    @classmethod
    def get_title(cls, request_message: ChatSessionMessage, response_message: ChatSessionMessage) -> str:
        user_prompt = request_message.data.get('prompt', None)
        prompt_format = _("Define a title for this message, only give the title without comments or explanations : user message : {user_prompt}")
        title = cls.generate_title(prompt_format.format(user_prompt=user_prompt))
        pretitle = _('%s search') % (cls.NAMESPACE,)
        return _('%s : %s') % (pretitle, title)

    def search_related_documents(self, data: dict) -> list[dict]:
        payload = {
            "query": data['prompt'],
            "namespace": self.NAMESPACE,
        }
        sr = SearchRequest(self.session.user)
        output = sr.post("/api/search/", json=payload)
        output_json = output.json()
        return output_json['results']

    @classmethod
    def format_response(cls, response_message: ChatSessionMessage) -> str:
        # logger.info("In format_response")
        context = response_message.data
        if cls.TEMPLATE_STRING is not None:
            template = Template(cls.TEMPLATE_STRING)
            content = template.render(context)
        else:
            template = cls.TEMPLATE
            content = render_to_string(template, context)
        return content

    def preprocess(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
        response_message.data = {'documents': []}
        response_message.renderer = RENDERER_HTML

    def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
        self.send_log(_("Using RAG"))
        data = request_message.data
        documents = self.search_related_documents(data)
        # directly defining data instead of calling set_result :
        response_message.data = {'documents': documents}
        response_message.renderer = RENDERER_HTML
