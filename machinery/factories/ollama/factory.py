from django.utils.translation import gettext as _
from django.utils.functional import classproperty

from machinery.bridges.ollama import OllamaPipeline
from machinery.factories.base import BasePipelineFactory
from core.models import ChatSessionMessage
from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin

from .schema import OllamaFactorySchema
from lib.constants import MESSAGE_KIND_REQUEST, MESSAGE_KIND_RESPONSE
import logging

logger = logging.getLogger('django')


class OllamaRunnerFactory(BasePipelineFactory):

    @classproperty
    def pydantic_model(cls):
        """
        Must return a UISchemaBaseModel (which is a pydantic model with additionnal stuff to be able to generate UI Schema)
        Here, there is a simple implementation that will fit most of pipelines
        """
        return OllamaFactorySchema

    class InnerRunner(OllamaPipeline, LlmTitleGeneratorMixin):

        # Example "meta" properties
        # MODEL = 'starling-lm'
        # SYSTEM = _("You're a nice assistant and you have to answer in English.")

        @classmethod
        def get_title(cls, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
            user_prompt = request_message.data['prompt']
            assistant_response = response_message.data['result']
            prompt_format = _("Define a title for our chat, only give the title without comments or explanations : user message : {user_prompt}. your answer:  {assistant_response}")
            new_prompt = prompt_format.format(user_prompt=user_prompt, assistant_response=assistant_response)
            return cls.generate_title(new_prompt)

        def build_ollama_history(self, history):
            ollama_history = []
            for message in history:
                if message.get('selected'):
                    kind = message.get('kind')
                    if kind == MESSAGE_KIND_REQUEST:
                        ollama_history.append({'role': 'user', 'content': message.get('content')})
                    elif kind == MESSAGE_KIND_RESPONSE:
                        ollama_history.append({'role': 'system', 'content': message.get('content')})
            return ollama_history

        def remove_empty_system_messages(self, ollama_history):
            i = 0
            while i < len(ollama_history):
                if ollama_history[i]['content'] == '' and ollama_history[i]['role'] == 'system':
                    ollama_history.pop(i)
                    if i > 0 and ollama_history[i-1]['role'] == 'user':
                        ollama_history.pop(i-1)
                        i -= 1
                else:
                    i += 1
            return ollama_history

        def get_formated_history(self):
            history = self.session.serialize_messages()
            logger.info(f"History: {history}")
            history = history[:-1]

            ollama_history = self.build_ollama_history(history)
            ollama_history = self.remove_empty_system_messages(ollama_history)

            return ollama_history

        def run_model(self):
            history = self.get_formated_history()
            messages = []
            messages.append({'role': 'system', 'content': self.SYSTEM})
            messages += history
            return self.client.chat(model=self.MODEL, messages=messages, stream=True)

        def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage) -> None:
            output = self.run_model()
            results = []
            raw_content = ''
            self.send_log('Extraction des résultats')

            for result in output:
                results.append(result['message']['content'])
                raw_content = ''.join(results)
                response_message.data['result'] = raw_content
                self.send_partial(response_message.as_dict())

            # NOTE : No need to set result at the end, the last loop does this

    @classmethod
    def produce(cls, **kwargs):
        model = kwargs['model']
        system = kwargs['system']
        name = f'ollama_{model}'
        kls = type(name, (cls.InnerRunner,), {
            'MODEL': model,
            'SYSTEM': system
        })
        return kls
