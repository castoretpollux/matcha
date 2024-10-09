from typing import Any
from django.utils.translation import gettext as _
from pydantic import Field


# Base UI field
class UIField:
    def __init__(
            self,
            label: str = None,
            default: Any = None,
            placeholder: str = None,
            description: str = None,
            tooltip: str = None,
            max_length: int = None,
            min_length: int = None,
            field_type: str = 'string',
            ui_type: str = 'input',
            required: bool = False,
            options: list = None,
            rule: dict = None,
            editable: bool = False,
            ):
        """
        ```
        (!) Do not provide ui_type (!)
        ```
        """
        self.type = field_type
        self.required = required
        self.uitype = ui_type

        self.label = label
        self.default = default
        self.description = description
        self.placeholder = placeholder
        self.max_length = max_length
        self.min_length = min_length
        self.tooltip = tooltip
        self.options = options or []
        self.editable = editable

        self.has_media = False
        self.rule = rule.as_list() if rule else None

    def __call__(self, f=None):
        # Base metadata
        metadata = {
            'default': self.default or None,
            'required': self.required,
            'has_media': self.has_media,
            'editable': self.editable
        }

        # Return instance of pydantic field
        return Field(
            default_factory=self,
            extra=metadata,
            type=self.type or 'string',
            description=self.description
        )

    # Method to generate Field UI Schema
    def generate_field_ui_schema(self):
        return {
            "label": self.label,
            "default": self.default,
            "options": {
                "max_length": self.max_length,
                "min_length": self.min_length,
                "tooltip": self.tooltip,
                'required': self.required,
                'placeholder': self.placeholder,
                'uitype': self.uitype,
                'rule': self.rule,
                'editable': self.editable
            }
        }


class UIInputField(UIField):
    def __init__(self, variant: str = 'text', **kwargs):
        """
        ```
        variant: str:
            - text default
            - email
            - date
            - password
        **kwargs:
        label: str
        default: str
        description: str
        placeholder: str
        max_length (int)
        min_length: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(**kwargs)
        self.variant = variant

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options']['format'] = 'input'
        ui_schema['options']['type'] = self.variant
        return ui_schema


class UIFileField(UIField):
    def __init__(self, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: str
        description: str
        placeholder: str
        max_length (int)
        min_length: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(**kwargs)

    def generate_field_ui_schema(self):
        return ''


# Number field
class UINumberField(UIField):
    def __init__(self, minimum: int | float = None, maximum: int | float = None, step: int | float = None, is_integer: bool = True, slider: bool = False, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default (int/float)
        description: str
        placeholder: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(**kwargs)
        self.slider = slider
        self.min = minimum
        self.max = maximum
        self.step = step

        self.input_mode = 'decimal'
        self.type = 'number'

        if is_integer:
            if isinstance(self.step, float):
                raise ValueError(_('This field cannot be an integer and have a float step'))
            self.input_mode = 'numeric'

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({
            "min": self.min,
            "max": self.max,
            "step": self.step,
            "input_mode": self.input_mode,
            "format": 'numeric',
        })

        variant = 'slider' if self.slider else 'numeric'
        ui_schema['options']['variant'] = variant

        return ui_schema


# Textearea field
class UITextareaField(UIField):
    def __init__(self, rows: int = 1, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: str
        description: str
        placeholder: str
        max_length (int)
        min_length: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(ui_type='textarea', **kwargs)
        self.rows = rows

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({
            "rows": self.rows,
            "multi": True,
        })
        return ui_schema


# Checkbox field
class UICheckboxField(UIField):
    def __init__(self, toggle: bool = False, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: bool
        description: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(ui_type='checkbox', field_type='boolean', **kwargs)
        self.toggle = toggle

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options']['format'] = 'checkbox'
        if self.toggle:
            ui_schema['options'].update({
                'variant': 'toggle',
            })
        return ui_schema


# Date field
class UIDateField(UIField):
    def __init__(self, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default (???)
        description: str
        placeholder: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(**kwargs)

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({'format': 'date'})
        return ui_schema


# Radio field
class UIRadioField(UIField):
    def __init__(self, options=None, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: str = options value
        description: str
        placeholder: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(ui_type="radio", **kwargs)
        self.options = options or [('value', 'label')]
        if self.required and not self.default:
            raise ValueError(_('Cannot be required with no default value'))

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({'format': 'radio'})
        ui_schema['options']['enum'] = [{"value": value, "label": label} for value, label in self.options]
        return ui_schema


# Select field
class UISelectField(UIField):
    def __init__(self, options: list = None, has_media: bool = False, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: str = options value
        options: list = [('value', 'label'),]
        description: str
        placeholder: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(ui_type='select', **kwargs)
        self.options = options if options else []
        self.has_media = has_media

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({'format': 'select'})
        options = [{"value": value, "label": label} for value, label in self.options]

        ui_schema['options']['enum'] = options
        return ui_schema


# Multiple Choice field
class UIMultipleChoiceField(UIField):
    def __init__(self, options=None, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: str = options value
        description: str
        placeholder: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(ui_type="choice", **kwargs)
        self.options = options or ['option a', 'option b']

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({'format': 'multiple'})
        ui_schema['options']['enum'] = [value for value in self.options]
        return ui_schema


# Autocomplete field
class UIAutocompleteField(UIField):
    def __init__(self, options: list = None, options_api_url: str = None, options_api_params: dict = None, **kwargs):
        """
        ```
        **kwargs:
        label: str
        default: str = options value
        description: str
        placeholder: str
        tooltip: str
        required: bool
        ```
        """
        super().__init__(ui_type='autocomplete', **kwargs)
        self.options = options
        self.api_url = options_api_url
        self.api_params = options_api_params

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({'format': 'autocomplete'})

        options = self.options or []

        ui_schema['options']['api_url'] = self.api_url
        ui_schema['options']['api_params'] = self.api_params
        ui_schema['options']['enum'] = [{"value": option[1], "label": option[0]} for option in options]

        return ui_schema


# Multiple Choice field
class UIDynamicListField(UIField):
    def __init__(self, options: list = None, field_layout: list = None, **kwargs):
        # TODO: ADD CHECKBOX
        """
        ```
        **kwargs:
        label: str
        description: str
        placeholder: str
        tooltip: str
        required: bool
        options: list = [(key, value, input_type, size, required)]
        ```
        """
        super().__init__(ui_type="dynamiclist", **kwargs)
        self.options = options
        if not field_layout:
            self.field_layout = [[option[0] for option in self.options]]
        else:
            self.field_layout = field_layout

    def generate_field_ui_schema(self):
        ui_schema = super().generate_field_ui_schema()
        ui_schema['options'].update({'format': 'dynamiclist'})
        ui_schema['options']['enum'] = [option for option in self.options]
        ui_schema['options']['layout'] = self.field_layout
        return ui_schema
