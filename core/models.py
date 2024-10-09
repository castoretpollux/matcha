from __future__ import annotations
import uuid
from typing import Type

import pytz
import os

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.utils.translation import gettext as _

import django_rq
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pydantic import ValidationError

from lib.utils import get_upload_path
from lib.constants import KIND_CHOICES, MESSAGE_KIND_CHOICES
from lib.constants import MESSAGE_KIND_REQUEST, MESSAGE_KIND_RESPONSE
from lib.constants import RENDERER_MARKDOWN
from machinery.exceptions import ChannelNotConnectedException
from machinery.router import get_pipeline_class, get_pipeline_aliases
from machinery.mixins import ChannelMixin
from machinery.router import get_factory_class


import machinery.pipelines.base as pipelines_base

TIMEZONE = pytz.timezone('Europe/Paris')
FRENCH_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def inline_schedule_call(session_id, payload):
    session = ChatSession.objects.get(id=session_id)
    session.channel_layer = get_channel_layer()
    session.connected = True
    session.schedule_call(payload)


class ChatSession(models.Model, ChannelMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255, null=True, blank=True) # NOSONAR

    def __init__(self, *args, **kwargs):
        super(ChatSession, self).__init__(*args, **kwargs)
        self.pipeline_cache = {}
        self.connected = False
        self.channel_id = self.compute_channel_id()

    def compute_channel_id(self):
        return str(self.id).replace('-', '_')

    @property
    def has_messages(self):
        pipeline_aliases = get_pipeline_aliases(self.user)
        return ChatSessionMessage.objects.filter(pipeline__in=pipeline_aliases, session=self).exists()

    @property
    def files(self) -> list[ChatSessionFile]:
        files = ChatSessionFile.objects.filter(session=self)
        file_list = [file.as_dict() for file in files]
        return file_list

    @property
    def session_id(self):
        return str(self.id)

    @property
    def session_title(self):
        return self.title or ''

    def _connect_channel(self):
        # it is strongly recommended not to override this function
        self.channel_layer = get_channel_layer()
        self.connected = True

    def _send_msg(self, msg):
        # it is strongly recommended not to override this function
        if self.connected:
            async_to_sync(self.channel_layer.group_send)(self.channel_id, msg)
        else:
            raise ChannelNotConnectedException

    @classmethod
    def from_channel_id(cls, channel_id):
        real_id = channel_id.replace('_', '-')
        return cls.objects.filter(id=real_id).first()

    def process(self, payload):
        if not self.connected:
            self._connect_channel()
        django_rq.enqueue(inline_schedule_call, str(self.id), payload)

    def schedule_call(self, payload: dict):
        pipeline_alias = payload['pipeline']
        pipeline = self.get_pipeline(pipeline_alias)
        # get and clean data :
        data = self.clean_payload(pipeline_alias, payload['payload'])
        if data is not None:
            # create a ChatSessionMessage with cleaned_data and files :
            request_message = ChatSessionMessage(
                session=self,
                pipeline=pipeline_alias,
                data=data,
                kind=MESSAGE_KIND_REQUEST
            )
            request_message.save()

            # returns, thru channel, a formatted version of this message
            self.send_message(request_message.as_dict())

            # Prepare a message for response :
            response_message = ChatSessionMessage(
                session=self,
                pipeline=pipeline_alias,
                data={},
                status='started',
                kind=MESSAGE_KIND_RESPONSE
            )
            # preprocess message :
            pipeline.preprocess(request_message, response_message)
            response_message.save()

            # send a partial for the front to know that processing will start so that
            # it can start displaying a block with content for the result
            self.send_partial(response_message.as_dict())

            # now, ask pipeline to process the request message and update "periodically" the response message :
            pipeline._start_processing(request_message, response_message)
            response_message.status = 'ended'
            response_message.save()
            self.send_message(response_message.as_dict())
            self.send_result(_("End processing"))

            # postprocess message
            pipeline.postprocess(request_message, response_message)
            response_message.save()

            # if current session has no title, let's ask current pipeline to generate one
            if not self.title:
                self.title = pipeline.get_title(request_message, response_message)
                self.send_title()
                self.save()
        # else:
        #     There is nothing to do : clean_data method already sent feedback to user

    # PIPELINE FUNCTIONS

    def get_pipeline_class(self, pipeline_alias) -> Type[pipelines_base.BasePipeline]:
        result = self.pipeline_cache.get(pipeline_alias, None)
        if result:
            return result
        result = get_pipeline_class(pipeline_alias, self.user)
        self.pipeline_cache[pipeline_alias] = result
        return result

    def get_pipeline(self, pipeline_alias) -> pipelines_base.BasePipeline:
        pipeline_class = self.get_pipeline_class(pipeline_alias)
        return pipeline_class(session=self)

    def clean_payload(self, pipeline_alias, payload):
        pipeline_class = self.get_pipeline_class(pipeline_alias)
        pydantic_model = pipeline_class.pydantic_model
        try:
            obj = pydantic_model(**payload)
        except ValidationError as e:
            errors = [(item['loc'][0], item['msg']) for item in e.errors()]
            self.send_error(errors)
            return None
        return obj.model_dump()

    # MESSAGES
    # NOTE : HISTORY
    def serialize_messages(self):
        pipeline_aliases = get_pipeline_aliases(self.user)
        session_messages = ChatSessionMessage.objects.filter(pipeline__in=pipeline_aliases, session=self).order_by('created_on')
        history = []
        for session_message in session_messages:
            serialized_message = session_message.as_dict()
            if serialized_message is not None:
                history.append(serialized_message)
        return history


