from typing import Type
from django.utils.translation import gettext as _

from django.utils.functional import classproperty
from machinery.factories.base import BasePipelineFactory
from machinery.factories.search.reference import ReferenceSearchPipeline

from .schema import SearchFactorySchema


class SearchFactory(BasePipelineFactory):

    @classproperty
    def pydantic_model(cls):
        return SearchFactorySchema

    @classmethod
    def get_default_label(cls):
        return _("Create a search pipeline")

    @classmethod
    def get_default_description(cls):
        return _("Allows to create pipeline that will help to search documents within a given namespace")

    @classmethod
    def produce(cls, **kwargs) -> Type[ReferenceSearchPipeline]:
        model = kwargs.get('model', None)
        namespace = kwargs['namespace']
        capitalized_namespace = namespace.capitalize()
        new_class_name = f'Search{capitalized_namespace}Pipeline'
        return type(new_class_name, (ReferenceSearchPipeline,), {
            'MODEL': model,
            'NAMESPACE': namespace
        })
