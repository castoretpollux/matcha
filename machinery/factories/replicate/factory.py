from django.utils.translation import gettext as _
from django.utils.functional import classproperty

from django.conf import settings

from .schema import ReplicateFactorySchema
from machinery.bridges.replicate import ReplicatePipeline
from machinery.factories.base import BasePipelineFactory
from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin


from core.models import ChatSessionMessage

from lib.utils import download_url
import lib.constants as lib_constants

import logging
logger = logging.getLogger('django')


class ReplicateRunnerFactory(BasePipelineFactory):

    @classproperty
    def pydantic_model(cls):
        return ReplicateFactorySchema

    class InnerRunner(ReplicatePipeline, LlmTitleGeneratorMixin):

        @classmethod
        def get_title(cls, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
            user_prompt = request_message.data.get('prompt', None)
            if not user_prompt:
                user_prompt = request_message.data.get('text', '')

            prompt_format = _("Define a title for our chat, only give the title without comments or explanations : user message : {user_prompt}")

            title = cls.generate_title(prompt_format.format(user_prompt=user_prompt))
            return title

        @classmethod
        def format_file_result(cls, urls):
            fragments = []
            for url in urls:
                fragments.append(f'![generatedfile]({settings.SITE_ROOT}{url})\n')
            content = ''.join(fragments)
            return content

        def run_model(self, payload):
            args = [self.model_version]

            new_payload = payload.copy()
            for key, value in payload.items():
                if not value:
                    del new_payload[key]

            kwargs = {'input': new_payload}
            output = self.replicate.run(*args, **kwargs)
            return output

        def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage) -> None:
            msg_tpl = _('Using %s model on replicate')
            self.send_log(msg_tpl % (self.model_version,))
            self.send_log(_('Extracting results'))

            output = self.run_model(request_message.data)

            result = ''
            urls = []

            if self.generated_output == lib_constants.KIND_FILE:
                if isinstance(output, dict):
                    urls = [download_url(value) for value in output.values()]
                else:
                    urls = [download_url(output)]
                result = self.format_file_result(urls)

            elif self.generated_output == lib_constants.KIND_FILE_LIST:
                for item in output:
                    url = download_url(item)
                    urls.append(url)
                result = self.format_file_result(urls)

            else:
                result = output

            response_message.data['result'] = result
            self.send_partial(response_message.as_dict())

    @classmethod
    def produce(cls, **kwargs):
        model = kwargs['model']
        version = kwargs['version']
        title_llm = kwargs['title_llm']
        name = f'replicate_{model}'
        kls = type(name, (cls.InnerRunner,), {
            'MODEL': model,
            'VERSION': version,
            'TITLE_LLM': title_llm
        })
        kls.get_replicate_datas()
        return kls
