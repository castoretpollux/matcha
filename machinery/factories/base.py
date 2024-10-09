from __future__ import annotations

from typing import Type

from django.utils.functional import classproperty

from machinery.common.schema import ModelSchema
from machinery.pipelines.base import BasePipeline
from machinery.exceptions import InformationNotDefined

import lib.uischema as lib_uischema


class BasePipelineFactory(object):

    ALIAS = None
    LABEL = None
    DESCRIPTION = None

    @classmethod
    def get_default_alias(cls) -> str:
        # override this method instead of overriding alias classproperty
        raise InformationNotDefined('%s ALIAS or get_default_alias must be defined' % (cls.__name__,))

    @classproperty
    def alias(cls) -> str:  # NOSONAR
        return getattr(cls, 'ALIAS') or cls.get_default_alias()

    @classmethod
    def get_default_label(cls) -> str:
        # override this method instead of overriding label classproperty
        raise InformationNotDefined('%s LABEL or get_default_label must be defined' % (cls.__name__,))

    @classproperty
    def label(cls) -> str:  # NOSONAR
        return cls.LABEL or cls.get_default_label()

    @classmethod
    def get_default_description(cls) -> str:
        return ''

    @classproperty
    def description(cls) -> str:  # NOSONAR
        return cls.DESCRIPTION or cls.get_default_description()

    @classproperty
    def pydantic_model(cls) -> Type[lib_uischema.UISchemaBaseModel]:
        """
        Must return a UISchemaBaseModel (which is a pydantic model with additionnal stuff to be able to generate UI Schema)
        Here, there is a simple implementation that will fit most of pipelines
        """
        return ModelSchema

    @classproperty
    def json_schema(cls) -> dict:
        return cls.pydantic_model.model_json_schema()

    @classproperty
    def ui_schema(cls) -> dict:
        return cls.pydantic_model.model_ui_schema()

    @classmethod
    def produce(cls, **kwargs) -> Type[BasePipeline]:
        "This must be overridden"
        raise NotImplementedError

    @classmethod
    def populate(cls, *args, **kwargs) -> tuple[dict, dict]:
        """
        Mainly for a dynamic pipeline\n
        The first dict returned is to add or update parameters in the pipeline parameters attribute\n
        The second dict returned is to update the pipeline attributes, such as ready or active.
        """
        return {}, {}
