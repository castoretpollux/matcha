from django.utils.translation import gettext as _
from django.conf import settings

from lib.constants import LANGUAGE_CHOICES, LANGUAGE_ENGLISH
from lib.uischema import UISchemaBaseModel
from lib.uifields import UISelectField
from lib.llm import ALL_LLM


class TranslationFactorySchema(UISchemaBaseModel):

    model: str = UISelectField(label=_("Translation Model"), options=ALL_LLM['ollama'], default=ALL_LLM['ollama'][0][0], required=True)(None)
    language: str = UISelectField(label=_("Language"), options=LANGUAGE_CHOICES, default=LANGUAGE_ENGLISH, required=True)(None)

    @staticmethod
    def layout():
        return [
            ['model', 'language']
        ]