class ChatSessionMessage(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    pipeline = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    created_on = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=255, null=True, blank=True, default='')  # NOSONAR
    valid = models.BooleanField(null=True, blank=True)
    selected = models.BooleanField(default=True, null=False, blank=False)
    kind = models.CharField(choices=MESSAGE_KIND_CHOICES)
    renderer = models.CharField(max_length=255, null=False, blank=False, default=RENDERER_MARKDOWN)

    @property
    def files(self):
        message_files = self.message_files
        return [mf.file for mf in message_files]

    @property
    def pipeline_class(self):
        return get_pipeline_class(self.pipeline, self.session.user)

    def files_as_dict(self):
        files = self.files
        return [{'id': file.id, 'name': file.file.name} for file in files]

    def as_dict(self):
        return {
            "id": str(self.id),
            "session_id": str(self.session.id),
            "channel_id": str(self.session.compute_channel_id()),
            "created_on": self.created_on.astimezone(settings.TIMEZONE).strftime(settings.DATETIME_FORMAT),
            "kind": self.kind,
            "username": self.session.user.username,
            "content": self.render(),
            "pipeline": self.pipeline,
            "pipeline_label": self.pipeline_class.label,
            "status": self.status,
            "valid": self.valid,
            "selected": self.selected,
            "renderer": self.renderer,
            "is_prompt": self.prompts.exists(),
            # "files": self.files_as_dict()
        }

    def render(self):
        from machinery.router import get_pipeline_class
        pipeline_class = get_pipeline_class(self.pipeline, self.session.user)
        kind = self.kind
        if pipeline_class is not None:
            format_method = getattr(pipeline_class, f'format_{kind}')
            return format_method(self)
        return None

    def set_result(self, content: str) -> None:
        self.data.update({'result': content})

    def set_renderer(self, renderer: str) -> None:
        self.renderer = renderer


class ChatSessionFile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_upload_path)
    name = models.CharField(max_length=255)
    favorite = models.BooleanField(default=False, null=True, blank=True)
    vectorized = models.BooleanField(default=False)

    def as_dict(self):
        return {
            'id': self.id,
            'session_id': self.session.id,
            'name': self.name,
            'url': self.file.url,
            'favorite': self.favorite,
            'vectorized': self.vectorized
        }

    def delete_file(self):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)


class ChatSessionMessageFile(models.Model):
    # This model helps to track which file have been used by a message at a time
    # NOTE : on_delete is OBLIGATORY, related_name caused error
    file = models.ForeignKey(ChatSessionFile, on_delete=models.DO_NOTHING)
    message = models.ForeignKey(ChatSessionMessage, on_delete=models.DO_NOTHING)


