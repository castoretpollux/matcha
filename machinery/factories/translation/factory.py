from typing import Type
from django.utils.translation import gettext as _

from django.utils.functional import classproperty
from machinery.factories.base import BasePipelineFactory
from machinery.factories.translation.reference import ReferenceTranslationPipeline

from .schema import TranslationFactorySchema


class TranslationFactory(BasePipelineFactory):

    @classproperty
    def pydantic_model(cls):
        return TranslationFactorySchema

    @classmethod
    def get_default_label(cls):
        return _("Translate a text")

    @classmethod
    def get_default_description(cls):
        return _("Translate a text using a neural network")

    @classmethod
    def produce(cls, **kwargs) -> Type[ReferenceTranslationPipeline]:
        model = kwargs.get('model', None)
        language = kwargs.get('language', None)
        capitalized_language = language.capitalize()
        new_class_name = f'Translate{capitalized_language}Pipeline'
        return type(new_class_name, (ReferenceTranslationPipeline,), {
            'MODEL': model,
            'LANGUAGE': language
        })
