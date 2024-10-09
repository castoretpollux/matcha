from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIInputField


class PromptSchema(UISchemaBaseModel):
    prompt: str = UIInputField(label=_("Prompt"), required=True)(None)


class ModelSchema(UISchemaBaseModel):
    model: str = UIInputField(label=_("LLM Model"), required=True)(None)
