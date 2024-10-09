from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIInputField, UISelectField
from lib.llm import ALL_LLM


class ReplicateFactorySchema(UISchemaBaseModel):
    model: str = UIInputField(label=_("Replicate model"), required=True)(None)
    version: str = UIInputField(label=_("Model version"), required=True)(None)
    title_llm: str = UISelectField(label=_("Title generation model"), options=ALL_LLM['ollama'], default=ALL_LLM['ollama'][0][0], required=True)(None)

    @staticmethod
    def layout():
        return [
            ['model', 'version'],
            ['title_llm'],
        ]
