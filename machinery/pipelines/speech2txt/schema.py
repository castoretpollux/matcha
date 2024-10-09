from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIField


class PromptFileSchema(UISchemaBaseModel):
    prompt: str = UIField(label=_("Prompt"), required=True)(None)
    files: str = UIField(label=_("Files"), required=True)(None)
