from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIField


class PromptFileSchema(UISchemaBaseModel):
    prompt: str = UIField(label=_("Prompt"), placeholder=_("Check some uploaded files then type your prompt. It will be used for each file"), required=True)(None)
