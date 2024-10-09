from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.functional import classproperty

from core.models import ChatSessionMessage
from machinery.pipelines.base import BasePipeline
from .schema import StableDiffusionSchema

from lib.utils import save_image_from_base64
from lib.constants import KIND_IMAGE, KIND_TEXT_AND_IMAGE

import requests


class StableDiffusionXLPipeline(BasePipeline):

    OUTPUT = KIND_IMAGE
    INPUT = KIND_TEXT_AND_IMAGE

    def __init__(self, session):
        super(StableDiffusionXLPipeline, self).__init__(session)

    @classproperty
    def pydantic_model(cls):
        return StableDiffusionSchema

    @classproperty
    def label(cls):
        return _("Generate image with Stable Diffusion XL")

    @classmethod
    def format_file_result(cls, urls):
        fragments = []
        for url in urls:
            fragments.append(f'![generatedfile]({settings.SITE_ROOT}{url})\n')
        content = ''.join(fragments)
        return content

    def run_model(self, payload):
        if settings.SDXL_BACKEND_URL is None:
            self.send_error('SDXL process has not been defined in config.yaml')
        new_payload = payload.copy()
        for key, value in payload.items():
            if value in [None, '']:
                del new_payload[key]

        output = requests.post(settings.SDXL_BACKEND_URL + "/process", json=new_payload)
        return output.json()
    
    def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
        self.send_log("Lancement de l'IA")
        self.send_log('Extraction des résultats')

        output = self.run_model(request_message.data)

        urls = []

        for img_base64_string in output['images']:
            urls.append(save_image_from_base64(img_base64_string))

        result = self.format_file_result(urls)
        response_message.data['result'] = result
