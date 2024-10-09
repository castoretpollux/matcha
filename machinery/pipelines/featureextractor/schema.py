from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIInputField, UIFileField


class FeatureExtractorSchema(UISchemaBaseModel):
    prompt: str = UIInputField(label=_("Prompt"), required=True)(None)
    files: list = UIFileField(label=_("Files"), field_type='list', required=False)(None)
