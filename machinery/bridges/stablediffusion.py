from django.utils.translation import gettext as _

from machinery.pipelines.base import BasePipeline
from core.models import ChatSessionMessage
from lib.constants import KIND_TEXT, KIND_IMAGE


class BaseStableDiffusionPipeline(BasePipeline):

    MODEL = None
    INPUT = KIND_TEXT
    OUTPUT = KIND_IMAGE

    @classmethod
    def get_default_label(cls):
        return _('Generate image from text')

    @classmethod
    def get_default_description(cls):
        return _('Generate image from text using stable diffusion')

    @classmethod
    def get_title(cls, request_message: ChatSessionMessage, response_message: ChatSessionMessage) -> str:
        return _('Stable diffusion generation')

    def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage):

        self.send_log(_("Starting StableDiffusion"))
        """
        cleaned_data = self.chat_session.clean_data(self.pipeline, self.payload)
        if self.payload['files']:
            for file in self.payload['files']:
                cleaned_data['prompt'] += f"![image]({file['url']})"

        if (self.payload.get('prompt') and not self.payload['files']):
            msg = self.chat_session.save_session_message(self.pipeline, cleaned_data, 'user')
            self.send_message(msg)

        output = self.run_model(self.payload)

        self.send_title()

        run_result = self.get_run_result(output, msg_system)

        content = self.format_run_result(run_result)
        """
        # save "final" result :
        response_message.set_result('NOTE : BaseStableDiffusionPipeline process not implemented')
