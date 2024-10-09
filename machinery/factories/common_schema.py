from django.utils.translation import gettext as _

from lib.uischema import UISchemaBaseModel
from lib.uifields import UIInputField, UICheckboxField, UITextareaField, UISelectField
from lib.constants import KIND_CHOICES
from lib.uirule import Clause, Exact, In, Property, Value


class BaseFactorySchema(UISchemaBaseModel):
    label: str = UIInputField(label=_('label'), placeholder=_('label of your pipeline'), required=True)(None)
    description: str = UITextareaField(
        label=_('description'),
        placeholder=_('description of your pipeline'),
        rows=3,
        required=False,
        rule=(
            Clause(Exact('auto_generate_description', False), Property('required', True)) &
            Clause(Exact('auto_generate_description', True), Property('disabled', True)) &
            Clause(Exact('auto_generate_description', True), Value('description', ''))
        ),
    )(None)
    auto_generate_description: bool = UICheckboxField(label=_('generate description'), required=False, default=False, toggle=True)(None)
    generate_media: bool = UICheckboxField(label=_('Generate Media ?'), required=False, default=False, toggle=True)(None)
    input: str = UISelectField(label=_("Input kind"), options=KIND_CHOICES)(None)
    output: str = UISelectField(label=_("Output kind"), options=KIND_CHOICES)(None)

    @staticmethod
    def layout():
        return [
            ['label',],
            ['input', 'output'],
            ['description', 'auto_generate_description'],
        ]