class UserPrompt(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    preference = models.ForeignKey('UserPreference', related_name="prompts", on_delete=models.CASCADE)
    content = models.TextField(default='', null=True, blank=True)  # NOSONAR
    # Chat session message id if the prompt is linked to a chat session message
    message = models.ForeignKey('ChatSessionMessage', related_name="prompts", on_delete=models.CASCADE, null=True)

    def as_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'message': self.message.as_dict() if self.message else None
        }


class UserPreference(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, related_name="preferences", on_delete=models.CASCADE)

    def as_dict(self):
        prompts = UserPrompt.objects.filter(preference=self.id)
        return {
            'prompts': [prompt.as_dict() for prompt in prompts]
        }


class UserToken(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    namespace = models.CharField(max_length=255, null=False)
    alias = models.CharField(max_length=32, null=False)
    token = models.CharField(max_length=255, null=False)
    expires_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "namespace", "alias"], name="unique_user_namespace_alias"
            )
        ]


class DynamicPipeline(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)  # NOSONAR
    generate_media = models.BooleanField(default=False)
    input = models.CharField(max_length=255, choices=KIND_CHOICES)
    output = models.CharField(max_length=255, choices=KIND_CHOICES)
    factory = models.CharField(max_length=255)
    params = models.JSONField(default=dict)
    active = models.BooleanField(default=True)
    ready = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name="dynamic_pipelines", on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, related_name="dynamic_pipelines", on_delete=models.CASCADE, null=True)
    user_can_read = models.BooleanField(default=False)
    user_can_write = models.BooleanField(default=False)
    user_can_update = models.BooleanField(default=False)
    user_can_delete = models.BooleanField(default=False)
    group_can_read = models.BooleanField(default=False)
    group_can_write = models.BooleanField(default=False)
    group_can_update = models.BooleanField(default=False)
    group_can_delete = models.BooleanField(default=False)
    other_can_read = models.BooleanField(default=False)
    other_can_write = models.BooleanField(default=False)
    other_can_update = models.BooleanField(default=False)
    other_can_delete = models.BooleanField(default=False)

    @property
    def normalized_id(self):
        return str(self.id).replace('-', '_')

    @property
    def alias(self):
        return f'dynamic.{self.normalized_id}'

    @property
    def group_rights(self):
        return {
            'can_write': self.group_can_write,
            'can_read': self.group_can_read,
            'can_update': self.group_can_update,
            'can_delete': self.group_can_delete,
        }

    @property
    def user_rights(self):
        return {
            'can_write': self.user_can_write,
            'can_read': self.user_can_read,
            'can_update': self.user_can_update,
            'can_delete': self.user_can_delete,
        }

    @property
    def other_rights(self):
        return {
            'can_write': self.other_can_write,
            'can_read': self.other_can_read,
            'can_update': self.other_can_update,
            'can_delete': self.other_can_delete,
        }

    @classmethod
    def from_alias(cls, alias):
        denormalized_id = alias.replace('dynamic.', '').replace('_', '-')
        return cls.objects.get(id=denormalized_id)

    def as_dict(self):
        user_id = group_id = None
        if self.user:
            user_id = self.user.id
        if self.group:
            group_id = self.group.id
        return {
            "id": self.id,
            "label": self.label,
            "alias": self.alias,
            "params": self.params,
            "ready": self.ready,
            "active": self.active,
            'user': user_id,
            'group': group_id,
            'user_rights': self.user_rights,
            'group_rights': self.group_rights,
            'other_rights': self.other_rights,
        }

    @property
    def pipeline_class(self):
        factory_class = get_factory_class(self.factory)
        editable = any(factory_class.ui_schema["editable_elements"].values())
        cls = factory_class.produce(**self.params)
        normalized_id = self.normalized_id
        cls.ALIAS = f'dynamic.{normalized_id}'
        cls.LABEL = self.label
        cls.DESCRIPTION = self.description
        cls.GENERATE_MEDIA = self.generate_media
        cls.INPUT = self.input
        cls.OUTPUT = self.output
        cls.READY = self.ready
        cls.ACTIVE = self.active
        cls.USER = self.user.id if self.user else None
        cls.GROUP = self.group.id if self.group else None
        cls.USER_RIGHTS = self.user_rights
        cls.GROUP_RIGHTS = self.group_rights
        cls.OTHER_RIGHTS = self.other_rights
        cls.FACTORY = self.factory
        cls.EDITABLE = editable
        return cls
