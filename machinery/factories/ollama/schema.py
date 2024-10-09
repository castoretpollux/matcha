from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIInputField, UISelectField
from lib.llm import ALL_LLM


class OllamaFactorySchema(UISchemaBaseModel):
    model: str = UISelectField(label=_("Model"), options=ALL_LLM['ollama'], default=ALL_LLM['ollama'][0][0], required=True)(None)
    system: str = UIInputField(label=_("System prompt"), required=True)(None)

    @staticmethod
    def layout():
        return [
            ['model', 'system'],
        ]
