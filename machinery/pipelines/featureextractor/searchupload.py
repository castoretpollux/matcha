import os

from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.functional import classproperty

import requests

from ollama import Client

from core.models import ChatSessionMessage, ChatSessionFile

from machinery.pipelines.base import BasePipeline
from machinery.mixins.llm_title_generator import LlmTitleGeneratorMixin
from machinery.exceptions import UploadFailedException, SearchFailedException

from lib.config import get_config
from lib.app_requests import SearchRequest
from .schema import FeatureExtractorSchema

config = get_config()


class SearchUploadPipeline(BasePipeline, LlmTitleGeneratorMixin):

    LLM_MODEL = config.pipelines.core.searchupload.settings.model

    def __init__(self, session):
        super(SearchUploadPipeline, self).__init__(session)
        self.client = Client(host=settings.OLLAMA_BACKEND_URL)

    @classproperty
    def pydantic_model(cls):
        return FeatureExtractorSchema

    @classproperty
    def label(cls):
        return _("Extract features from documents")

    @classmethod
    def get_default_description(cls):
        return _("This helps to answers questions and extract informations after selecting some uploaded documents")

    @classmethod
    def get_title(cls, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
        user_prompt = request_message.data.get('prompt', None)
        prompt_format = _("Define a title for our chat, only give the title without comments or explanations : user message : {user_prompt}")
        title = cls.generate_title(prompt_format.format(user_prompt=user_prompt))
        result = _("Informations extraction")
        return f'{result}: {title}'

    def vectorize_document(self, file):
        file_path = os.path.join(settings.BASE_DIR, file['url'])
        # remove /media from url
        file_path = file_path.replace('/media', str(settings.MEDIA_ROOT))
        files_payload = {
            "file": open(file_path, 'rb')
        }
        data_payload = {
            "path": f"ROOT/SEARCH/MATCHA/{self.channel_id}",
            "title": file['name'],
        }
        sr = SearchRequest(self.session.user)
        output = sr.post("/api/document/", files=files_payload, data=data_payload)

        # Check if the request was successful
        if output.status_code != 200:
            raise UploadFailedException("Upload failed" + output.text)
        ChatSessionFile.objects.filter(id=file['id']).update(vectorized=True)

    def vectorize_documents(self, payload):
        for i, file in enumerate(payload['files']):
            session_file = ChatSessionFile.objects.get(id=file['id'])
            payload['files'][i]['vectorized'] = session_file.vectorized
        for file in payload['files']:
            if not file['vectorized'] and file['selected']:
                self.vectorize_document(file)

    def search_parts(self, payload):
        new_payload = {
            "query": payload['prompt'],
            "namespace": f"ROOT/SEARCH/MATCHA/{self.channel_id}",
        }
        sr = SearchRequest(self.session.user)
        output = sr.post("/api/search_parts/", json=new_payload)
        json_output = output.json()
        return json_output['results']

    def run_ollama(self, prompt: str):
        messages = [{'role': 'user', 'content': prompt}]
        # request to ollama API
        output = self.client.chat(model=self.LLM_MODEL, messages=messages, stream=True)
        return output

    def run_model(self, data):
        self.vectorize_documents(data)
        output = self.search_parts(data)
        prompt = data["prompt"]
        # create a prompt for the ia
        ollama_prompt = ''
        ollama_prompt += _('With following data : {output}').format(output=output)
        ollama_prompt += _('Answer the following question: {prompt}').format(prompt=prompt)
        ollama_prompt += ''
        output = self.run_ollama(ollama_prompt)
        return output

    def process(self, request_message: ChatSessionMessage, response_message: ChatSessionMessage):
        self.send_log(_("Executing AI with SearchWithUpload"))
        output = self.run_model(request_message.data)
        self.send_log(_('Extracting results'))
        # output is iterable and asychronous, let's do iterate over it
        # and send "notifications" after each iteration
        results = []
        raw_content = ''
        for result in output:
            results.append(result['message']['content'])
            raw_content = ''.join(results)
            # send msg from template
            # FIXME : send_partial should send a serialized message
            self.send_partial(raw_content)
        # save "final" result :
        response_message.data['result'] = raw_content
        response_message.save()
        # response_message.set_result(raw_content)
