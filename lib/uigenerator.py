from django.conf import settings
from django.utils.translation import gettext as _
from django.core.cache import caches

from typing import Any, Optional, List, Dict, Any
from pydantic import create_model, Field

import logging
logger = logging.getLogger("django")

from lib.constants import (
    KIND_TEXT,
    KIND_IMAGE,
    KIND_TEXT_AND_IMAGE,
    KIND_AUDIO,
    KIND_SOUND,
    KIND_MUSIC,
    KIND_FILE,
    KIND_FILE_LIST,
)
from lib.uischema import UISchemaBaseModel
from lib.uifields import (
    UIInputField,
    UINumberField,
    UISelectField,
    UICheckboxField,
    UIFileField,
    UITextareaField
)

import requests

cache = caches['djangocache']


class ReplicateModelGenerator():

    TYPE_TO_FIELD = {
        "*": (UIInputField, str),
        "uri": (UIFileField, str),
        "string": (UIInputField, str),
        "textarea": (UITextareaField, str),
        "integer": (UINumberField, int),
        "number": (UINumberField, float),
        "boolean": (UICheckboxField, bool),
        "allOf": (UISelectField, Any),
    }

    UNWANTED_PROPERTIES = [
        'title',
        'prompt',
        'type',
        'x-order',
        'format',
        'allOf'
    ]

    def __init__(self):
        self.MODEL = None
        self.replicate_schema = None
        self.replicate_output = None
        self.replicate_properties = None
        self.replicate_field_required = None

    @classmethod
    def get_replicate_datas(cls, model, version):
        # Replicate API Url
        url = f"https://api.replicate.com/v1/models/{model}/versions/{version}"
        headers = {
            "Authorization": f"Token {settings.REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            cls.replicate_schema = data.get("openapi_schema", {}).get("components", {}).get("schemas", {})
            cls.replicate_properties = cls.replicate_schema.get("Input", {}).get('properties', {})
            cls.replicate_output = cls.replicate_schema.get('Output', {})

            model_formated = model.replace('/', '_').replace('-', '_')

            cls.MODEL = model
            replicate_input = cls.get_input()
            replicate_output = cls.get_output()
            replicate_generated_output = cls.get_generated_output(replicate_output)

            cache.set_many({
                f'replicate_schema_{model_formated}': data.get("openapi_schema", {}).get("components", {}).get("schemas", {}),
                f'replicate_input_{model_formated}': replicate_input,
                f'replicate_output_{model_formated}': replicate_output,
                f'replicate_generated_output_{model_formated}': replicate_generated_output
            })

    # INPUT
    @classmethod
    def get_input(cls):
        has_prompt = cls.replicate_properties.get('prompt', None) is not None
        has_text = cls.replicate_properties.get('text', None) is not None
        has_image = cls.replicate_properties.get('image', None) is not None

        if (has_prompt or has_text) and has_image:
            return KIND_TEXT_AND_IMAGE
        elif has_prompt or has_text:
            return KIND_TEXT
        elif has_image:
            return KIND_IMAGE

    # OUTPUT
    @classmethod
    def get_output(cls):
        # Determine the output based on the 'type' or '$ref' in replicate_output
        output_type = cls.replicate_output.get('type', '')
        if output_type:
            return cls._get_output_by_type(output_type)
        return cls._get_output_by_ref()

    @classmethod
    def _get_output_by_type(cls, output_type):
        # Handle cases where output_type is defined
        if output_type == 'string':
            return cls._get_string_output()
        elif output_type == 'array':
            return cls._get_array_output()
        return ''

    @classmethod
    def _get_string_output(cls):
        # Return appropriate kind if the output is a string
        if cls.replicate_output.get('format', '') == 'uri':
            return KIND_FILE
        return KIND_TEXT

    @classmethod
    def _get_array_output(cls):
        # Return appropriate kind if the output is an array
        if cls.replicate_output.get('items', {}).get('format', '') == 'uri':
            return KIND_FILE_LIST
        return ''

    @classmethod
    def _get_output_by_ref(cls):
        # Handle cases where output_type is not defined, using '$ref'
        output_ref = cls.replicate_output.get('$ref', '')
        if output_ref:
            ref = output_ref.split('/')[-1]
            schema_ref_properties = cls.replicate_schema.get(ref, '').get('properties', {})
            return cls._get_output_by_properties(schema_ref_properties)
        return ''

    @classmethod
    def _get_output_by_properties(cls, properties):
        # Determine the kind of output based on properties of the referenced schema
        for key in properties.keys():
            if 'audio' in key:
                return KIND_AUDIO
            elif 'sound' in key:
                return KIND_SOUND
            elif 'music' in key:
                return KIND_MUSIC
        return ''

    # OUTPUT
    @classmethod
    def get_generated_output(cls, output):
        if output == KIND_TEXT:
            return KIND_TEXT
        elif output in [KIND_FILE, KIND_IMAGE, KIND_AUDIO, KIND_SOUND, KIND_MUSIC]:
            return KIND_FILE
        elif output in [KIND_FILE_LIST]:
            return KIND_FILE_LIST

    # PYDANTIC MODEL
    @classmethod
    def get_pydantic_model(cls, model, schema):
        model_formated = model.replace('/', '_').replace('-', '_')

        cls.replicate_schema = schema
        cls.replicate_properties = schema.get("Input", {}).get('properties', {})
        cls.replicate_field_required = schema.get("Input", {}).get("required", [])
        fields = {}

        cache.set(f'replicate_layout_{model_formated}', cls.create_layout())

        for field_name, field_info in cls.replicate_properties.items():
            fields[field_name] = cls.create_field(field_name, field_info)

        return create_model(f'dynamic_replicate_{model_formated}', __base__=UISchemaBaseModel, **fields)

    @classmethod
    def create_field(cls, field_name, field_info):
        field_label = field_info.get('title', field_name)
        field_type = field_info.get('type', None)
        field_default = field_info.get('default', None)

        field_instance = None
        field_instance_type = None

        if field_type:

            field = cls.TYPE_TO_FIELD[field_type]
            field_instance = field[0]
            field_instance_type = field[1]

            if field_type == 'integer':
                field_info['is_integer'] = True
            if field_type in ['integer', 'number'] and field_default:
                field_info['slider'] = True
            if field_type == 'boolean':
                field_info['toggle'] = True

        else:
            field_all_of = cls.TYPE_TO_FIELD.get('allOf', None)
            if field_all_of:
                field_instance = field_all_of[0]
                field_instance_type = field_all_of[1]
                options = cls.replicate_schema.get(field_label).get('enum', [])
                field_info['options'] = [(option, option) for option in options]
                # logger.info(field_info['options'])

        if field_instance:
            cls.clean_field_info(field_info)
            if field_label.lower() in cls.replicate_field_required:
                field_info['required'] = True
            else:
                field_instance_type = Optional[field_instance_type]
            return (field_instance_type, field_instance(label=field_label, **field_info)(None))
        else:
            raise ValueError(_('Error creating field'))

    @classmethod
    def create_layout(cls):
        sorted_data = dict(sorted(cls.replicate_properties.items(), key=lambda item: item[1]['x-order']))

        prompt = sorted_data.get('prompt', None)
        if prompt:
            del sorted_data['prompt']
        text = sorted_data.get('text', None)
        if text:
            del sorted_data['text']

        keys = list(sorted_data.keys())
        return [keys[i:i+4] for i in range(0, len(keys), 4)]

    @classmethod
    def clean_field_info(cls, field_info):
        for unwanted_property in cls.UNWANTED_PROPERTIES:
            unwanted_field = field_info.get(unwanted_property, None)
            if unwanted_field is not None:
                del field_info[unwanted_property]


class ExtractTransformContextModelGenerator:

    def generate_fields(self, schema: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        fields = {}
        for key, data in schema.items():
            if data['type'] == 'list':
                field_type = List[str]
            else:
                field_type = str

            if data.get('description', None):
                fields[key] = (Optional[field_type], Field(..., description=data['description']))
            else:
                fields[key] = (Optional[field_type], ...)

        return fields

    def generate_model(self, pipeline_alias: str, schema: Dict[str, Dict[str, str]]):
        fields = self.generate_fields(schema)
        return create_model(f'extracttransform_context_model_{pipeline_alias}', **fields)
