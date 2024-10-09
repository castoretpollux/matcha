from __future__ import annotations

from typing import Type

from django.utils.translation import gettext as _
from django.utils.functional import classproperty
from django.conf import settings

import ollama

from machinery.common.schema import PromptSchema
from machinery.mixins import ChannelMixin
from machinery.exceptions import InformationNotDefined

import core.models as core_models
import lib.uischema as lib_uischema
from lib.constants import KIND_TEXT, MESSAGE_KIND_TO_LABEL, MESSAGE_KIND_ERROR


class BasePipeline(ChannelMixin):

    ALIAS = None
    LABEL = None
    DESCRIPTION = None
    GENERATE_MEDIA = False  # useful default value
    INPUT = KIND_TEXT  # useful default value
    OUTPUT = KIND_TEXT  # useful default value
    ACTIVE = True
    READY = True
    EDITABLE = False

    USER = None
    GROUP = None
    BASE_RIGHTS = {
        'can_create': False,
        'can_read': False,
        'can_update': False,
        'can_delete': False,
    }
    USER_RIGHTS = BASE_RIGHTS
    GROUP_RIGHTS = BASE_RIGHTS
    OTHER_RIGHTS = BASE_RIGHTS

    def __init__(self, session: core_models.ChatSession):
        self.session: core_models.ChatSession = session
        self.channel_id = session.channel_id

    # Please don't override methods starting with _

    def _start_processing(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        # it is strongly recommended not to override this function
        try:
            self.process(request_message, response_message)
        except Exception as e:
            self.send_error(str(e))

            response_message.data['error'] = str(e)
            response_message.kind = MESSAGE_KIND_ERROR
            response_message.save()

            self.send_message(response_message.as_dict())

    def _send_msg(self, msg):
        # it is strongly recommended not to override this function
        self.session._send_msg(msg)

    @classmethod
    def get_default_alias(cls) -> str:
        # override this method instead of overriding alias classproperty
        raise InformationNotDefined('%s ALIAS or get_default_alias must be defined' % (cls.__name__,))

    @property
    def session_id(self):
        return self.session.session_id

    @property
    def session_title(self):
        return self.session.session_title

    @classproperty
    def alias(cls) -> str:  # NOSONAR
        # don't override this "method"
        return cls.ALIAS or cls.get_default_alias()

    @classproperty
    def editable(cls) -> bool:  # NOSONAR
        return cls.EDITABLE

    @classmethod
    def get_default_label(cls) -> str:
        # override this method instead of overriding label classproperty
        raise InformationNotDefined('%s LABEL or get_default_label must be defined' % (cls.__name__,))

    @classproperty
    def label(cls) -> str:  # NOSONAR
        # don't override this "method"
        return cls.LABEL or cls.get_default_label()

    @classmethod
    def get_default_description(cls) -> str:
        # override this method instead of overriding description classproperty
        return ''

    @classproperty
    def description(cls) -> str:  # NOSONAR
        # don't override this "method"
        return cls.DESCRIPTION or cls.get_default_description()

    @classmethod
    def generate_description(cls) -> str:
        # override this method instead of overriding description classproperty
        prompt_preformat = '''
        Generate a short description based on the label : "{label}" and the model name: "{model}".
        Also takes into consideration input type: "{input}" and the output type: "{output}".
        Only give the description without comments or explanations.
        '''
        prompt_format = _(prompt_preformat)
        prompt = prompt_format.format(label=cls.label, model=cls.MODEL, input=cls.input, output=cls.output)
        result = ollama.Client(host=settings.OLLAMA_BACKEND_URL).generate(model=settings.SMALL_LLM, prompt=prompt)
        return result['response']

    @classmethod
    def get_default_generate_media(cls) -> bool:
        return False

    @classproperty
    def generate_media(cls) -> bool:  # NOSONAR
        # don't override this "method"
        return cls.GENERATE_MEDIA or cls.get_default_generate_media()

    @classmethod
    def get_default_input(cls) -> str:
        # override this method instead of overriding input classproperty
        return KIND_TEXT

    @classproperty
    def input(cls) -> str:  # NOSONAR
        # don't override this "method"
        return cls.INPUT or cls.get_default_input()

    @classmethod
    def get_default_output(cls) -> str:
        # override this method instead of overriding output classproperty
        return KIND_TEXT

    @classproperty
    def output(cls) -> str:  # NOSONAR
        # don't override this "method"
        return cls.OUTPUT or cls.get_default_output()

    @classproperty
    def pydantic_model(cls) -> Type[lib_uischema.UISchemaBaseModel]:
        """
        Must return a UISchemaBaseModel (which is a pydantic model with additionnal stuff to be able to generate UI Schema)
        Here, there is a simple implementation that will fit most of pipelines
        as it is the classical prompt form everyone is familiar with....
        """
        return PromptSchema

    @classproperty
    def json_schema(cls) -> dict:
        return cls.pydantic_model.model_json_schema()

    @classproperty
    def ui_schema(cls) -> dict:
        return cls.pydantic_model.model_ui_schema()

    @classmethod
    def get_title(cls, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> str:
        """
        if a pipeline is the 1st to be used within a session
        it will have the opportunity to infer the title for the whole session
        whatever comes after...

        default implementation below is an incentive to define this method in inherited classes :p
        """
        cls_name = cls.__name__
        title = _("%s must override a get_title method") % (cls_name,)
        return title

    @classmethod
    def format_request(cls, request_message: core_models.ChatSessionMessage) -> str:
        # Generates content from a request session message
        # 
        # Simple implementation suitable for most cases :
        return request_message.data.get('prompt', '')

    @classmethod
    def format_response(cls, response_message: core_models.ChatSessionMessage) -> str:
        # Generates content from a response session message
        #
        # Simple implementation suitable for most cases :
        return response_message.data.get('result', '')

    @classmethod
    def format_error(cls, error_message: core_models.ChatSessionMessage) -> str:
        # Generates content from a error session message
        #
        # Simple implementation suitable for most cases :
        return error_message.data.get('error', '')

    @classmethod
    def format_media(cls, session_message: core_models.ChatSessionMessage) -> str:
        # Use to generate content from either a saved or realtime media
        # This must be overridden"
        raise NotImplementedError

    # most important methods :

    def preprocess(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        # This is a "hook" to change response_message before process method is called
        # main use is to change response_message renderer
        pass

    def process(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        # This must be implemented by classes that inherits from BasePipeline
        # The goal of this method is to use informations in request_message
        # to do what needs to be done to :
        # - update response_message
        # - possibly send feedbacks to frontend user by using the send_* methods (coming from ChannelMixin)
        #   note : feedbacks are particularly welcomed where result generation is iterative (which is the case, for instance, for most LLMs)
        raise NotImplementedError

    def postprocess(self, request_message: core_models.ChatSessionMessage, response_message: core_models.ChatSessionMessage) -> None:
        # This is a "hook" to change response_message after process is called
        pass
